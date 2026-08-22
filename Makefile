.PHONY: format migrate-create migrate-up migrate-down run install

format:
	@echo "formating..." ; \
	ruff format .; \
	docker-compose -f docker/docker-compose.yml --project-directory docker run --rm prettier


migrate-create:
	@read -p "Enter migration name: " name; \
	if [ -n "$$name" ]; then \
		echo "Create migration '$$name'"; \
		uv run alembic revision --autogenerate -m "$$name"; \
	else \
		echo "Name cannot be empty"; \
	fi

migrate-up:
	@uv run alembic upgrade head

migrate-down:
	@uv run alembic downgrade -1

run:
	HOST=0.0.0.0 PORT=9000 python run.py

install:
	uv pip install -r pyproject.toml
