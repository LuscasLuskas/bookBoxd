from datetime import datetime

from pydantic import BaseModel, Field

from app.models.reading_register import GoalFrequency, ReadingUnit


# ---- Livro do mês (admin) ----


class MonthlyBookSet(BaseModel):
    """Corpo da requisição para definir um livro do mês de um clube."""

    book_id: str


class MonthlyBookResponse(BaseModel):
    id: str
    club_id: str
    book_id: str
    book_title: str
    book_author: str
    set_by: str | None
    start_date: datetime
    end_date: datetime
    is_active: bool
    cycle_days: int
    days_elapsed: int
    days_remaining: int
    member_count: int


class MonthlyBookListResponse(BaseModel):
    """Lista dos livros do mês de um clube (vários podem estar ativos)."""

    items: list[MonthlyBookResponse]
    total: int


# ---- Registro de leitura pessoal (membro) ----


class RegisterUpdate(BaseModel):
    """Atualização parcial do registro de leitura. Todos os campos opcionais."""

    unit: ReadingUnit | None = None
    goal_frequency: GoalFrequency | None = None
    total_amount: int | None = Field(None, ge=1)
    current_position: int | None = Field(None, ge=0)


class RegisterResponse(BaseModel):
    id: str
    monthly_book_id: str
    user_id: str
    user_name: str
    unit: ReadingUnit
    goal_frequency: GoalFrequency
    total_amount: int | None
    current_position: int
    # True quando o membro já informou o total (registro utilizável).
    is_configured: bool
    amount_remaining: int | None
    days_remaining: int
    weeks_remaining: float
    # Metas com recálculo dinâmico (quanto falta / tempo restante).
    daily_goal: int | None
    weekly_goal: int | None
    # Meta vigente conforme a frequência escolhida pelo membro.
    current_goal: int | None
    progress_percent: float
    # Onde o membro deveria estar para o ritmo ideal do ciclo.
    expected_position: int | None
    on_pace: bool | None
    is_completed: bool
    updated_at: datetime


class RegisterListResponse(BaseModel):
    """Placar de progresso de todos os membros para um livro do mês."""

    monthly_book: MonthlyBookResponse
    items: list[RegisterResponse]
    total: int
