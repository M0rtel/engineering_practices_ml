# Руководство по быстрому старту

Полная пошаговая инструкция по настройке и использованию проекта Engineering Practices ML.

## Предварительные требования

- **Python 3.10+** - проверьте версию: `python3 --version`
- **UV** - быстрый менеджер пакетов для Python (написан на Rust)
- **Git** - система контроля версий
- **Docker и Docker Compose** (опционально, для MinIO и контейнеризации)

## Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd engineering_practices_ml
```

## Шаг 2: Установка UV

Если UV не установлен:

```bash
# Автоматическая установка (рекомендуется)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Добавить в PATH для текущей сессии
export PATH="$HOME/.local/bin:$PATH"

# Или добавить в ~/.bashrc для постоянного использования
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Проверка установки
uv --version
```

Альтернативно через pip:
```bash
pip install uv
```

## Шаг 3: Создание виртуального окружения

UV может работать двумя способами:
1. **С явным виртуальным окружением** (рекомендуется) - создается в `.venv/`
2. **Без явного окружения** - UV управляет окружением автоматически

### Рекомендуемый способ: Явное виртуальное окружение

```bash
# Создание виртуального окружения
uv venv

# Активация виртуального окружения
# Для Linux/macOS:
source .venv/bin/activate

# Для Windows:
# .venv\Scripts\activate
```

**Проверка активации:**
```bash
# После активации в начале строки терминала должно появиться (.venv)
which python  # Должен показать путь к .venv/bin/python
python --version  # Должен показать Python 3.10+
```

## Шаг 4: Установка зависимостей проекта

### Вариант A: Автоматическая настройка (рекомендуется)

```bash
# Запустить скрипт автоматической настройки
./scripts/setup/setup.sh

# Скрипт автоматически:
# 1. Создаст виртуальное окружение (.venv)
# 2. Установит все зависимости
# 3. Настроит pre-commit hooks
```

**Примечание:** После выполнения скрипта активируйте виртуальное окружение:
```bash
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
```

### Вариант B: Ручная установка

```bash
# Убедитесь, что виртуальное окружение активировано
# (см. Шаг 3)

# Установка зависимостей через UV (включая dev зависимости)
uv sync --all-extras

# Проверка установки
python --version
pip list
```

**Важно:** После активации виртуального окружения все команды можно выполнять напрямую:
- `python script.py` вместо `python script.py`
- `dvc repro` вместо `dvc repro`
- `pytest` вместо `pytest`

**Деактивация окружения:**
```bash
deactivate
```

## Шаг 5: Настройка pre-commit hooks

**Важно:** Убедитесь, что виртуальное окружение активировано!

Pre-commit hooks автоматически проверяют код при каждом коммите:

```bash
# Установка hooks
pre-commit install

# Проверка всех файлов (рекомендуется после установки)
pre-commit run --all-files
```

**Примечание:** Если hooks не установлены, можно пропустить этот шаг, но рекомендуется их использовать.

## Шаг 6: Настройка DVC (Data Version Control)

### 6.1. Инициализация DVC

```bash
# Инициализация DVC (если еще не инициализирован)
dvc init --no-scm

# Если DVC уже инициализирован, будет ошибка - это нормально
# Используйте -f для переинициализации: dvc init --no-scm -f
```

### 6.2. Настройка remote storage

Проект поддерживает три типа remote storage:

#### Local Storage (для локальной разработки)

```bash
dvc remote add local storage/local
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
# Автоматическая настройка (если скрипт существует)
# ./scripts/setup/setup_minio.sh

# Или вручную:
dvc remote add minio s3://engineering-practices-ml/dvc
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin --local
dvc remote modify minio secret_access_key minioadmin --local
dvc remote default minio
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
dvc remote add s3 s3://engineering-practices-ml/dvc

# Настройка credentials через переменные окружения или .dvc/config.local
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
```

### 6.3. Проверка конфигурации DVC

```bash
# Список всех remote storage
dvc remote list

# Проверка текущего default remote
dvc remote default

# Просмотр конфигурации
cat .dvc/config
```

## Шаг 6: Подготовка данных

### 6.1. Добавление исходных данных в DVC

```bash
# Автоматически через скрипт (если существует)
./scripts/data/track_data.sh data/raw/WineQT.csv

