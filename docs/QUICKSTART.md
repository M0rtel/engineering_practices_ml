# Руководство по быстрому старту

Полная пошаговая инструкция по настройке и использованию проекта Engineering Practices ML.

## Предварительные требования

- **Python 3.10+** - проверьте версию: `python3 --version`
- **Poetry** - менеджер зависимостей (установится автоматически или вручную)
- **Git** - система контроля версий
- **Docker и Docker Compose** (опционально, для MinIO и контейнеризации)

## Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd engineering_practices_ml
```

## Шаг 2: Установка Poetry

Если Poetry не установлен:

```bash
# Автоматическая установка (рекомендуется)
curl -sSL https://install.python-poetry.org | python3 -

# Добавить в PATH для текущей сессии
export PATH="$HOME/.local/bin:$PATH"

# Или добавить в ~/.bashrc для постоянного использования
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Проверка установки
poetry --version
```

Альтернативно через pip:
```bash
pip install poetry
```

## Шаг 3: Установка зависимостей проекта

### Вариант A: Автоматическая настройка (рекомендуется)

```bash
# Запустить скрипт автоматической настройки
./scripts/setup/setup.sh
```

Скрипт автоматически:
- Проверит наличие Poetry
- Установит все зависимости
- Настроит pre-commit hooks
- Создаст виртуальное окружение

### Вариант B: Ручная установка

```bash
# Установка зависимостей через Poetry
poetry install

# Активация виртуального окружения
poetry shell

# Проверка установки
poetry env info
```

**Важно:** Все последующие команды должны выполняться либо:
- В активированном окружении Poetry (`poetry shell`)
- Или с префиксом `poetry run` (например, `poetry run python`)

## Шаг 4: Настройка pre-commit hooks

Pre-commit hooks автоматически проверяют код при каждом коммите:

```bash
# Установка hooks
poetry run pre-commit install

# Проверка всех файлов (рекомендуется после установки)
poetry run pre-commit run --all-files
```

**Примечание:** Если hooks не установлены, можно пропустить этот шаг, но рекомендуется их использовать.

## Шаг 5: Настройка DVC (Data Version Control)

### 5.1. Инициализация DVC

```bash
# Инициализация DVC (если еще не инициализирован)
poetry run dvc init --no-scm

# Если DVC уже инициализирован, будет ошибка - это нормально
# Используйте -f для переинициализации: poetry run dvc init --no-scm -f
```

### 5.2. Настройка remote storage

Проект поддерживает три типа remote storage:

#### Local Storage (для локальной разработки)

```bash
poetry run dvc remote add local storage/local
```

#### MinIO (S3-совместимое хранилище через docker-compose)

**Шаг 1:** Запуск MinIO через docker-compose:

```bash
# Запуск MinIO
docker compose up -d minio

# Проверка статуса (должен быть "healthy")
docker compose ps minio
```

**Шаг 2:** Настройка DVC для MinIO:

```bash
# Автоматическая настройка
./scripts/setup/setup_minio.sh

# Или вручную:
poetry run dvc remote add minio s3://engineering-practices-ml/dvc
poetry run dvc remote modify minio endpointurl http://localhost:9000
poetry run dvc remote modify minio access_key_id minioadmin --local
poetry run dvc remote modify minio secret_access_key minioadmin --local
poetry run dvc remote default minio
```

**Шаг 3:** Создание bucket в MinIO:

```bash
docker compose exec -T minio sh -c "
  mc alias set local http://localhost:9000 minioadmin minioadmin && \
  mc mb local/engineering-practices-ml 2>/dev/null || echo 'Bucket уже существует'
"
```

**Доступ к MinIO:**
- **API:** http://localhost:9000
- **Console:** http://localhost:9001
- **Credentials:** minioadmin / minioadmin

#### AWS S3 (для production)

```bash
poetry run dvc remote add s3 s3://engineering-practices-ml/dvc

# Настройка credentials через переменные окружения или .dvc/config.local
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
```

### 5.3. Проверка конфигурации DVC

```bash
# Список всех remote storage
poetry run dvc remote list

# Проверка текущего default remote
poetry run dvc remote default

# Просмотр конфигурации
cat .dvc/config
```

## Шаг 6: Подготовка данных

### 6.1. Добавление исходных данных в DVC

```bash
# Автоматически через скрипт
./scripts/data/track_data.sh data/raw/WineQT.csv

# Или вручную
poetry run dvc add data/raw/WineQT.csv
git add data/raw/WineQT.csv.dvc .gitignore
git commit -m "data: add WineQT dataset"
```

### 6.2. Запуск pipeline подготовки данных

```bash
# Запуск стадии prepare_data
poetry run dvc repro prepare_data

# Проверка статуса
poetry run dvc status
```

**Ожидаемый результат:**
- Созданы файлы: `data/processed/train.csv`, `data/processed/test.csv`
- Созданы метрики: `reports/metrics/data_stats.json`
- Создан plot: `reports/plots/data_distribution.json`

## Шаг 7: Обучение модели

```bash
# Запуск стадии train_model
poetry run dvc repro train_model

