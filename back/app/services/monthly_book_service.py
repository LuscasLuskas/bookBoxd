import math
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book_club import BookClub
from app.models.club_monthly_book import ClubMonthlyBook
from app.models.membership import MembershipStatus
from app.models.reading_register import GoalFrequency, ReadingRegister
from app.models.user import Role, User
from app.repositories.book_club_repository import BookClubRepository
from app.repositories.book_repository import BookRepository
from app.repositories.club_monthly_book_repository import ClubMonthlyBookRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.reading_register_repository import ReadingRegisterRepository
from app.services.forum_service import ForumService
from app.schemas.reading_register import (
    MonthlyBookListResponse,
    MonthlyBookResponse,
    RegisterListResponse,
    RegisterResponse,
    RegisterUpdate,
)

# Duração do ciclo de leitura de cada livro do mês.
CYCLE_DAYS = 30


class MonthlyBookService:
    """Livros do mês de um clube e os registros de leitura pessoais.

    Um clube pode ter vários livros do mês ativos ao mesmo tempo; cada um inicia
    seu próprio ciclo de CYCLE_DAYS dias e tem registros independentes.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = ClubMonthlyBookRepository(db)
        self.register_repo = ReadingRegisterRepository(db)
        self.club_repo = BookClubRepository(db)
        self.book_repo = BookRepository(db)
        self.membership_repo = MembershipRepository(db)

    # ------------------------------------------------------------------
    # Livros do mês (owner / MASTER)
    # ------------------------------------------------------------------

    def set_monthly_book(
        self, club_id: str, book_id: str, current_user: User
    ) -> MonthlyBookResponse:
        """Adiciona um livro do mês e cria um registro para cada membro ativo."""
        club = self._get_club_or_404(club_id)
        self._assert_owner_or_master(club, current_user)

        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado"
            )

        if self.repo.get_active_by_club_and_book(club_id, book_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este livro já é um livro do mês ativo deste clube",
            )

        now = datetime.now(timezone.utc)
        monthly_book = self.repo.create(
            ClubMonthlyBook(
                id=str(uuid.uuid4()),
                club_id=club_id,
                book_id=book_id,
                set_by=current_user.id,
                start_date=now,
                end_date=now + timedelta(days=CYCLE_DAYS),
                is_active=True,
            )
        )

        # Gera um registro de leitura para cada membro ativo do clube.
        active_members = self.membership_repo.list_by_club(
            club_id, status=MembershipStatus.ACTIVE
        )
        registers = [
            ReadingRegister(
                id=str(uuid.uuid4()),
                monthly_book_id=monthly_book.id,
                user_id=m.user_id,
            )
            for m in active_members
        ]
        if registers:
            self.register_repo.add_all(registers)

        # Auto-open (or repin) a forum thread for this monthly book.
        ForumService(self.db).on_monthly_book_set(
            club_id=club_id,
            book_id=book_id,
            book_title=book.title,
            actor=current_user,
        )

        return self._monthly_book_response(monthly_book, len(registers))

    def list_monthly_books(
        self, club_id: str, current_user: User
    ) -> MonthlyBookListResponse:
        club = self._get_club_or_404(club_id)
        self._assert_member_or_manager(club, current_user)
        books = self.repo.list_by_club(club_id)
        items = [
            self._monthly_book_response(
                mb, len(self.register_repo.list_by_monthly_book(mb.id))
            )
            for mb in books
        ]
        return MonthlyBookListResponse(items=items, total=len(items))

    def get_monthly_book(
        self, club_id: str, monthly_book_id: str, current_user: User
    ) -> MonthlyBookResponse:
        club = self._get_club_or_404(club_id)
        self._assert_member_or_manager(club, current_user)
        monthly_book = self._get_monthly_book_or_404(club_id, monthly_book_id)
        registers = self.register_repo.list_by_monthly_book(monthly_book.id)
        return self._monthly_book_response(monthly_book, len(registers))

    def clear_monthly_book(
        self, club_id: str, monthly_book_id: str, current_user: User
    ) -> None:
        club = self._get_club_or_404(club_id)
        self._assert_owner_or_master(club, current_user)
        monthly_book = self._get_monthly_book_or_404(club_id, monthly_book_id)
        if not monthly_book.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este livro do mês já foi encerrado",
            )
        monthly_book.is_active = False
        self.repo.save(monthly_book)
        ForumService(self.db).on_monthly_book_cleared(
            club_id=club_id, book_id=monthly_book.book_id
        )

    def list_registers(
        self, club_id: str, monthly_book_id: str, current_user: User
    ) -> RegisterListResponse:
        """Placar: progresso de todos os membros em um livro do mês."""
        club = self._get_club_or_404(club_id)
        self._assert_member_or_manager(club, current_user)
        monthly_book = self._get_monthly_book_or_404(club_id, monthly_book_id)
        registers = self.register_repo.list_by_monthly_book(monthly_book.id)
        items = [self._register_response(r, monthly_book) for r in registers]
        items.sort(key=lambda r: r.progress_percent, reverse=True)
        return RegisterListResponse(
            monthly_book=self._monthly_book_response(monthly_book, len(registers)),
            items=items,
            total=len(items),
        )

    # ------------------------------------------------------------------
    # Registro de leitura pessoal (membro)
    # ------------------------------------------------------------------

    def get_my_register(
        self, club_id: str, monthly_book_id: str, current_user: User
    ) -> RegisterResponse:
        self._get_club_or_404(club_id)
        monthly_book = self._get_monthly_book_or_404(club_id, monthly_book_id)
        self._assert_active_member(club_id, current_user)
        register = self._get_or_create_register(monthly_book, current_user)
        return self._register_response(register, monthly_book)

    def update_my_register(
        self,
        club_id: str,
        monthly_book_id: str,
        body: RegisterUpdate,
        current_user: User,
    ) -> RegisterResponse:
        self._get_club_or_404(club_id)
        monthly_book = self._get_monthly_book_or_404(club_id, monthly_book_id)
        self._assert_active_member(club_id, current_user)
        register = self._get_or_create_register(monthly_book, current_user)

        if body.unit is not None:
            register.unit = body.unit
        if body.goal_frequency is not None:
            register.goal_frequency = body.goal_frequency
        if body.total_amount is not None:
            register.total_amount = body.total_amount
        if body.current_position is not None:
            register.current_position = body.current_position

        if (
            register.total_amount is not None
            and register.current_position > register.total_amount
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A posição atual não pode ultrapassar o total de páginas/capítulos",
            )

        register = self.register_repo.save(register)
        return self._register_response(register, monthly_book)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_or_create_register(
        self, monthly_book: ClubMonthlyBook, user: User
    ) -> ReadingRegister:
        """Devolve o registro do membro, criando-o se ele entrou após o set."""
        register = self.register_repo.get_by_book_and_user(monthly_book.id, user.id)
        if register:
            return register
        return self.register_repo.create(
            ReadingRegister(
                id=str(uuid.uuid4()),
                monthly_book_id=monthly_book.id,
                user_id=user.id,
            )
        )

    def _cycle_progress(self, monthly_book: ClubMonthlyBook) -> tuple[int, int]:
        """Devolve (dias decorridos, dias restantes), ambos limitados ao ciclo."""
        now = datetime.now(timezone.utc)
        start = monthly_book.start_date
        if start.tzinfo is None:
            # Bancos sem suporte a timezone (ex.: SQLite) devolvem naive.
            start = start.replace(tzinfo=timezone.utc)
        elapsed = (now - start).days
        elapsed = max(0, min(elapsed, CYCLE_DAYS))
        return elapsed, CYCLE_DAYS - elapsed

    def _monthly_book_response(
        self, monthly_book: ClubMonthlyBook, member_count: int
    ) -> MonthlyBookResponse:
        elapsed, remaining = self._cycle_progress(monthly_book)
        return MonthlyBookResponse(
            id=monthly_book.id,
            club_id=monthly_book.club_id,
            book_id=monthly_book.book_id,
            book_title=monthly_book.book.title,
            book_author=monthly_book.book.author,
            set_by=monthly_book.set_by,
            start_date=monthly_book.start_date,
            end_date=monthly_book.end_date,
            is_active=monthly_book.is_active,
            cycle_days=CYCLE_DAYS,
            days_elapsed=elapsed,
            days_remaining=remaining,
            member_count=member_count,
        )

    def _register_response(
        self, register: ReadingRegister, monthly_book: ClubMonthlyBook
    ) -> RegisterResponse:
        elapsed, remaining = self._cycle_progress(monthly_book)
        weeks_remaining = round(remaining / 7, 2)

        total = register.total_amount
        current = register.current_position
        is_configured = total is not None

        amount_remaining: int | None = None
        daily_goal: int | None = None
        weekly_goal: int | None = None
        current_goal: int | None = None
        expected_position: int | None = None
        on_pace: bool | None = None
        progress_percent = 0.0
        is_completed = False

        if is_configured:
            amount_remaining = max(0, total - current)
            is_completed = current >= total
            progress_percent = round(min(current / total, 1.0) * 100, 1)
            expected_position = round(total * elapsed / CYCLE_DAYS)
            on_pace = current >= expected_position

            # Meta dinâmica de recuperação: o que falta dividido pelo tempo
            # restante. Sobe se o membro ficar para trás; zera ao concluir.
            days_divisor = max(1, remaining)
            weeks_divisor = max(1.0, remaining / 7)
            daily_goal = math.ceil(amount_remaining / days_divisor)
            weekly_goal = math.ceil(amount_remaining / weeks_divisor)
            current_goal = (
                daily_goal
                if register.goal_frequency == GoalFrequency.DAILY
                else weekly_goal
            )

        return RegisterResponse(
            id=register.id,
            monthly_book_id=register.monthly_book_id,
            user_id=register.user_id,
            user_name=register.user.name,
            unit=register.unit,
            goal_frequency=register.goal_frequency,
            total_amount=total,
            current_position=current,
            is_configured=is_configured,
            amount_remaining=amount_remaining,
            days_remaining=remaining,
            weeks_remaining=weeks_remaining,
            daily_goal=daily_goal,
            weekly_goal=weekly_goal,
            current_goal=current_goal,
            progress_percent=progress_percent,
            expected_position=expected_position,
            on_pace=on_pace,
            is_completed=is_completed,
            updated_at=register.updated_at,
        )

    def _get_club_or_404(self, club_id: str) -> BookClub:
        club = self.club_repo.get_by_id(club_id)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado"
            )
        return club

    def _get_monthly_book_or_404(
        self, club_id: str, monthly_book_id: str
    ) -> ClubMonthlyBook:
        monthly_book = self.repo.get_by_id(monthly_book_id)
        if not monthly_book or monthly_book.club_id != club_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro do mês não encontrado",
            )
        return monthly_book

    def _assert_owner_or_master(self, club: BookClub, user: User) -> None:
        if club.owner_id != user.id and user.role != Role.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o dono ou MASTER pode gerenciar os livros do mês",
            )

    def _assert_active_member(self, club_id: str, user: User) -> None:
        membership = self.membership_repo.get_by_user_and_club(user.id, club_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você precisa ser um membro ativo do clube",
            )

    def _assert_member_or_manager(self, club: BookClub, user: User) -> None:
        if club.owner_id == user.id or user.role == Role.MASTER:
            return
        membership = self.membership_repo.get_by_user_and_club(user.id, club.id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas membros do clube podem ver os livros do mês",
            )