# Или вручную
dvc add data/raw/WineQT.csv
git add data/raw/WineQT.csv.dvc .gitignore
git commit -m "data: add WineQT dataset"
```

### 6.2. Запуск pipeline подготовки данных

```bash
# Запуск стадии prepare_data
dvc repro prepare_data

# Проверка статуса
dvc status

# Просмотр графа зависимостей
dvc dag
```

**Ожидаемый результат:**
- Созданы файлы: `data/processed/train.csv`, `data/processed/test.csv`
- Созданы метрики: `reports/metrics/data_stats.json`
- Создан plot: `reports/plots/data_distribution.json`

**Примечание:** Скрипт использует Pydantic для валидации конфигурации из `config/train_params.yaml`. Для запуска всего пайплайна сразу см. **Шаг 13: Запуск полного ML пайплайна**.

## Шаг 7: Валидация данных

### 7.1. Запуск валидации данных

```bash
# Запуск стадии validate_data
dvc repro validate_data

# Проверка результата
cat reports/metrics/data_validation.json
```

**Ожидаемый результат:**
- Создан файл валидации: `reports/metrics/data_validation.json`
- Проверены: наличие целевой переменной, признаков, отсутствие пропусков

**Примечание:** Валидация выполняется автоматически с использованием Pydantic моделей для проверки конфигурации.

## Шаг 8: Обучение модели

### 8.1. Запуск обучения модели

```bash
# Запуск стадии train_model (использует модель из конфигурации)
dvc repro train_model

# Проверка результата
ls -lh models/model.pkl
cat reports/metrics/model_metrics.json
```

**Ожидаемый результат:**
- Создана модель: `models/model.pkl`
- Созданы метрики: `reports/metrics/model_metrics.json`

### 8.2. Использование разных типов моделей

Модель выбирается через параметр `model_type` в `dvc.yaml` или через конфигурацию:

**Через утилиту для изменения параметров:**
```bash
# Использование утилиты для изменения параметров и запуска
python scripts/pipeline/run_with_params.py train_model -S model_type=ridge
python scripts/pipeline/run_with_params.py train_model -S model_type=rf
python scripts/pipeline/run_with_params.py train_model -S model_type=gb
```

**Или изменение params.yaml напрямую:**
```bash
# Изменить model_type в params.yaml
# Затем запустить
dvc repro train_model
```

**Через конфигурационный файл:**
```yaml
# config/train_params.yaml
model:
  model_type: rf  # или linear, ridge, lasso, elasticnet, knn, svr, dt, rf, ada, gb
  params:
    n_estimators: 100
    max_depth: 10
```

**Поддерживаемые типы моделей:**
- `linear` - Linear Regression
- `ridge` - Ridge Regression
- `lasso` - Lasso Regression
- `elasticnet` - ElasticNet Regression
- `knn` - K-Nearest Neighbors
- `svr` - Support Vector Regression
- `dt` - Decision Tree
- `rf` - Random Forest (по умолчанию)
- `ada` - AdaBoost
- `gb` - Gradient Boosting

**Примечание:** Все конфигурации валидируются через Pydantic модели для обеспечения корректности параметров.

## Шаг 9: Оценка модели

```bash
# Запуск стадии evaluate_model
dvc repro evaluate_model

# Проверка результата
cat reports/metrics/evaluation.json
cat reports/plots/confusion_matrix.json
```

**Ожидаемый результат:**
- Созданы метрики оценки: `reports/metrics/evaluation.json`
- Создан plot: `reports/plots/confusion_matrix.json`

**Примечание:** Скрипт использует Pydantic для загрузки конфигурации и определения признаков.

## Шаг 10: Мониторинг пайплайна

### 10.1. Запуск мониторинга

```bash
# Запуск стадии monitor_pipeline (автоматически после evaluate_model)
dvc repro monitor_pipeline

# Или запуск полного пайплайна с мониторингом
python scripts/pipeline/run_pipeline.py --config config/train_params.yaml --monitor
```

**Ожидаемый результат:**
- Создан отчет мониторинга: `reports/monitoring/pipeline_report.json`
- Выведена сводка выполнения всех стадий
- Показаны метрики времени выполнения

### 10.2. Просмотр отчета мониторинга

```bash
# Просмотр последнего отчета
cat reports/monitoring/pipeline_report.json