# Проверка результата
ls -lh models/model.pkl
cat reports/metrics/model_metrics.json
```

**Ожидаемый результат:**
- Создана модель: `models/model.pkl`
- Созданы метрики: `reports/metrics/model_metrics.json`

## Шаг 8: Оценка модели

```bash
# Запуск стадии evaluate_model
poetry run dvc repro evaluate_model

# Проверка результата
cat reports/metrics/evaluation.json
```

**Ожидаемый результат:**
- Созданы метрики оценки: `reports/metrics/evaluation.json`
- Создан plot: `reports/plots/confusion_matrix.json`

## Шаг 9: Работа с remote storage

### Отправка данных в remote storage

```bash
# Отправка в default remote (minio)
poetry run dvc push

# Отправка в конкретный remote
poetry run dvc push --remote local
poetry run dvc push --remote minio
```

### Загрузка данных из remote storage

```bash
# Загрузка из default remote
poetry run dvc pull

# Загрузка из конкретного remote
poetry run dvc pull --remote local
poetry run dvc pull --remote minio
```

**Важно:** Перед `dvc pull` убедитесь, что все стадии pipeline выполнены, иначе могут возникнуть ошибки с отсутствующими файлами.

## Шаг 10: Работа с экспериментами

### 10.1. Настройка системы экспериментов

```bash
# Автоматическая настройка
./scripts/setup/setup_experiments.sh

# Это создаст:
# - Конфигурации экспериментов в config/experiments/
# - Необходимые директории
```

### 10.2. Запуск всех экспериментов

```bash
# Запуск всех 26 экспериментов
python scripts/experiments/run_all_experiments.py

# Или запуск одного эксперимента
python scripts/experiments/run_experiment.py \
  --model rf \
  --config config/experiments/exp_018_rf_100_10.yaml
```

### 10.3. Сравнение и фильтрация экспериментов

```bash
# Список всех экспериментов
python scripts/experiments/compare_experiments.py --list

# Сравнение двух экспериментов
python scripts/experiments/compare_experiments.py \
  --compare exp_001_linear exp_002_ridge_1.0

# Фильтрация по модели
python scripts/experiments/compare_experiments.py --filter-model rf

# Фильтрация по метрикам
python scripts/experiments/compare_experiments.py \
  --min-r2 0.5 --max-rmse 0.8

# Поиск экспериментов
python scripts/experiments/compare_experiments.py --search ridge

# Экспорт в CSV
python scripts/experiments/compare_experiments.py --export experiments.csv
```

### 10.4. Использование Python API для экспериментов

```python
from src.data_science_project import experiment_tracker

# Создание трекера
tracker = experiment_tracker.DVCExperimentTracker()

# Логирование параметров
tracker.log_params("exp_001", {"alpha": 1.0, "max_depth": 10})

# Логирование метрик
tracker.log_metrics("exp_001", {"test_r2": 0.85, "test_rmse": 0.5})

# Использование декоратора
from src.data_science_project.experiment_tracker import track_experiment

@track_experiment(experiment_id="exp_001")
def train_model(**params):
    # Код обучения
    return {"test_r2": 0.85}

# Использование контекстного менеджера
from src.data_science_project.experiment_tracker import experiment

with experiment("exp_001", params={"alpha": 1.0}) as tracker:
    # Код эксперимента
    tracker.log_metrics("exp_001", metrics)
```

## Шаг 11: Проверка качества кода

### Форматирование кода

```bash
# Black
poetry run black src tests scripts

# isort
poetry run isort src tests scripts

# Ruff (check + format)
poetry run ruff check src tests scripts
poetry run ruff format src tests scripts

# Или через Makefile
make format
```

### Линтинг

```bash
# MyPy (проверка типов)
poetry run mypy src

# Bandit (проверка безопасности)
poetry run bandit -r src

# Ruff (проверка стиля)
poetry run ruff check src tests scripts

# Или через Makefile
make lint
```

### Тестирование

```bash
# Запуск всех тестов
poetry run pytest

# С покрытием кода
poetry run pytest --cov=src --cov-report=html

# Или через Makefile
make test
make test-cov
```

## Шаг 12: Работа с Docker

### Сборка образа

```bash
docker build -t engineering-practices-ml .
```

### Запуск контейнера

```bash
# Простой запуск
docker run -it engineering-practices-ml

# С монтированием директорий
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/src:/app/src \
  engineering-practices-ml
```

### Запуск с MinIO через docker-compose

```bash
# Запуск MinIO и проекта
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка
docker compose down

# Остановка с удалением volumes
docker compose down -v
```

## Шаг 13: Работа с Git

### Структура веток

Проект использует Git Flow:

```bash
# Основные ветки
git checkout main      # Стабильная версия
git checkout develop   # Ветка разработки

# Создание веток для работы
git checkout -b feature/new-feature    # Новая функция
git checkout -b bugfix/fix-name        # Исправление ошибки
git checkout -b hotfix/urgent-fix     # Срочное исправление
```

### Коммит изменений

```bash
# Pre-commit hooks запустятся автоматически
git add .
git commit -m "feat: описание изменений"

