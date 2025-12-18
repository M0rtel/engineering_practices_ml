# Engineering Practices ML

Добро пожаловать в проект **Engineering Practices ML** - полноценный ML проект с использованием современных инженерных практик.

## О проекте

Этот проект демонстрирует применение современных инженерных практик в области Data Science и Machine Learning:

- ✅ **Версионирование данных и моделей** с помощью DVC
- ✅ **Трекинг экспериментов** с DVC и ClearML
- ✅ **Автоматизация ML пайплайнов** с DVC Pipelines
- ✅ **Управление конфигурациями** с Pydantic
- ✅ **MLOps платформа** ClearML для управления экспериментами и моделями
- ✅ **Контейнеризация** с Docker
- ✅ **CI/CD** с GitHub Actions
- ✅ **Документация** с MkDocs и автоматической публикацией

## Быстрый старт

Для начала работы с проектом:

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/M0rtel/engineering_practices_ml.git
   cd engineering_practices_ml
   ```

2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # или
   .venv\Scripts\activate  # Windows
   ```

3. **Установите зависимости:**
   ```bash
   uv sync
   ```

4. **Настройте проект:**
   ```bash
   dvc init --no-scm
   pre-commit install
   ```

5. **Запустите пайплайн:**
   ```bash
   dvc repro
   ```

📖 **Подробная инструкция:** [Quick Start Guide](QUICKSTART.md)

## Структура проекта

```
engineering_practices_ml/
├── data/              # Данные проекта
├── src/               # Исходный код
├── scripts/           # Вспомогательные скрипты
├── config/            # Конфигурационные файлы
├── docs/              # Документация
├── reports/           # Отчеты и результаты
└── tests/             # Тесты
```

## Основные возможности

### Версионирование данных

Проект использует DVC для версионирования данных и моделей:

```bash
# Добавление данных в DVC
dvc add data/raw/WineQT.csv

# Отправка в remote storage
dvc push
```

### Трекинг экспериментов

Система трекинга экспериментов с DVC и ClearML:

```bash
# Запуск эксперимента
python scripts/experiments/run_experiment.py \
  --model rf \
  --config config/experiments/exp_018_rf_100_10.yaml

# Сравнение экспериментов
python scripts/experiments/compare_experiments.py --list
```

### ML Пайплайны

Автоматизированные ML пайплайны с DVC:

```bash
# Запуск всего пайплайна
dvc repro

# Запуск с мониторингом
python scripts/pipeline/run_pipeline.py \
  --config config/train_params.yaml \
  --monitor
```

### ClearML Integration

Интеграция с ClearML для MLOps:

```bash
# Обучение с трекингом
python scripts/clearml/train_with_clearml.py \
  --config config/train_params.yaml \
  --model-type ridge

# Управление моделями
python scripts/clearml/manage_models.py --list
```

## Документация

- 📘 [Quick Start Guide](QUICKSTART.md) - Полное руководство по настройке
- 🚀 [Deployment Guide](DEPLOYMENT.md) - Руководство по развертыванию
- 📊 [Experiment Reports](reports/README.md) - Отчеты об экспериментах
- 📝 [Homework Reports](homework_1/REPORT.md) - Отчеты по домашним заданиям
  - [ДЗ 1: Quick Start](homework_1/QUICKSTART.md) | [Report](homework_1/REPORT.md)
  - [ДЗ 2: Quick Start](homework_2/QUICKSTART.md) | [Report](homework_2/REPORT.md)
  - [ДЗ 3: Quick Start](homework_3/QUICKSTART.md) | [Report](homework_3/REPORT.md)
  - [ДЗ 4: Quick Start](homework_4/QUICKSTART.md) | [Report](homework_4/REPORT.md)
  - [ДЗ 5: Quick Start](homework_5/QUICKSTART.md) | [Report](homework_5/REPORT.md)
  - [ДЗ 6: Quick Start](homework_6/QUICKSTART.md) | [Report](homework_6/REPORT.md)
- 🔧 [API Reference](api/experiment_tracker.md) - Справочник API

## Требования

- Python 3.10+
- UV
- Docker (опционально)
- Git

## Лицензия

MIT License

## Автор

**Игорь Горобец**

---

Для получения дополнительной информации см. [Quick Start Guide](QUICKSTART.md) или [Deployment Guide](DEPLOYMENT.md).
