.PHONY: help install dev build up down logs clean test lint format migrate migrate-create shell db-shell redis-cli

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (requires uv: https://github.com/astral-sh/uv)
	uv pip install -r requirements.txt

dev: ## Start development environment (hot-reload)
	docker compose -f docker/docker-compose.dev.yml up --build

build: ## Build production Docker image (requires config.ini)
	cd docker && ./sync_compose_from_config.sh && docker compose build

up: ## Start production environment (requires config.ini)
	./start.sh -d

down: ## Stop all containers
	cd docker && docker compose down 2>/dev/null || true
	docker compose -f docker/docker-compose.dev.yml down 2>/dev/null || true

logs: ## Show production logs (follow)
	cd docker && docker compose logs -f

clean: ## Remove containers, volumes, and images
	cd docker && docker compose down -v --rmi all 2>/dev/null || true
	docker compose -f docker/docker-compose.dev.yml down -v --rmi all 2>/dev/null || true

test: ## Run pytest test suite
	pytest tests/ -v

lint: ## Run ruff linter
	ruff check .

format: ## Auto-fix lint issues and format code
	ruff check --fix .
	ruff format .

migrate: ## Apply database migrations
	alembic upgrade head

migrate-create: ## Create new migration (autogenerate)
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

shell: ## Open Python shell with app context
	python -c "from src.main import app; import IPython; IPython.embed()" 2>/dev/null \
		|| python -c "from src.main import app; import code; code.interact(local={'app': app})"

db-shell: ## Open PostgreSQL CLI inside dev stack
	docker compose -f docker/docker-compose.dev.yml exec -it postgres psql -U postgres -d oxyroute_db

redis-cli: ## Open Redis CLI inside dev stack
	docker compose -f docker/docker-compose.dev.yml exec -it redis redis-cli
