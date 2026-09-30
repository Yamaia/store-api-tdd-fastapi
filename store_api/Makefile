.PHONY: install run test cov mongo

install:
	poetry install

mongo:
	docker compose up -d mongo

run:
	poetry run uvicorn store.main:app --reload

test:
	poetry run pytest -v

cov:
	poetry run pytest --cov=store --cov-report=term-missing
