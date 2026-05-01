# BookBoxd

Plataforma de clubes de leitura com autenticação Google OAuth.

## 🚀 Executando

### Backend

```bash
# Executar backend + banco
docker-compose up --build

# Ou apenas backend
cd backend && make up-build
```

**URLs:**
- API: `http://localhost:8000`
- Documentação: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health/`

### Frontend

```bash
cd front
npm install
npm start
```

**URL:** `http://localhost:3000`

## 📚 Documentação

- [Backend API Documentation](./backend/API_DOCUMENTATION.md)
- [Backend API Examples](./backend/API_EXAMPLES.md)
- [Backend README](./backend/README.md)

## 🏗️ Arquitetura

```
bookboxd/
├── backend/          # FastAPI + PostgreSQL
├── front/           # React + JavaScript
└── docker-compose.yml
```

## 🔧 Stack Tecnológica

### Backend
- **FastAPI**: API web assíncrona
- **PostgreSQL**: Banco de dados
- **SQLAlchemy**: ORM
- **JWT**: Autenticação
- **Google OAuth**: Login social

### Frontend
- **React**: Interface do usuário
- **JavaScript**: Lógica client-side

## 📋 Funcionalidades

- ✅ Autenticação Google OAuth
- ✅ Criação e gerenciamento de livros
- ✅ Sistema de clubes de leitura
- ✅ Gerenciamento de membresias
- ✅ Transferência de propriedade
- ✅ Expulsão temporária de membros

## 🔄 Fluxos Principais

1. **Usuário faz login** via Google OAuth
2. **Cria livros** no sistema
3. **Cria clube** de leitura
4. **Outros usuários solicitam** participação
5. **Dono aprova/rejeita** solicitações
6. **Gerencia membros** (expulsar, etc.)