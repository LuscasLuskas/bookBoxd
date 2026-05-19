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

## Status de Membership

`PENDING → ACTIVE | REJECTED`
`ACTIVE → LEFT | BANNED | KICKED`
`LEFT | REJECTED → PENDING` (novo ciclo)
`KICKED → PENDING` (após kicked_until expirar)
`BANNED` → estado terminal, sem saída
