.PHONY: help install format lint test clean docker-build docker-run setup-pre-commit

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости через Poetry
	poetry install

format: ## Форматировать код (Black, isort, Ruff)
	poetry run black src tests scripts main.py
	poetry run isort src tests scripts main.py
	poetry run ruff format src tests scripts main.py

lint: ## Запустить линтеры (Ruff, MyPy, Bandit)
	poetry run ruff check src tests scripts main.py
	poetry run mypy src
	poetry run bandit -r src scripts

test: ## Запустить тесты
	poetry run pytest

test-cov: ## Запустить тесты с покрытием
	poetry run pytest --cov=src --cov-report=html --cov-report=term-missing

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build

docker-build: ## Собрать Docker образ
	docker build -t engineering-practices-ml .

docker-run: ## Запустить Docker контейнер
	docker run -it engineering-practices-ml

setup-pre-commit: ## Настроить pre-commit hooks
	poetry run pre-commit install

pre-commit-all: ## Запустить pre-commit на всех файлах
	poetry run pre-commit run --all-files

docs-build: ## Собрать документацию
	poetry run mkdocs build

docs-serve: ## Запустить локальный сервер документации
	poetry run mkdocs serve

docs-deploy: ## Опубликовать документацию на GitHub Pages
	poetry run mkdocs gh-deploy

report-generate: ## Сгенерировать отчет об экспериментах
	poetry run python scripts/reports/generate_experiment_report.py
