.PHONY: help info env-file check-env check-runtime format migrate-create migrate-up migrate-down up down logs install create-superadmin

.DEFAULT_GOAL := help

export HOST_UID := $(shell id -u)
export HOST_GID := $(shell id -g)

# "docker compose" (plugin, Linux/WSL) or standalone "docker-compose"
COMPOSE_BIN := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo docker-compose)
COMPOSE = $(COMPOSE_BIN) -f docker/docker-compose.yml --project-directory docker
APP = $(COMPOSE) run --rm app
RUNTIME = docker/runtime
ENV_FILE = app/.env
CHECK_ENV = sh docker/check-env.sh $(ENV_FILE) app/default.env

help: ## Показать это меню
	@echo "Использование: make <команда>"
	@echo
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Creates app/.env from app/default.env when it is missing
env-file:
	@$(CHECK_ENV) --create-only

# env-file + LOG_DIR default + required variables (POSTGRES_*, SECRET_KEY)
check-env:
	@$(CHECK_ENV)

# Creates runtime dirs and fails fast if Postgres data was removed
# while the container is still running. The data dir is checked from inside
# the container: on Linux/WSL it belongs to the postgres user (uid 999,
# mode 700) and the host user cannot look into it.
check-runtime: check-env
	@if [ -n "$$($(COMPOSE) ps -q --status running postgres 2>/dev/null)" ] && \
		! $(COMPOSE) exec -T postgres test -f /var/lib/postgresql/data/PG_VERSION; then \
		echo "ERROR: $(RUNTIME)/postgres удалён, а postgres ещё запущен."; \
		echo "       Перезапусти контейнеры: make down && make up"; \
		exit 1; \
	fi
	@mkdir -p $(RUNTIME)/logs/webapp $(RUNTIME)/cache/npm

format: check-runtime ## Отформатировать код (ruff + prettier)
	@echo "formating..." ; \
	$(APP) ruff format .; \
	$(COMPOSE) run --rm prettier


migrate-create: check-runtime ## Создать миграцию (autogenerate) и отформатировать ruff
	@read -p "Enter migration name: " name; \
	if [ -n "$$name" ]; then \
		echo "Create migration '$$name'"; \
		$(APP) alembic revision --autogenerate -m "$$name" && \
		$(APP) ruff format migrations/versions; \
	else \
		echo "Name cannot be empty"; \
	fi

migrate-up: check-runtime ## Применить все миграции
	@$(APP) alembic upgrade head

migrate-down: check-runtime ## Откатить последнюю миграцию
	@$(APP) alembic downgrade -1

up: check-runtime ## Собрать образ и запустить все контейнеры
	$(COMPOSE) up -d --build
	@$(MAKE) --no-print-directory info

# host port published for <service> <container_port>
port = $$($(COMPOSE) port $(1) $(2) 2>/dev/null | sed 's/.*://')

info: env-file ## Показать адреса запущенных сервисов
	@echo
	@echo "Сервисы запущены:"
	@echo "  App:           http://localhost:$(call port,app,9000)"
	@echo "  Mailpit (UI):  http://localhost:$(call port,mailpit,8025)"
	@echo "  Mailpit SMTP:  localhost:$(call port,mailpit,1025)"
	@echo "  Jodit finder:  http://localhost:$(call port,jodit-finder,9023)"
	@echo "  Postgres:      localhost:$(call port,postgres,5432)"
	@echo "  Логи:          $(RUNTIME)/logs/webapp"
	@echo

down: env-file ## Остановить и удалить контейнеры
	$(COMPOSE) down

logs: env-file ## Логи приложения в реальном времени
	$(COMPOSE) logs -f app

create-superadmin: check-runtime ## Создать или обновить суперадмина
	@$(APP) python cli.py create-superadmin

install: check-runtime ## Установить зависимости (docker-образ, npm, .venv для IDE)
	$(COMPOSE) build app
	$(COMPOSE) run --rm node install
	@if command -v uv >/dev/null 2>&1; then \
		uv sync; \
	else \
		echo "uv не найден: .venv для подсветки в IDE не создан (необязательно)."; \
		echo "Установка uv: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	fi
