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
│   └── pipeline/     # Скрипты для пайплайнов
├── config/           # Конфигурационные файлы
├── params.yaml       # Параметры DVC pipeline
├── dvc.yaml          # Конфигурация DVC pipeline
├── reports/          # Отчеты и результаты
│   ├── figures/      # Графики и визуализации
│   └── models/       # Сохраненные модели
├── pyproject.toml    # Конфигурация Poetry
├── requirements.txt  # Зависимости проекта
├── Dockerfile        # Docker конфигурация
└── README.md         # Этот файл
```

## Требования

- Python 3.10+
- Poetry (для управления зависимостями)
- Docker (опционально, для контейнеризации)

## Установка

### 1. Установка Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Или через pip:
```bash
pip install poetry
```

### 2. Клонирование и установка зависимостей

```bash
# Клонировать репозиторий
git clone <repository-url>
cd engineering_practices_ml

# Установить зависимости через Poetry
poetry install

# Активировать виртуальное окружение
poetry shell
```

### 3. Альтернативная установка через pip

```bash
pip install -r requirements.txt
```

## Настройка pre-commit hooks

После установки зависимостей настройте pre-commit hooks:

```bash
# Установить hooks
poetry run pre-commit install

# Или если используете pip
pre-commit install

# Запустить проверку всех файлов
pre-commit run --all-files
```

## Использование

### Запуск проекта

```bash
python main.py
```

### Запуск ML пайплайна

```bash
# Запуск всего пайплайна
poetry run dvc repro

# Запуск конкретной стадии
poetry run dvc repro prepare_data
poetry run dvc repro train_model

# Запуск с изменением параметров
poetry run python scripts/pipeline/run_with_params.py train_model -S model_type=ridge

# Запуск с мониторингом
poetry run python scripts/pipeline/run_pipeline.py --config config/train_params.yaml --monitor
```

Подробнее см. `docs/QUICKSTART.md`

### Форматирование кода

```bash
# Black
poetry run black src tests

# isort
poetry run isort src tests

# Ruff
poetry run ruff check src tests
poetry run ruff format src tests
```

### Линтинг

```bash
# MyPy
poetry run mypy src

# Bandit (проверка безопасности)
poetry run bandit -r src
```

### Тестирование

```bash
# Запуск всех тестов
poetry run pytest

# С покрытием кода
poetry run pytest --cov=src --cov-report=html
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

### Запуск с MinIO (S3-совместимое хранилище)

```bash
# Запуск MinIO и проекта
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

MinIO доступен по адресам:
- **API:** http://localhost:9000
- **Console:** http://localhost:9001
- **Credentials:** minioadmin / minioadmin

Подробнее см. `docs/QUICKSTART.md` (раздел "Настройка DVC" и "Запуск с MinIO")

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
- **Pydantic** - валидация и управление конфигурациями
- **Poetry** - управление зависимостями
- **MinIO** - S3-совместимое хранилище для DVC
- **GitHub Actions** - CI/CD автоматизация

## Документация

- `docs/homework_1/` - Домашнее задание 1: Настройка рабочего места Data Scientist
  - `REPORT.md` - Отчет о проделанной работе
- `docs/homework_2/` - Домашнее задание 2: Версионирование данных и моделей с DVC
  - `REPORT.md` - Отчет о проделанной работе
- `docs/homework_3/` - Домашнее задание 3: Трекинг экспериментов с DVC
  - `REPORT.md` - Отчет о проделанной работе
- `docs/homework_4/` - Домашнее задание 4: Автоматизация ML пайплайнов
  - `REPORT.md` - Отчет о проделанной работе
- `docs/GIT_WORKFLOW.md` - Документация по Git workflow
- `docs/QUICKSTART.md` - Руководство по быстрому старту

## Автор

Горобец Игорь Сергеевич
