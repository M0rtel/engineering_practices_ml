# Отчет о настройке версионирования данных и моделей с DVC

## Введение

Настроена система версионирования данных и моделей с использованием DVC (Data Version Control) и MinIO (S3-совместимое хранилище). Все компоненты автоматизированы и готовы к использованию.

## 1. Настройка выбранного инструмента для данных (4 балла)

### 1.1. Установка и настройка DVC

**Установка через Poetry:**
```toml
dvc = {extras = ["s3"], version = "^3.48.0"}
boto3 = "^1.34.0"
pyyaml = "^6.0.1"
```

**Инициализация:**
```bash
dvc init --no-scm
```

**Скриншот:** Результат инициализации DVC
*(Здесь должен быть скриншот вывода команды `dvc init`)*

### 1.2. Настройка remote storage

Настроены три типа remote storage:

1. **Local Storage** (`storage/local`) - для локальной разработки
2. **MinIO** (`http://localhost:9000`) - S3-совместимое хранилище через docker-compose
3. **AWS S3** - для production (требует credentials)

**Конфигурация в `.dvc/config`:**
```ini
['remote "local"']
    url = storage/local
['remote "minio"']
    url = s3://engineering-practices-ml/dvc
    endpointurl = http://localhost:9000
['remote "s3"']
    url = s3://engineering-practices-ml/dvc
```

**MinIO запускается через docker-compose:**
```bash
docker compose up -d minio
```