# Или через Python
python -c "
import json
from pathlib import Path
report = json.load(open('reports/monitoring/pipeline_report.json'))
print('Статус:', report['summary'])
"
```

**Содержание отчета:**
- Статус каждой стадии (pending, running, completed, failed)
- Время выполнения каждой стадии
- Метрики и ошибки (если есть)
- Общая сводка выполнения

### 10.3. Запуск полного пайплайна с мониторингом

Для запуска полного пайплайна с мониторингом см. **Шаг 13.4: Запуск с мониторингом**.

## Шаг 11: Работа с remote storage

### Настройка default remote

Перед использованием `dvc push` или `dvc pull` без указания `-r` необходимо установить default remote:

```bash
# Установить local как default remote (для локальной разработки)
dvc remote default local

# Или установить minio как default remote (если MinIO запущен)
dvc remote default minio

# Проверить текущий default remote
dvc remote default
```

### Отправка данных в remote storage

```bash
# Отправка в default remote
dvc push

# Отправка в конкретный remote (без установки default)
dvc push --remote local
dvc push --remote minio
```

### Загрузка данных из remote storage

```bash
# Загрузка из default remote
dvc pull

# Загрузка из конкретного remote (без установки default)
dvc pull --remote local
dvc pull --remote minio
```

**Важно:**
- Перед `dvc pull` убедитесь, что все стадии pipeline выполнены, иначе могут возникнуть ошибки с отсутствующими файлами.
- Если default remote не установлен, используйте `-r <remote_name>` для указания конкретного remote.

### Типичные ошибки с MinIO и как их исправить

**Ошибка 1: InvalidAccessKeyId (неверный Access Key / Secret Key)**

Сообщение:

```text
The Access Key Id you provided does not exist in our records.
```

**Решение:**

1. Убедитесь, что MinIO запущен:

   ```bash
   docker compose up -d minio
   ```

2. В активированном окружении задайте креденшели (по умолчанию из `docker-compose.yml`):

   ```bash
   export AWS_ACCESS_KEY_ID=minioadmin
   export AWS_SECRET_ACCESS_KEY=minioadmin
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. После этого повторно выполните:

   ```bash
   dvc push -r minio
   ```

**Ошибка 2: NoSuchBucket (бакет не существует)**

Сообщение:

```text
The specified bucket does not exist.
```

**Решение:**

1. Откройте MinIO UI: `http://localhost:9000` (логин/пароль по умолчанию `minioadmin` / `minioadmin`).
2. Создайте bucket с именем:

   ```text
   engineering-practices-ml
   ```

3. Повторите команду:

   ```bash
   dvc push -r minio
   ```

> Подсказка: вместо ручного экспорта переменных можно создать `.dvc/config.local` и сохранить там `access_key_id` и `secret_access_key` для remote `minio`.

## Шаг 12: Работа с экспериментами

### 12.1. Настройка системы экспериментов

```bash
# Автоматическая настройка (если скрипт существует)
# ./scripts/setup/setup_experiments.sh

# Или вручную - конфигурации экспериментов создаются при первом запуске
# Это создаст:
# - Конфигурации экспериментов в config/experiments/
# - Необходимые директории
```

### 12.2. Запуск всех экспериментов

```bash
# Запуск всех 26 экспериментов
python scripts/experiments/run_all_experiments.py

# Или запуск одного эксперимента
python scripts/experiments/run_experiment.py \
  --model rf \
  --config config/experiments/exp_018_rf_100_10.yaml
```

### 12.3. Сравнение и фильтрация экспериментов

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

### 12.4. Использование Python API для экспериментов

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

## Шаг 13: Запуск полного ML пайплайна

### 13.1. Запуск всего пайплайна одной командой

```bash
# Запуск всех стадий последовательно
dvc repro

# Это выполнит:
# 1. prepare_data - подготовка данных
# 2. validate_data - валидация данных
# 3. train_model - обучение модели
# 4. evaluate_model - оценка модели
# 5. monitor_pipeline - мониторинг выполнения
```

