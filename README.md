# Engineering Practices ML Project

## Описание проекта

### Цель
Создать полноценный ML проект с использованием современных инженерных практик.
Фокус на инженерных аспектах, а не на сложности ML задач.

### Проект
Система классификации/регрессии на простых датасетах с полным MLOps workflow.


## Структура проекта

```
engineering_practices_ml/
├── data/              # Данные проекта
│   ├── raw/          # Исходные данные
│   ├── processed/    # Обработанные данные
│   ├── external/     # Внешние данные
│   └── interim/      # Промежуточные данные
├── src/              # Исходный код
│   ├── data_science_project/
│   ├── models/       # Модели машинного обучения
│   ├── features/     # Инженерия признаков
│   └── visualization/ # Визуализация
├── tests/            # Тесты
│   ├── unit/         # Юнит-тесты
│   └── integration/  # Интеграционные тесты
├── notebooks/        # Jupyter notebooks
├── docs/             # Документация
├── scripts/          # Вспомогательные скрипты
│   ├── setup/        # Скрипты настройки
│   ├── data/         # Скрипты для работы с данными
│   ├── models/       # Скрипты для моделей
│   ├── experiments/  # Скрипты для экспериментов
│   ├── pipeline/     # Скрипты для пайплайнов
│   └── clearml/      # Скрипты для ClearML
├── config/           # Конфигурационные файлы
├── params.yaml       # Параметры DVC pipeline
├── dvc.yaml          # Конфигурация DVC pipeline
├── reports/          # Отчеты и результаты
│   ├── figures/      # Графики и визуализации
│   └── models/       # Сохраненные модели
├── pyproject.toml    # Конфигурация проекта (UV)
├── uv.lock          # Lock-файл зависимостей (UV)
├── Dockerfile        # Docker конфигурация
└── README.md         # Этот файл
```

## Требования

- Python 3.10+
- UV (для управления зависимостями) - быстрый менеджер пакетов на Rust
- Docker (опционально, для контейнеризации)

## Быстрый старт

Для пошаговой настройки проекта см. **`docs/QUICKSTART.md`** - полное руководство по установке и настройке всех компонентов.

**Краткая инструкция:**
1. Клонировать репозиторий: `git clone <repository-url> && cd engineering_practices_ml`
2. Установить UV (если не установлен): `curl -LsSf https://astral.sh/uv/install.sh | sh` или `pip install uv`
3. Установить зависимости: `uv sync`
4. Настроить pre-commit: `uv run pre-commit install`

## Использование

### Запуск проекта

```bash
python main.py
```

### Запуск ML пайплайна

```bash
# Запуск всего пайплайна
uv run dvc repro

# Запуск конкретной стадии
uv run dvc repro prepare_data
uv run dvc repro train_model

# Запуск с изменением параметров
uv run python scripts/pipeline/run_with_params.py train_model -S model_type=ridge

# Запуск с мониторингом
uv run python scripts/pipeline/run_pipeline.py --config config/train_params.yaml --monitor
```

### Запуск экспериментов с ClearML

```bash
# Обучение модели с трекингом в ClearML
uv run python scripts/clearml/train_with_clearml.py \
  --config config/train_params.yaml \
  --model-type ridge \
  --experiment-name ridge_experiment_001

# Сравнение экспериментов
uv run python scripts/clearml/compare_experiments.py --list

# Управление моделями
uv run python scripts/clearml/manage_models.py --list
```

Подробнее см. `docs/QUICKSTART.md` и `docs/homework_5/README.md`

### Форматирование кода

```bash
# Black
uv run black src tests

# isort
uv run isort src tests

# Ruff
uv run ruff check src tests
uv run ruff format src tests
```

### Линтинг

```bash
# MyPy
uv run mypy src

# Bandit (проверка безопасности)
uv run bandit -r src
```

### Тестирование

```bash
# Запуск всех тестов
uv run pytest

# С покрытием кода
uv run pytest --cov=src --cov-report=html
```

## Docker

### Сборка образа

```bash
docker build -t engineering-practices-ml .
```

### Запуск контейнера

```bash
docker run -it engineering-practices-ml
```

### Запуск с MinIO и ClearML

```bash
# Запуск всех сервисов (MinIO, ClearML Server, проект)
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка
docker compose down
```

**MinIO:**
- **API:** http://localhost:9000
- **Console:** http://localhost:9001
- **Credentials:** minioadmin / minioadmin