# Если нужно пропустить hooks (не рекомендуется)
git commit --no-verify -m "message"
```

## Часто встречающиеся проблемы и решения

### Проблема 1: DVC уже инициализирован

**Ошибка:** `ERROR: failed to initiate DVC - '.dvc' exists`

**Решение:**
```bash
# Если нужно переинициализировать
poetry run dvc init --no-scm -f

# Или просто используйте существующую конфигурацию
poetry run dvc status
```

### Проблема 2: Отсутствуют файлы для pull

**Ошибка:** `ERROR: failed to pull data from the cloud - Checkout failed`

**Решение:**
```bash
# Убедитесь, что все стадии pipeline выполнены
poetry run dvc repro

# Затем попробуйте pull снова
poetry run dvc pull
```

### Проблема 3: MinIO не запускается

**Решение:**
```bash
# Проверка статуса
docker compose ps minio

# Просмотр логов
docker compose logs minio

# Перезапуск
docker compose restart minio

# Полная переустановка
docker compose down -v
docker compose up -d minio
```

### Проблема 4: Pre-commit hooks не работают

**Решение:**
```bash
# Переустановка hooks
poetry run pre-commit uninstall
poetry run pre-commit install

# Обновление hooks
poetry run pre-commit autoupdate

# Проверка вручную
poetry run pre-commit run --all-files
```

### Проблема 5: Ошибки MyPy

**Решение:**
```bash
# Проверка конкретного файла
poetry run mypy src/data_science_project/experiment_tracker.py

# Игнорирование отсутствующих импортов (если нужно)
poetry run mypy src --ignore-missing-imports
```

### Проблема 6: Модель не может быть добавлена в DVC

**Ошибка:** `ERROR: cannot update 'model.pkl': overlaps with an output of stage`

**Решение:**
Модель уже отслеживается через DVC pipeline. Используйте:
```bash
# Запуск pipeline для создания модели
poetry run dvc repro train_model

# Или принудительное обновление
poetry run dvc commit -f
```

## Полезные команды

### DVC

```bash
# Статус pipeline
poetry run dvc status

# Запуск всего pipeline
poetry run dvc repro

# Запуск конкретной стадии
poetry run dvc repro prepare_data
poetry run dvc repro train_model
poetry run dvc repro evaluate_model

# Сравнение метрик
poetry run dvc metrics diff

# Сравнение параметров
poetry run dvc params diff

# Просмотр метрик
poetry run dvc metrics show
```

### Poetry

```bash
# Информация об окружении
poetry env info

# Список зависимостей
poetry show

# Обновление зависимостей
poetry update

# Добавление новой зависимости
poetry add package-name

# Добавление dev зависимости
poetry add --group dev package-name
```

### Makefile

```bash
# Показать все доступные команды
make help

# Установка зависимостей
make install

# Форматирование кода
make format

# Линтинг
make lint

# Тесты
make test
make test-cov

# Очистка временных файлов
make clean

# Docker команды
make docker-build
make docker-run
```

## Проверка работоспособности

После настройки выполните полную проверку:

```bash
# 1. Проверка установки зависимостей
poetry run python --version
poetry run dvc --version

# 2. Проверка качества кода
poetry run pre-commit run --all-files

# 3. Проверка DVC
poetry run dvc status
poetry run dvc remote list

# 4. Проверка Docker (если используется)
docker compose ps

# 5. Запуск тестов
poetry run pytest

# 6. Запуск основного pipeline
poetry run dvc repro
```

## Следующие шаги

После успешной настройки:

1. **Изучите документацию:**
   - `README.md` - общая информация о проекте
   - `docs/homework_1/REPORT.md` - настройка рабочего места
   - `docs/homework_2/REPORT.md` - версионирование данных и моделей
   - `docs/homework_3/REPORT.md` - трекинг экспериментов

2. **Начните работу:**
   - Запустите pipeline: `poetry run dvc repro`
   - Проведите эксперименты: `python scripts/experiments/run_all_experiments.py`
   - Изучите результаты: `python scripts/experiments/compare_experiments.py --list`

3. **Настройте CI/CD:**
   - GitHub Actions уже настроен в `.github/workflows/ci.yml`
   - При push в `main` или `develop` автоматически запускаются проверки

## Получение помощи

- **Документация проекта:** `docs/`
- **GitHub Issues:** создайте issue в репозитории
- **DVC документация:** https://dvc.org/doc
- **Poetry документация:** https://python-poetry.org/docs/

## Важные замечания

1. **Всегда используйте `poetry run`** для команд Python/DVC, если не активировано окружение
2. **MinIO должен быть запущен** перед использованием `dvc push/pull` с MinIO remote
3. **Выполняйте pipeline последовательно:** `prepare_data` → `train_model` → `evaluate_model`
4. **Проверяйте статус DVC** перед push/pull: `poetry run dvc status`
5. **Credentials для MinIO** хранятся в `.dvc/config.local` (не в Git)

---

**Готово!** Проект настроен и готов к использованию. 🚀