### 13.2. Параллельное выполнение независимых стадий

```bash
# DVC автоматически определит независимые стадии и выполнит их параллельно
dvc repro --jobs 4

# Например, validate_data и train_model могут выполняться параллельно
# после завершения prepare_data
```

### 13.3. Запуск с изменением параметров

Для изменения параметров модели (например, `model_type`) см. **Шаг 8.2: Использование разных типов моделей**.

**Дополнительные примеры:**
```bash
# Изменение нескольких параметров одновременно
python scripts/pipeline/run_with_params.py train_model \
  -S model_type=ridge \
  -S enable_validation=true

# Или изменение params.yaml напрямую
# 1. Отредактировать params.yaml (изменить model_type)
# 2. dvc repro train_model
```

### 13.4. Запуск с мониторингом

```bash
# Запуск через скрипт с полным мониторингом
python scripts/pipeline/run_pipeline.py \
  --config config/train_params.yaml \
  --monitor

# Запуск конкретных стадий с мониторингом
python scripts/pipeline/run_pipeline.py \
  --config config/train_params.yaml \
  --monitor \
  --stages prepare_data validate_data train_model

# Результат:
# - Выполнение всех стадий
# - Отслеживание времени выполнения каждой стадии
# - Сохранение отчета мониторинга в reports/monitoring/
# - Уведомление о завершении
# - Детальная сводка выполнения
```

**Преимущества:**
- Автоматическое отслеживание всех стадий
- Детальные отчеты о выполнении
- Уведомления о завершении
- Сохранение истории выполнения

### 13.5. Просмотр графа зависимостей

```bash
# Визуализация зависимостей между стадиями
dvc dag

# Вывод покажет:
# - Порядок выполнения стадий
# - Зависимости между стадиями
# - Возможности параллельного выполнения
```

### 13.6. Проверка статуса пайплайна

```bash
# Проверка, какие стадии нужно перезапустить
dvc status

# Вывод покажет:
# - Измененные зависимости
# - Стадии, требующие перезапуска
# - Статус кэширования
```

## Шаг 14: Проверка качества кода

### Форматирование кода

```bash
# Black
black src tests scripts

# isort
isort src tests scripts

# Ruff (check + format)
ruff check src tests scripts
ruff format src tests scripts

# Или через Makefile
make format
```

### Линтинг

```bash
# MyPy (проверка типов)
mypy src

# Bandit (проверка безопасности)
bandit -r src

# Ruff (проверка стиля)
ruff check src tests scripts

# Или через Makefile
make lint
```

### Тестирование

```bash
# Запуск всех тестов
pytest

# С покрытием кода
pytest --cov=src --cov-report=html

# Или через Makefile
make test
make test-cov
```

## Шаг 15: Работа с Docker

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

## Шаг 16: Работа с Git

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
dvc init --no-scm -f

# Или просто используйте существующую конфигурацию
dvc status
```

### Проблема 2: Отсутствуют файлы для pull

**Ошибка:** `ERROR: failed to pull data from the cloud - Checkout failed`

**Решение:**
```bash
# Убедитесь, что все стадии pipeline выполнены
dvc repro

# Затем попробуйте pull снова
dvc pull
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
pre-commit uninstall
pre-commit install

# Обновление hooks
pre-commit autoupdate

# Проверка вручную
pre-commit run --all-files
```

### Проблема 5: Ошибки MyPy

**Решение:**
```bash
# Проверка конкретного файла
mypy src/data_science_project/experiment_tracker.py

# Игнорирование отсутствующих импортов (если нужно)
mypy src --ignore-missing-imports
```

### Проблема 6: Модель не может быть добавлена в DVC

**Ошибка:** `ERROR: cannot update 'model.pkl': overlaps with an output of stage`

**Решение:**
Модель уже отслеживается через DVC pipeline. Используйте:
```bash
# Запуск pipeline для создания модели
dvc repro train_model

# Или принудительное обновление
dvc commit -f
```

### Проблема 7: ClearML Server не запускается

**Ошибка:** `Container clearml-server is unhealthy` или `dependency failed to start: container clearml-server is unhealthy`

**Причина:** Healthcheck для `clearml-server` проверял корневой путь `/`, который возвращает 400 (сервер работает, но endpoint неверный).

**Решение:**
```bash
# Проверка статуса всех сервисов
docker compose ps