**ClearML:**
- **Web UI:** http://localhost:8080
- **API:** http://localhost:8008
- **File Server:** http://localhost:8081
- **Сервисы:** MongoDB, Elasticsearch, Redis, API Server, File Server, Web UI
- **Отладочные порты:** MongoDB `27017`, Redis `6379`, Elasticsearch `9200/9300` проброшены на хост для диагностики (через `mongo`, `redis-cli`, `curl http://localhost:9200/_cluster/health`)
- **Перед запуском ClearML пайплайнов:** создайте шаблонные задачи (`prepare_data_template`, `validate_data_template`, `train_model_template`, `evaluate_model_template`) с помощью `uv run clearml-task create ...`, как описано в `docs/QUICKSTART.md`
- **Уведомления:** настройте, например, Slack Webhook (Settings → Workspace → Notifications) и добавьте параметры в `~/.clearml/clearml.conf`

**Примечание:** ClearML Server состоит из нескольких сервисов. Первый запуск может занять 1-2 минуты для инициализации.

Подробнее см. `docs/QUICKSTART.md` и `docs/homework_5/REPORT.md`

## Git Workflow

Проект использует следующую структуру веток:

- `main` - основная ветка с рабочим кодом
- `develop` - ветка разработки
- `feature/*` - ветки для новых функций
- `bugfix/*` - ветки для исправления ошибок
- `hotfix/*` - ветки для срочных исправлений

### GitHub Actions CI/CD

Проект настроен с автоматической проверкой кода через GitHub Actions:
- Автоматическая проверка форматирования и линтинга
- Запуск тестов при каждом push и pull request
- Сборка Docker образа для main и develop веток

Подробнее см. `.github/workflows/ci.yml`

### Создание веток

```bash
# Ветка разработки
git checkout -b develop

# Ветка для новой функции
git checkout -b feature/new-feature

# Ветка для исправления ошибки
git checkout -b bugfix/fix-name
```

## Инструменты качества кода

Проект использует следующие инструменты:

- **Black** - форматирование кода
- **isort** - сортировка импортов
- **Ruff** - быстрый линтер и форматтер
- **MyPy** - статическая проверка типов
- **Bandit** - проверка безопасности кода
- **pytest** - фреймворк для тестирования

Все инструменты настроены через pre-commit hooks и запускаются автоматически при коммите.

## Основные инструменты проекта

- **DVC** - версионирование данных и моделей, оркестрация пайплайнов
- **ClearML** - MLOps платформа для трекинга экспериментов и управления моделями
- **Pydantic** - валидация и управление конфигурациями
- **UV** - быстрый менеджер пакетов для Python (написан на Rust)
- **MinIO** - S3-совместимое хранилище для DVC
- **GitHub Actions** - CI/CD автоматизация
- **MkDocs** - генерация и публикация документации

## Документация

Документация проекта доступна онлайн на [GitHub Pages](https://gorobets.github.io/engineering_practices_ml/).

### Локальная документация

Для просмотра документации локально:

```bash
# Сборка документации
make docs-build

# Запуск локального сервера
make docs-serve
# Откройте http://127.0.0.1:8000
```

### Структура документации

- **Главная страница** - Обзор проекта и быстрый старт
- **Quick Start Guide** (`docs/QUICKSTART.md`) - Полное руководство по настройке
- **Deployment Guide** (`docs/DEPLOYMENT.md`) - Руководство по развертыванию
- **Homework Reports:**
  - `docs/homework_1/REPORT.md` - ДЗ 1: Настройка рабочего места Data Scientist
  - `docs/homework_2/REPORT.md` - ДЗ 2: Версионирование данных и моделей с DVC
  - `docs/homework_3/REPORT.md` - ДЗ 3: Трекинг экспериментов с DVC
  - `docs/homework_4/REPORT.md` - ДЗ 4: Автоматизация ML пайплайнов
  - `docs/homework_5/REPORT.md` - ДЗ 5: ClearML для MLOps
  - `docs/homework_6/REPORT.md` - ДЗ 6: Документация и отчеты
- **Experiment Reports** - Автоматически сгенерированные отчеты об экспериментах
- **API Reference** - Справочник API для всех модулей
- **Git Workflow** (`docs/GIT_WORKFLOW.md`) - Документация по Git workflow

## Автор

Горобец Игорь Сергеевич
