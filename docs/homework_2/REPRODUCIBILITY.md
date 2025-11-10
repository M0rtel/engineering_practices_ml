# Инструкции по воспроизведению проекта с DVC

## Предварительные требования

- Python 3.10+
- Poetry или pip
- Git
- Docker и docker compose (для MinIO)

## Быстрая установка

### 1. Клонирование и установка зависимостей

```bash
git clone <repository-url>
cd engineering_practices_ml
poetry install  # или pip install -r requirements.txt
```

### 2. Настройка DVC

```bash
# Автоматическая настройка
./scripts/setup_dvc.sh

# Или вручную
dvc init --no-scm
dvc remote add -d local storage/local
```

### 3. Запуск MinIO (S3-совместимое хранилище)

```bash
# Запуск MinIO
docker compose up -d minio

# Настройка DVC для MinIO
./scripts/setup_minio.sh
```

**Доступ к MinIO:**
- API: http://localhost:9000
- Console: http://localhost:9001
- Credentials: minioadmin / minioadmin

### 4. Загрузка данных и моделей

```bash
# Загрузка из MinIO
dvc pull --remote minio

# Или из local storage
dvc pull --remote local
```

## Воспроизведение pipeline

### Запуск всего pipeline

```bash
dvc repro
```

### Запуск отдельных стадий

```bash
dvc repro prepare_data
dvc repro train_model
dvc repro evaluate_model
```

## Версионирование данных и моделей

### Добавление данных

```bash
./scripts/track_data.sh data/raw/WineQT.csv
git add data/raw/WineQT.csv.dvc .gitignore
git commit -m "data: add dataset"
```

### Добавление модели

```bash
./scripts/track_model.sh models/model.pkl reports/metrics/model_metrics.json
git add models/model.pkl.dvc models/model.pkl.meta .gitignore
git commit -m "model: add trained model"
```

### Отправка в remote storage

```bash
# В MinIO
dvc push --remote minio

# В local storage
dvc push --remote local
```

## Сравнение версий

```bash
# Сравнение файлов
dvc diff data/raw/WineQT.csv HEAD~1

# Сравнение метрик
dvc metrics diff reports/metrics/model_metrics.json

# Сравнение параметров
dvc params diff
```

## Использование Docker

### Запуск с MinIO

```bash
docker compose up -d
```

### Работа в контейнере

```bash
docker compose exec ml-project bash
dvc pull --remote minio
dvc repro
```

## Тестирование воспроизводимости

```bash
# Очистка результатов
dvc remove models/model.pkl.dvc
rm -rf data/processed/* models/* reports/metrics/*

# Воспроизведение
dvc repro

# Проверка
ls -lh models/ reports/metrics/
```

## Устранение проблем

### MinIO не запускается

```bash
docker compose logs minio
docker compose down
docker compose up -d minio
```

### Ошибки DVC

```bash
dvc status
dvc checkout --force
```

Подробнее см. `docs/homework_2/MINIO_SETUP.md`