# Просмотр логов конкретного сервиса
docker compose logs clearml-server
docker compose logs clearml-webserver
docker compose logs clearml-mongo
docker compose logs clearml-elastic
docker compose logs clearml-redis

# Если сервер показывает "unhealthy", но работает (возвращает HTTP коды):
# Healthcheck был исправлен в docker-compose.yml
# Просто перезапустите сервер:
docker compose up -d --force-recreate clearml-server

# Перезапуск всех сервисов ClearML
docker compose restart clearml-mongo clearml-elastic clearml-redis clearml-server clearml-webserver

# Полная переустановка
docker compose down -v
docker compose up -d clearml-mongo clearml-elastic clearml-redis clearml-server clearml-webserver

# Ожидание готовности (может занять 1-2 минуты)
sleep 60
curl http://localhost:8080
curl http://localhost:8008
```

**Важно:**
- Убедитесь, что все зависимые сервисы (MongoDB, Elasticsearch, Redis) запущены перед запуском API Server.
- Если `clearml-server` показывает "unhealthy", но сервер отвечает на запросы (возвращает HTTP коды 400/404), это нормально - сервер работает, просто healthcheck был настроен неправильно. В текущей версии `docker-compose.yml` healthcheck исправлен.

### Проблема 8: ClearML не может подключиться к серверу

**Ошибка:** `Failed to connect to ClearML server`

**Решение:**
```bash
# Проверьте, что все сервисы запущены
docker compose ps

# Убедитесь, что API Server и Web UI работают
# API Server может возвращать 400 для корневого пути - это нормально
curl http://localhost:8008
curl http://localhost:8080

# Проверьте логи на наличие ошибок
docker compose logs clearml-server | tail -50

# Если сервер показывает "unhealthy", но отвечает на запросы:
# Это может быть проблема с healthcheck (исправлено в docker-compose.yml)
# Попробуйте перезапустить:
docker compose up -d --force-recreate clearml-server

# Проверьте credentials
clearml-init

# Или установите переменные окружения
export CLEARML_API_HOST=http://localhost:8008
export CLEARML_WEB_HOST=http://localhost:8080
export CLEARML_API_ACCESS_KEY=<your-key>
export CLEARML_API_SECRET_KEY=<your-key>
```

**Примечание:**
- Если Elasticsearch не запускается из-за нехватки памяти, увеличьте лимит памяти в `docker-compose.yml` или уменьшите `ES_JAVA_OPTS`.
- Если `clearml-server` возвращает HTTP 400 для корневого пути `/`, это нормально - сервер работает, просто этот endpoint не поддерживается. Healthcheck в `docker-compose.yml` настроен правильно и проверяет, что сервер отвечает (любой HTTP код).

### Проблема 9: "Invalid user id (protected identity)" при создании credentials

**Ошибка:** `Invalid user id (protected identity)` при попытке создать credentials в ClearML

**Причина:**
При первом запуске ClearML Server автоматически создается системный пользователь `__allegroai__`. Credentials можно создавать только для обычных пользовательских аккаунтов, не для системных.

**Решение:**
1. Откройте http://localhost:8080
2. Убедитесь, что вы **не** вошли в системный аккаунт `__allegroai__`
3. Если видите системного пользователя, выйдите из аккаунта
4. Создайте **новый пользовательский аккаунт**:
   - Нажмите "Sign Up" или "Create Account"
   - Заполните форму регистрации (email, пароль, имя)
   - Подтвердите регистрацию
5. Войдите в созданный аккаунт
6. Перейдите в **Settings > Workspace > Create new credentials**
7. Теперь credentials должны создаться успешно

**Проверка:**
```bash
# После создания credentials, проверьте их:
clearml-init

# Или установите переменные окружения:
export CLEARML_API_HOST=http://localhost:8008
export CLEARML_API_SECRET_KEY=<your-secret-key>
export CLEARML_API_ACCESS_KEY=<your-access-key>
```

## Полезные команды

### DVC

```bash
# Статус pipeline
dvc status

# Запуск всего pipeline
dvc repro

