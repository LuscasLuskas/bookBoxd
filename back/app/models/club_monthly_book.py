import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClubMonthlyBook(Base):
    """O livro do mês de um clube. Apenas um fica ativo por clube de cada vez.

    Ao ser criado, inicia um ciclo de leitura (ver CYCLE_DAYS no service) e gera
    um ReadingRegister para cada membro ativo do clube.
    """

    __tablename__ = "club_monthly_books"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    club_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("book_clubs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    set_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    book: Mapped["Book"] = relationship(  # type: ignore[name-defined]
        "Book", foreign_keys=[book_id]
    )
    club: Mapped["BookClub"] = relationship(  # type: ignore[name-defined]
        "BookClub", foreign_keys=[club_id]
    )
    setter: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[set_by]
    )
    registers: Mapped[list["ReadingRegister"]] = relationship(  # type: ignore[name-defined]
        "ReadingRegister", back_populates="monthly_book", cascade="all, delete-orphan"
    )
