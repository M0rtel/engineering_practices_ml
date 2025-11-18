# Руководство по развертыванию

Полное руководство по развертыванию проекта Engineering Practices ML в различных окружениях.

## Содержание

- [Локальное развертывание](#локальное-развертывание)
- [Развертывание с Docker](#развертывание-с-docker)
- [Развертывание в облаке](#развертывание-в-облаке)
- [Настройка CI/CD](#настройка-cicd)
- [Развертывание ClearML Server](#развертывание-clearml-server)
- [Развертывание MinIO](#развертывание-minio)

## Локальное развертывание

### Предварительные требования

- Python 3.10+
- UV (быстрый менеджер пакетов для Python)
- Git
- Docker и Docker Compose (для MinIO и ClearML)

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/gorobets/engineering_practices_ml.git
cd engineering_practices_ml
```

### Шаг 2: Установка зависимостей

```bash
# Установка UV (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей проекта
uv sync
```

### Шаг 3: Настройка DVC

```bash
# Инициализация DVC
uv run dvc init --no-scm

# Настройка remote storage (выберите один вариант)
# Локальное хранилище
uv run dvc remote add local storage/local
uv run dvc remote default local

# MinIO (требует запущенный MinIO)
uv run dvc remote add minio s3://engineering-practices-ml/dvc
uv run dvc remote modify minio endpointurl http://localhost:9000
uv run dvc remote modify minio access_key_id minioadmin --local
uv run dvc remote modify minio secret_access_key minioadmin --local
uv run dvc remote default minio
```

### Шаг 4: Настройка pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

### Шаг 5: Запуск пайплайна

```bash
# Добавление исходных данных
uv run dvc add data/raw/WineQT.csv

# Запуск пайплайна
uv run dvc repro
```

## Развертывание с Docker

### Сборка образа

```bash
docker build -t engineering-practices-ml:latest .
```

### Запуск контейнера

```bash
# Простой запуск
docker run -it engineering-practices-ml:latest

# С монтированием директорий
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  engineering-practices-ml:latest
```

### Docker Compose

Для запуска всех сервисов (MinIO, ClearML, проект):

```bash
# Запуск всех сервисов
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка
docker compose down
```

## Развертывание в облаке

### AWS

#### Настройка S3 для DVC

```bash
# Создание S3 bucket
aws s3 mb s3://engineering-practices-ml-dvc

# Настройка DVC для S3
uv run dvc remote add s3 s3://engineering-practices-ml-dvc/dvc

# Настройка credentials через переменные окружения
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### Развертывание на EC2

1. Создайте EC2 инстанс с Ubuntu
2. Установите зависимости:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.10 python3-pip git
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Клонируйте репозиторий и настройте проект
4. Настройте systemd service для автоматического запуска

### Google Cloud Platform

#### Настройка GCS для DVC

```bash
# Установка gsutil
pip install gsutil

# Создание bucket
gsutil mb gs://engineering-practices-ml-dvc

# Настройка DVC для GCS
uv run dvc remote add gcs gs://engineering-practices-ml-dvc/dvc
```

### Azure

#### Настройка Azure Blob Storage для DVC

```bash
# Настройка DVC для Azure
uv run dvc remote add azure azure://engineering-practices-ml-dvc/dvc
uv run dvc remote modify azure account_name your_account_name
uv run dvc remote modify azure account_key your_account_key --local
```

## Настройка CI/CD

### GitHub Actions

Проект уже настроен с GitHub Actions для автоматической проверки кода и тестирования.

Файл конфигурации: `.github/workflows/ci.yml`

#### Добавление автоматической публикации документации

См. `.github/workflows/docs.yml` для автоматической публикации документации на GitHub Pages.

### GitLab CI/CD

Пример `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.10
  script:
    - pip install uv
    - uv sync
    - uv run pytest

build:
  stage: build
  image: docker:latest
  script:
    - docker build -t engineering-practices-ml:$CI_COMMIT_SHA .

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
```

## Развертывание ClearML Server

### Локальное развертывание с Docker Compose

```bash
# Запуск всех сервисов ClearML
docker compose up -d clearml-mongo clearml-elastic clearml-redis clearml-server clearml-fileserver clearml-webserver

# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f clearml-server
```

### Развертывание в production

1. **Настройка MongoDB:**
   - Используйте managed MongoDB (MongoDB Atlas) или настроенный кластер
   - Обновите `docker-compose.yml` с правильными connection strings

2. **Настройка Elasticsearch:**
   - Используйте managed Elasticsearch или настроенный кластер
   - Настройте индексы и mappings

3. **Настройка Redis:**
   - Используйте managed Redis или настроенный кластер
   - Настройте persistence и replication

4. **Настройка ClearML Server:**
   - Обновите конфигурацию в `docker-compose.yml`
   - Настройте SSL/TLS для production
   - Настройте backup стратегию

### Настройка credentials

1. Откройте ClearML Web UI: http://localhost:8080
2. Создайте пользовательский аккаунт (не системный)
3. Создайте credentials в Settings > Workspace
4. Настройте локальный клиент:
   ```bash
   uv run python scripts/clearml/init_clearml.py \
     --api-host http://your-clearml-server:8008 \
     --web-host http://your-clearml-server:8080 \
     --access-key <your-key> \
     --secret-key <your-secret>
   ```

## Развертывание MinIO

### Локальное развертывание

```bash
# Запуск MinIO через Docker Compose
docker compose up -d minio

# Проверка статуса
docker compose ps minio

# Доступ к MinIO Console
# http://localhost:9001
# Credentials: minioadmin / minioadmin
```

### Production развертывание

1. **Настройка MinIO в production:**
   - Используйте MinIO в distributed mode для высокой доступности
   - Настройте SSL/TLS
   - Настройте backup и replication

2. **Настройка credentials:**
   - Измените default credentials
   - Используйте secrets management для хранения credentials

3. **Настройка bucket policies:**
   - Настройте IAM policies для доступа
   - Настройте lifecycle policies

## Мониторинг и логирование

### Настройка мониторинга

Проект включает систему мониторинга пайплайнов:

```bash
# Запуск с мониторингом
uv run python scripts/pipeline/run_pipeline.py \
  --config config/train_params.yaml \
  --monitor
```

Отчеты сохраняются в `reports/monitoring/pipeline_report.json`.

### Настройка логирования

Настройте логирование в `config/logging.yaml` или через переменные окружения.

## Troubleshooting

### Проблемы с DVC

```bash
# Проверка статуса
uv run dvc status

# Очистка кэша
uv run dvc cache dir
uv run dvc cache clean
```

### Проблемы с ClearML

```bash
# Проверка подключения
uv run python -c "from clearml import Task; print('OK')"

# Просмотр логов
docker compose logs clearml-server
```

### Проблемы с MinIO

```bash
# Проверка статуса
docker compose ps minio

# Просмотр логов
docker compose logs minio

# Перезапуск
docker compose restart minio
```

## Дополнительные ресурсы

- [DVC Documentation](https://dvc.org/doc)
- [ClearML Documentation](https://clear.ml/docs)
- [MinIO Documentation](https://min.io/docs)
- [Docker Documentation](https://docs.docker.com)

---

Для получения дополнительной информации см. [Quick Start Guide](QUICKSTART.md).