# Запуск конкретной стадии
dvc repro prepare_data
dvc repro validate_data
dvc repro train_model
dvc repro evaluate_model
dvc repro monitor_pipeline

# Запуск нескольких стадий
dvc repro prepare_data validate_data train_model

# Запуск с изменением параметров через утилиту
python scripts/pipeline/run_with_params.py train_model -S model_type=ridge
python scripts/pipeline/run_with_params.py train_model -S model_type=gb

# Или изменение params.yaml и запуск
# 1. Изменить model_type в params.yaml
# 2. dvc repro train_model

# Сравнение метрик
dvc metrics diff

# Сравнение параметров
dvc params diff

# Просмотр метрик
dvc metrics show
```

### UV

```bash
# Информация об окружении
uv --version

# Список зависимостей
uv pip list

# Обновление зависимостей
uv sync --upgrade

# Добавление новой зависимости
uv add package-name

# Добавление dev зависимости
uv add --group dev package-name
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
python --version
dvc --version

# 2. Проверка качества кода
pre-commit run --all-files

# 3. Проверка DVC
dvc status
dvc remote list

# 4. Проверка Docker (если используется)
docker compose ps

# 5. Запуск тестов
pytest

# 6. Запуск основного pipeline
dvc repro

# 7. Проверка мониторинга
ls -lh reports/monitoring/
cat reports/monitoring/pipeline_report.json

# 8. Проверка Pydantic моделей
python -c "from src.data_science_project.config_models import TrainingConfig; print('✅ Pydantic models OK')"

# 9. Проверка ClearML (если настроен)
python -c "from src.data_science_project.clearml_tracker import ClearMLTracker; print('✅ ClearML OK')" 2>/dev/null || echo "⚠️ ClearML не настроен (опционально)"
```

## Следующие шаги

После успешной настройки:

1. **Изучите документацию:**
   - `README.md` - общая информация о проекте
   - `docs/homework_1/REPORT.md` - настройка рабочего места
   - `docs/homework_2/REPORT.md` - версионирование данных и моделей
   - `docs/homework_3/REPORT.md` - трекинг экспериментов
   - `docs/homework_4/REPORT.md` - автоматизация ML пайплайнов
   - `docs/homework_5/REPORT.md` - ClearML для MLOps

2. **Начните работу:**
   - Запустите полный pipeline: `dvc repro` (см. Шаг 13)
   - Запустите с мониторингом: `python scripts/pipeline/run_pipeline.py --config config/train_params.yaml --monitor` (см. Шаг 13.4)
   - Попробуйте разные модели: `python scripts/pipeline/run_with_params.py train_model -S model_type=ridge` (см. Шаг 8.2)
   - Проведите эксперименты: `python scripts/experiments/run_all_experiments.py` (см. Шаг 12)
   - Изучите результаты: `python scripts/experiments/compare_experiments.py --list` (см. Шаг 12.3)
   - Просмотрите отчет мониторинга: `cat reports/monitoring/pipeline_report.json` (см. Шаг 10.2)
   - (Опционально) Настройте ClearML и запустите эксперименты с трекингом: `python scripts/clearml/train_with_clearml.py --config config/train_params.yaml --model-type ridge` (см. Шаг 17)

3. **Настройте CI/CD:**
   - GitHub Actions уже настроен в `.github/workflows/ci.yml`
   - При push в `main` или `develop` автоматически запускаются проверки

## Шаг 17: Работа с ClearML (ДЗ 5)

### 17.1. Запуск ClearML Server

ClearML Server состоит из нескольких сервисов:
- MongoDB - база данных
- Elasticsearch - поиск и индексация
- Redis - кэширование
- API Server - API сервер (порт 8008)
- File Server - файловый сервер для артефактов (порт 8081)
- Web UI - веб-интерфейс (порт 8080)

```bash
# Запуск всех сервисов ClearML
docker compose up -d clearml-mongo clearml-elastic clearml-redis clearml-server clearml-fileserver clearml-webserver

# Или запуск всех сервисов сразу
docker compose up -d

# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f clearml-server
docker compose logs -f clearml-webserver

