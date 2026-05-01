.PHONY: format migrate-create migrate-up run install

format:
	@echo "formating..." ; \
	ruff format .;


migrate-create:
	@read -p "Enter migration name: " name; \
	if [ -n "$$name" ]; then \
		echo "Create migration '$$name'"; \
		alembic revision --autogenerate -m "$$name"; \
	else \
		echo "Name cannot be empty"; \
	fi

migrate-up:
	@alembic upgrade head


run:
	HOST=0.0.0.0 PORT=9000 python run.py

install:
	uv pip install -r pyproject.toml
