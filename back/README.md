# BookBoxd API

API REST para gerenciamento de clubes de leitura com autenticação Google OAuth.

## Stack

- **Python 3.12** + **FastAPI**
- **PostgreSQL 15** + **SQLAlchemy 2** + **Alembic**
- **Docker** + **Docker Compose**
- Auth: Google OAuth → JWT próprio

## Rodando em desenvolvimento

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com seus valores (GOOGLE_CLIENT_ID, JWT_SECRET, etc.)

# 2. Subir containers
docker compose up --build

# 3. Aplicar migrations (em outro terminal)
docker compose exec backend alembic upgrade head
```

A API estará disponível em `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`

## Rodando em produção

```bash
cp .env.example .env
# Configurar todas as variáveis obrigatórias no .env

docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Variáveis de ambiente obrigatórias

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL de conexão PostgreSQL |
| `POSTGRES_USER` | Usuário do banco |
| `POSTGRES_PASSWORD` | Senha do banco |
| `POSTGRES_DB` | Nome do banco |
| `JWT_SECRET` | Segredo para assinar JWTs (use valor forte em prod) |
| `GOOGLE_CLIENT_ID` | Client ID do Google OAuth |

## Rodando testes

```bash
pip install -r requirements.txt
pytest --cov=app tests/
```

## Endpoints principais

### Auth
- `POST /auth/google` — Login via Google (recebe `id_token`, retorna JWT)

### Usuários
- `GET /users/me` — Perfil do usuário autenticado
- `DELETE /users/me` — Deleta própria conta
- `DELETE /users/{id}` — Deleta qualquer usuário (MASTER)

### Livros (catálogo global)
- `POST /books` — Cria livro
- `GET /books` — Lista livros (filtros: `title`, `author`)
- `GET /books/{id}` — Detalhe do livro

### Clubes
- `POST /clubs` — Cria clube
- `GET /clubs` — Lista todos os clubes
- `GET /clubs/{id}` — Detalhe do clube
- `PATCH /clubs/{id}` — Atualiza clube (owner/MASTER)
- `DELETE /clubs/{id}` — Deleta clube (owner/MASTER)

### Membership
- `POST /clubs/{id}/join` — Solicitar entrada
- `POST /clubs/{id}/leave` — Sair do clube
- `POST /clubs/{id}/members/{uid}/approve` — Aprovar (owner/MASTER)
- `POST /clubs/{id}/members/{uid}/reject` — Rejeitar (owner/MASTER)
- `POST /clubs/{id}/members/{uid}/ban` — Banir permanentemente (owner/MASTER)
- `POST /clubs/{id}/members/{uid}/kick` — Expulsar temporariamente (owner/MASTER)
- `GET /clubs/{id}/members` — Listar membros

### Livros do clube
- `POST /clubs/{id}/books` — Adicionar livro ao clube (owner/MASTER)
- `GET /clubs/{id}/books` — Listar livros do clube
- `DELETE /clubs/{id}/books/{book_id}` — Remover livro (owner/MASTER)

### Biblioteca pessoal
- `POST /me/books` — Adicionar à biblioteca
- `GET /me/books` — Listar biblioteca (filtro: `status`)
- `PATCH /me/books/{book_id}` — Atualizar status de leitura
- `DELETE /me/books/{book_id}` — Remover da biblioteca

### Livros do mês & registro de leitura
Um clube pode ter vários livros do mês ativos ao mesmo tempo, cada um com seu
próprio ciclo de 30 dias.

- `POST /clubs/{id}/monthly-books` — Adiciona um livro do mês; inicia um ciclo de 30 dias e cria um registro de leitura para cada membro ativo (owner/MASTER)
- `GET /clubs/{id}/monthly-books` — Lista os livros do mês do clube
- `GET /clubs/{id}/monthly-books/{mb_id}` — Detalhe de um livro do mês
- `DELETE /clubs/{id}/monthly-books/{mb_id}` — Encerra um livro do mês (owner/MASTER)
- `GET /clubs/{id}/monthly-books/{mb_id}/register` — Registro de leitura pessoal do usuário
- `PATCH /clubs/{id}/monthly-books/{mb_id}/register` — Atualiza o registro: `unit` (PAGE/CHAPTER), `goal_frequency` (DAILY/WEEKLY), `total_amount`, `current_position`
- `GET /clubs/{id}/monthly-books/{mb_id}/registers` — Placar de progresso de todos os membros

A meta é dinâmica (modo *catch-up*): `meta = quanto falta ÷ tempo restante`, recalculada
a cada atualização — sobe se o membro ficar para trás e zera ao concluir. O membro escolhe
acompanhar por página ou capítulo e ver a meta por dia ou por semana.

## Status de Membership

`PENDING → ACTIVE | REJECTED`
`ACTIVE → LEFT | BANNED | KICKED`
`LEFT | REJECTED → PENDING` (novo ciclo)
`KICKED → PENDING` (após kicked_until expirar)
`BANNED` → estado terminal, sem saída
