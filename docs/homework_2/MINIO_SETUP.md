# Настройка MinIO для DVC

## Описание

MinIO - это S3-совместимое объектное хранилище, которое можно использовать локально для разработки и тестирования. В проекте MinIO настроен как альтернатива AWS S3 для хранения данных и моделей через DVC.

## Запуск MinIO

### Через docker-compose

```bash
# Запуск MinIO
docker-compose up -d minio

# Просмотр логов
docker-compose logs -f minio

# Остановка MinIO
docker-compose stop minio
```

### Автоматическая настройка

```bash
./scripts/setup_minio.sh
```

Скрипт автоматически:
- Запускает MinIO через docker-compose
- Ждет пока MinIO запустится
- Настраивает DVC для работы с MinIO
- Создает необходимый bucket

## Доступ к MinIO

После запуска MinIO доступен по следующим адресам:

- **API (S3 endpoint):** http://localhost:9000
- **Web Console:** http://localhost:9001

**Учетные данные по умолчанию:**
- Access Key: `minioadmin`
- Secret Key: `minioadmin`

⚠️ **Важно:** В production измените эти credentials!

## Настройка DVC для работы с MinIO

### Автоматическая настройка

```bash
./scripts/setup_minio.sh
```

### Ручная настройка

1. Добавьте MinIO как remote:
   ```bash
   dvc remote add minio s3://engineering-practices-ml/dvc
   ```

2. Настройте endpoint:
   ```bash
   dvc remote modify minio endpointurl http://localhost:9000
   ```

3. Настройте credentials (локально, не в Git):
   ```bash
   dvc remote modify minio --local access_key_id minioadmin
   dvc remote modify minio --local secret_access_key minioadmin
   ```

4. Установите MinIO как default remote:
   ```bash
   dvc remote default minio
   ```

## Использование MinIO с DVC

### Отправка данных в MinIO

```bash
# Отправка всех данных и моделей
dvc push --remote minio

# Отправка конкретного файла
dvc push data/raw/WineQT.csv.dvc --remote minio
```

### Загрузка данных из MinIO

```bash
# Загрузка всех данных и моделей
dvc pull --remote minio

# Загрузка конкретного файла
dvc pull data/raw/WineQT.csv.dvc --remote minio
```

### Проверка статуса

```bash
# Проверка статуса DVC
dvc status

# Список remotes
dvc remote list

# Просмотр конфигурации MinIO remote
dvc remote show minio
```

## Работа через MinIO Console

1. Откройте http://localhost:9001 в браузере
2. Войдите с credentials: `minioadmin` / `minioadmin`
3. Создайте bucket `engineering-practices-ml` (если не создан автоматически)
4. Просматривайте загруженные файлы

**Скриншот:** MinIO Console с загруженными данными
*(Здесь должен быть скриншот MinIO Console)*

## Использование в Docker контейнере

При запуске проекта через docker-compose, MinIO доступен по адресу `http://minio:9000` внутри сети Docker.

### Настройка DVC в контейнере

```bash
# Войти в контейнер
docker-compose exec ml-project bash

# Настроить MinIO remote
dvc remote add minio s3://engineering-practices-ml/dvc
dvc remote modify minio endpointurl http://minio:9000
dvc remote modify minio --local access_key_id minioadmin
dvc remote modify minio --local secret_access_key minioadmin

# Загрузить данные
dvc pull --remote minio
```

## Переменные окружения

В docker-compose.yml настроены следующие переменные:

```yaml
environment:
  - MINIO_ENDPOINT=http://minio:9000
  - MINIO_ACCESS_KEY=minioadmin
  - MINIO_SECRET_KEY=minioadmin
```

Эти переменные можно использовать в Python коде:

```python
import os
import boto3

s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('MINIO_ENDPOINT'),
    aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('MINIO_SECRET_KEY')
)
```

## Изменение credentials

### Через docker-compose.yml

Измените переменные окружения в `docker-compose.yml`:

```yaml
environment:
  MINIO_ROOT_USER: your_username
  MINIO_ROOT_PASSWORD: your_password
```

### Через .env файл

Создайте файл `.env`:

```env
MINIO_ROOT_USER=your_username
MINIO_ROOT_PASSWORD=your_password
```

И обновите docker-compose.yml:

```yaml
environment:
  MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minioadmin}
  MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minioadmin}
```

## Устранение проблем

### MinIO не запускается

```bash
# Проверка логов
docker-compose logs minio

# Проверка портов
netstat -tuln | grep 9000
netstat -tuln | grep 9001

# Пересоздание контейнера
docker-compose down
docker-compose up -d minio
```

### Ошибки подключения DVC к MinIO

```bash
# Проверка доступности MinIO
curl http://localhost:9000/minio/health/live

# Проверка конфигурации DVC
dvc remote show minio

# Проверка bucket
curl http://minioadmin:minioadmin@localhost:9000/engineering-practices-ml
```

### Очистка данных MinIO

```bash
# Остановка и удаление volumes
docker-compose down -v

# Запуск заново
docker-compose up -d minio
```

## Миграция с local на MinIO

Если у вас уже есть данные в local storage:

```bash
# 1. Отправьте данные в MinIO
dvc push --remote minio

# 2. Переключите default remote
dvc remote default minio

# 3. Проверьте
dvc status
```

## Сравнение с AWS S3

MinIO полностью совместим с S3 API, поэтому для перехода на AWS S3 достаточно изменить:

```bash
dvc remote modify minio endpointurl https://s3.amazonaws.com
dvc remote modify minio url s3://your-bucket-name/dvc
dvc remote modify minio --local access_key_id YOUR_AWS_ACCESS_KEY
dvc remote modify minio --local secret_access_key YOUR_AWS_SECRET_KEY
```