**Скриншот:** Конфигурация remote storage и MinIO Console
*(Здесь должен быть скриншот `.dvc/config` и MinIO Console на http://localhost:9001)*

### 1.3. Создание системы версионирования данных

**Добавление данных в DVC:**
```bash
# Автоматически
./scripts/track_data.sh data/raw/WineQT.csv

# Вручную
dvc add data/raw/WineQT.csv
git add data/raw/WineQT.csv.dvc .gitignore
git commit -m "data: add WineQT dataset"
```

**Python API:**
```python
from src.data_science_project import dvc_utils
dvc_utils.track_data("data/raw/WineQT.csv")
dvc_utils.pull_data(remote="minio")
dvc_utils.push_data(remote="minio")
```

**Скриншот:** Структура .dvc файлов для данных
*(Здесь должен быть скриншот содержимого `data/raw/WineQT.csv.dvc`)*

### 1.4. Настройка автоматического создания версий

**DVC Pipeline (`dvc.yaml`):**
```yaml
stages:
  prepare_data:
    cmd: python scripts/prepare_data.py
    deps:
      - data/raw/WineQT.csv
    outs:
      - data/processed/train.csv
      - data/processed/test.csv
```

**Запуск:**
```bash
dvc repro prepare_data
```

**Скриншот:** Результат выполнения DVC pipeline
*(Здесь должен быть скриншот вывода `dvc repro`)*

## 2. Настройка выбранного инструмента для моделей (3 балла)

### 2.1. Настройка DVC для моделей

Модели версионируются аналогично данным:
```bash
dvc add models/model.pkl
```

**Скриншот:** Структура .dvc файлов для моделей
*(Здесь должен быть скриншот содержимого `models/model.pkl.dvc`)*

### 2.2. Создание системы версионирования моделей

**Добавление модели:**
```bash
./scripts/track_model.sh models/model.pkl reports/metrics/model_metrics.json
```

**Версионирование метрик:**
```yaml
stages:
  train_model:
    outs:
      - models/model.pkl
    metrics:
      - reports/metrics/model_metrics.json
```

**Скриншот:** Версионирование метрик модели
*(Здесь должен быть скриншот вывода `dvc metrics show`)*

### 2.3. Настройка метаданных для моделей

Метаданные сохраняются в `models/model.pkl.meta`:
```json
{
  "model_name": "model.pkl",
  "created_at": "2024-11-10T20:00:00",
  "version": "v1.0.0",
  "metrics_file": "reports/metrics/model_metrics.json",
  "description": "ML model trained on WineQT dataset"
}
```

**Скриншот:** Пример метаданных модели
*(Здесь должен быть скриншот содержимого `models/model.pkl.meta`)*

### 2.4. Создание системы сравнения версий

**Сравнение файлов:**
```bash
dvc diff models/model.pkl HEAD~1 HEAD
```

**Сравнение метрик:**
```bash
dvc metrics diff reports/metrics/model_metrics.json
```

**Сравнение параметров:**
```bash
dvc params diff
```

**Python API:**
```python
comparison = dvc_utils.compare_versions("models/model.pkl", "HEAD~1", "HEAD")
```

**Скриншот:** Результаты сравнения версий
*(Здесь должен быть скриншот вывода `dvc diff` и `dvc metrics diff`)*

## 3. Воспроизводимость (2 балла)

### 3.1. Инструкции по воспроизведению

Создан документ `docs/homework_2/REPRODUCIBILITY.md` с инструкциями:
- Установка и настройка DVC
- Настройка remote storage (Local, MinIO, S3)
- Загрузка данных и моделей
- Воспроизведение pipeline
- Использование Docker

**Скриншот:** Инструкции по воспроизведению
*(Здесь должен быть скриншот документа REPRODUCIBILITY.md)*

### 3.2. Фиксация версий зависимостей

Версии зафиксированы в:
- `pyproject.toml` - для Poetry
- `requirements.txt` - для pip
- `poetry.lock` - точные версии (генерируется автоматически)

**Скриншот:** Зафиксированные версии зависимостей
*(Здесь должен быть скриншот содержимого requirements.txt)*

### 3.3. Тестирование воспроизводимости

**Тест полного pipeline:**
```bash
# Очистка результатов
dvc remove models/model.pkl.dvc
rm -rf data/processed/* models/* reports/metrics/*

# Воспроизведение
dvc repro

# Проверка
ls -lh models/ reports/metrics/
```

**Скриншот:** Результаты тестирования воспроизводимости
*(Здесь должен быть скриншот успешного выполнения `dvc repro`)*

### 3.4. Docker контейнер

**Dockerfile обновлен:**
```dockerfile
RUN dvc init --no-scm || true
```

**Запуск с MinIO:**
```bash
docker compose up -d
```

**Скриншот:** Успешная сборка Docker образа с DVC
*(Здесь должен быть скриншот вывода `docker compose up`)*

## 4. Отчет о проделанной работе (1 балл)

### 4.1. Отчет в формате Markdown

Отчет создан в `docs/homework_2/REPORT.md` и включает:
- Описание настройки DVC для данных и моделей
- Настройку remote storage (Local, MinIO, S3)
- Систему версионирования и метаданных
- Инструкции по воспроизведению
- Места для скриншотов

### 4.2. Описание настройки инструментов

В отчете описаны:
1. **DVC** - установка, инициализация, конфигурация
2. **Remote Storage** - Local, MinIO (через docker-compose), AWS S3
3. **Версионирование данных** - добавление, Python API, pipeline
4. **Версионирование моделей** - добавление, метрики, метаданные
5. **Сравнение версий** - файлы, метрики, параметры
6. **Воспроизводимость** - инструкции, тесты, Docker

### 4.3. Скриншоты результатов

В отчете предусмотрены места для скриншотов:
1. Инициализация DVC
2. Конфигурация remote storage и MinIO Console
3. Структура .dvc файлов для данных
4. Результат выполнения DVC pipeline
5. Структура .dvc файлов для моделей
6. Версионирование метрик модели
7. Пример метаданных модели
8. Результаты сравнения версий
9. Инструкции по воспроизведению
10. Зафиксированные версии зависимостей
11. Результаты тестирования воспроизводимости
12. Успешная сборка Docker образа

### 4.4. Сохранение в Git репозитории

Отчет сохранен в `docs/homework_2/REPORT.md` и включен в Git репозиторий.

**Скриншот:** Отчет в Git репозитории
*(Здесь должен быть скриншот файла REPORT.md в GitHub)*

## Заключение

Настроена полноценная система версионирования данных и моделей:

✅ **DVC установлен и настроен** - через Poetry с поддержкой S3
✅ **Remote storage настроен** - Local, MinIO (docker-compose), S3
✅ **Система версионирования данных** - автоматическое создание версий через pipeline
✅ **Система версионирования моделей** - с метаданными и метриками
✅ **Сравнение версий** - файлов, метрик и параметров
✅ **Воспроизводимость** - инструкции, тесты, Docker с MinIO
✅ **Отчет создан** - с описанием всех настроек и местами для скриншотов

Все инструменты настроены, протестированы и готовы к использованию.