# ClearML Web UI: http://localhost:8080
# ClearML API: http://localhost:8008
# ClearML File Server: http://localhost:8081
# MongoDB: mongodb://localhost:27017
# Redis: redis://localhost:6379
# Elasticsearch: http://localhost:9200
# Transport-порт Elasticsearch: 9300 (для внешних агентов)
# Примеры проверок:
#   curl http://localhost:9200/_cluster/health?pretty
#   mongo --host localhost --eval "db.runCommand({ping:1})"
#   redis-cli -h localhost ping
```

**Примечание:**
- Первый запуск может занять 1-2 минуты для инициализации всех сервисов.
- Если `clearml-server` показывает статус "unhealthy" при первом запуске, подождите 1-2 минуты - серверу нужно время для инициализации. Healthcheck настроен с `start_period: 90s` для учета времени запуска.
- Если проблема сохраняется, проверьте логи: `docker compose logs clearml-server | tail -50`

### 17.2. Настройка credentials

**Важно:** При первом запуске ClearML Server создается системный пользователь `__allegroai__`. Для работы нужно создать обычного пользователя.

1. Откройте http://localhost:8080
2. **Создайте новый аккаунт** (не используйте системный пользователь):
   - Нажмите "Sign Up" или "Create Account"
   - Заполните форму регистрации (email, пароль, имя)
   - Подтвердите регистрацию
3. Войдите в созданный аккаунт
4. Перейдите в **Settings > Workspace > Create new credentials**
5. Скопируйте **Access Key** и **Secret Key**

**Если возникает ошибка "Invalid user id (protected identity)":**
- Убедитесь, что вы вошли в обычный пользовательский аккаунт (не системный)
- Если вы видите системного пользователя `__allegroai__`, создайте новый аккаунт через "Sign Up"
- Credentials можно создавать только для обычных пользователей, не для системных

### 17.3. Подготовка шаблонов задач для пайплайна

`scripts/clearml/ml_pipeline.py` использует существующие шаблонные задачи (`base_task_name`). Их нужно создать один раз (из корня репозитория):

```bash
PROJECT="Engineering Practices ML"

# Создать все шаблонные задачи одной командой
python scripts/clearml/create_task_templates.py \
  --project "$PROJECT" \
  --queue default \
  --all

# Или создать задачи по одной (интерактивный режим)
python scripts/clearml/create_task_templates.py --project "$PROJECT"
```

Проверка:

```bash
python scripts/clearml/compare_experiments.py --list --limit 10
```

Шаблонные задачи должны появиться в UI проекта. При желании их можно создать вручную в веб-интерфейсе (Create Task → Scripts → указать файл → Save as template) — главное, чтобы названия совпадали.

### 17.4. Инициализация ClearML

**Важно:** Перед инициализацией убедитесь, что вы получили credentials (см. раздел 17.2).

```bash
# Через скрипт (с указанием credentials)
python scripts/clearml/init_clearml.py \
  --api-host http://localhost:8008 \
  --web-host http://localhost:8080 \
  --access-key <your-access-key> \
  --secret-key <your-secret-key>

# Или через переменные окружения
export CLEARML_API_HOST=http://localhost:8008
export CLEARML_WEB_HOST=http://localhost:8080
export CLEARML_API_ACCESS_KEY=<your-access-key>
export CLEARML_API_SECRET_KEY=<your-secret-key>
clearml-init

# Или запустите скрипт без параметров - он покажет инструкции
python scripts/clearml/init_clearml.py
```

**Проверка инициализации:**
```bash
# Проверьте, что ClearML может подключиться
python -c "from clearml import Task; print('✅ ClearML подключен')"
```

### 17.5. Запуск эксперимента с трекингом

```bash
# Обучение модели с трекингом
python scripts/clearml/train_with_clearml.py \
  --config config/train_params.yaml \
  --model-type ridge \
  --experiment-name ridge_experiment_001
```

**Примечание:** Если в конце выполнения появляются ошибки подключения (Connection refused), убедитесь, что `clearml-fileserver` запущен: `docker compose up -d clearml-fileserver`. Fileserver необходим для загрузки артефактов (модели, метрики) в ClearML. После запуска fileserver ошибки должны исчезнуть.

### 17.6. Сравнение экспериментов

```bash
# Список экспериментов
python scripts/clearml/compare_experiments.py --list

