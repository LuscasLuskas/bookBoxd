.PHONY: help build up down restart logs clean test migrate create-migration

# Default target
help: ## Show this help message
	@echo "BookBoxd Backend - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Docker commands
build: ## Build the Docker containers
	docker-compose build

up: ## Start the services
	docker-compose up -d

up-build: ## Build and start the services
	docker-compose up --build -d

down: ## Stop the services
	docker-compose down

restart: ## Restart the services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show logs from backend service
	docker-compose logs -f backend

# Database commands
migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

create-migration: ## Create a new migration (usage: make create-migration MESSAGE="migration description")
	docker-compose exec backend alembic revision --autogenerate -m "$(MESSAGE)"

# Cleanup
clean: ## Remove containers, volumes, and images
	docker-compose down -v --rmi all

# Development
shell: ## Open a shell in the backend container
	docker-compose exec backend bash

test: ## Run tests (if implemented)
	docker-compose exec backend python -m pytest

# Health check
health: ## Check if the API is healthy
	curl -s http://localhost:8000/health/ | jq . || echo "API not responding"

# Full reset
reset: down clean build up migrate ## Full reset: down, clean, build, up, migrate