import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReadingUnit(str, enum.Enum):
    """Unidade pela qual o membro acompanha o progresso de leitura."""

    PAGE = "PAGE"
    CHAPTER = "CHAPTER"


class GoalFrequency(str, enum.Enum):
    """Frequência pela qual a meta de leitura é apresentada."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class ReadingRegister(Base):
    """Registro de leitura pessoal de um membro para o livro do mês do clube.

    Acompanha a posição atual (cumulativa). A meta é derivada dinamicamente do
    quanto falta dividido pelo tempo restante (ver MonthlyBookService).
    """

    __tablename__ = "reading_registers"
    __table_args__ = (
        UniqueConstraint(
            "monthly_book_id", "user_id", name="uq_reading_register_book_user"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    monthly_book_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("club_monthly_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit: Mapped[ReadingUnit] = mapped_column(
        Enum(ReadingUnit), nullable=False, default=ReadingUnit.PAGE
    )
    goal_frequency: Mapped[GoalFrequency] = mapped_column(
        Enum(GoalFrequency), nullable=False, default=GoalFrequency.DAILY
    )
    # Total de páginas/capítulos da edição do membro. Nulo até ele configurar.
    total_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Posição atual cumulativa (página/capítulo já alcançado).
    current_position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    monthly_book: Mapped["ClubMonthlyBook"] = relationship(  # type: ignore[name-defined]
        "ClubMonthlyBook", back_populates="registers"
    )
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[user_id]
    )
