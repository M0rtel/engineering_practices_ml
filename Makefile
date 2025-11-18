.PHONY: help install format lint test clean docker-build docker-run setup-pre-commit

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости через UV
	uv sync

format: ## Форматировать код (Black, isort, Ruff)
	uv run black src tests scripts main.py
	uv run isort src tests scripts main.py
	uv run ruff format src tests scripts main.py

lint: ## Запустить линтеры (Ruff, MyPy, Bandit)
	uv run ruff check src tests scripts main.py
	uv run mypy src
	uv run bandit -r src scripts

test: ## Запустить тесты
	uv run pytest

test-cov: ## Запустить тесты с покрытием
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

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
	uv run pre-commit install

pre-commit-all: ## Запустить pre-commit на всех файлах
	uv run pre-commit run --all-files

docs-build: ## Собрать документацию
	uv run mkdocs build

docs-serve: ## Запустить локальный сервер документации
	uv run mkdocs serve

docs-deploy: ## Опубликовать документацию на GitHub Pages
	uv run mkdocs gh-deploy

report-generate: ## Сгенерировать отчет об экспериментах
	uv run python scripts/reports/generate_experiment_report.py