# Сравнение
python scripts/clearml/compare_experiments.py \
  --compare <task_id_1> <task_id_2>
```

### 17.7. Управление моделями

```bash
# Список моделей
python scripts/clearml/manage_models.py --list

# Регистрация модели
python scripts/clearml/manage_models.py \
  --register models/model.pkl \
  --name wine_quality_model
```

### 17.8. Запуск пайплайна

```bash
# Создание и запуск пайплайна
python scripts/clearml/ml_pipeline.py \
  --model-type rf \
  --queue default
```

### 17.9. Использование Python API для ClearML

```python
from src.data_science_project.clearml_tracker import ClearMLTracker

# Создание трекера
tracker = ClearMLTracker(
    project_name="Engineering Practices ML",
    task_name="my_experiment",
    tags=["ridge", "training"]
)

# Логирование параметров
tracker.log_params({"alpha": 1.0, "max_depth": 10})

# Логирование метрик
tracker.log_metrics({"test_r2": 0.85, "test_rmse": 0.5})

# Регистрация модели
tracker.log_model(
    model_path="models/model.pkl",
    model_name="wine_quality_model",
    metadata={"version": "1.0.0"}
)

# Закрытие задачи
tracker.close()
```

### 17.10. Просмотр экспериментов в веб-интерфейсе

После запуска экспериментов:
1. Откройте http://localhost:8080
2. Перейдите в проект "Engineering Practices ML"
3. Просмотрите список экспериментов
4. Откройте конкретный эксперимент для просмотра метрик, параметров и артефактов

### 17.11. Настройка уведомлений

ClearML поддерживает уведомления через Slack, Email и Webhooks. Пример настройки Slack:

1. Создайте Slack Incoming Webhook и скопируйте URL.
2. В ClearML UI перейдите в Settings → Workspace → Notifications → Add Rule.
3. Выберите `Slack`, вставьте URL, включите события (например, Task completed/failed, Pipeline failed).
4. Добавьте секцию в `~/.clearml/clearml.conf`, чтобы CLI также отправлял уведомления:

```ini
notifications {
    slack {
        url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
        channel = "#mlops-alerts"
        notify_failed = true
        notify_completed = true
    }
}
```

После этого все задачи и пайплайны будут автоматически слать уведомления в выбранный канал. Аналогично можно добавить email или webhook.

Подробнее см. `docs/homework_5/REPORT.md` и `docs/homework_5/screenshots/README.md`

## Получение помощи

- **Документация проекта:** `docs/`
- **GitHub Issues:** создайте issue в репозитории
- **DVC документация:** https://dvc.org/doc
- **UV документация:** https://docs.astral.sh/uv/
- **ClearML документация:** https://clear.ml/docs

## Важные замечания

1. **Всегда активируйте виртуальное окружение** перед работой: `source .venv/bin/activate` (Linux/macOS) или `.venv\Scripts\activate` (Windows)
2. **MinIO должен быть запущен** перед использованием `dvc push/pull` с MinIO remote
3. **Выполняйте pipeline последовательно:** `prepare_data` → `validate_data` → `train_model` → `evaluate_model` → `monitor_pipeline`
4. **Или запускайте все сразу:** `dvc repro` (DVC автоматически определит порядок)
5. **Проверяйте статус DVC** перед push/pull: `dvc status`
6. **Credentials для MinIO** хранятся в `.dvc/config.local` (не в Git)
7. **Конфигурации валидируются через Pydantic** - проверяйте корректность параметров в `config/train_params.yaml`
8. **Мониторинг пайплайна** автоматически сохраняет отчеты в `reports/monitoring/`
9. **Параллельное выполнение** доступно через `dvc repro --jobs N` для независимых стадий
10. **ClearML Server** должен быть запущен перед использованием ClearML: `docker compose up -d clearml-mongo clearml-elastic clearml-redis clearml-server clearml-fileserver clearml-webserver` (см. Шаг 17.1)
11. **ClearML credentials** настраиваются через веб-интерфейс (http://localhost:8080) или переменные окружения
12. **Для ClearML** используйте `python scripts/clearml/` для всех скриптов (в активированном окружении)

---

**Готово!** Проект настроен и готов к использованию. 🚀
