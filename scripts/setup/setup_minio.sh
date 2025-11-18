#!/bin/bash
# Скрипт для настройки DVC с MinIO

set -e

echo "🚀 Настройка DVC с MinIO..."

# Проверка наличия DVC
if ! command -v dvc &> /dev/null; then
    echo "❌ DVC не установлен. Устанавливаю через UV..."
    uv sync
fi

# Запуск MinIO через docker-compose
echo "🐳 Запуск MinIO..."
docker compose up -d minio

# Ждем пока MinIO запустится
echo "⏳ Ожидание запуска MinIO..."
sleep 5

# Проверка доступности MinIO
until curl -f http://localhost:9000/minio/health/live 2>/dev/null; do
    echo "  → Ожидание MinIO..."
    sleep 2
done

echo "✅ MinIO запущен!"
echo ""
echo "MinIO доступен по адресам:"
echo "  API: http://localhost:9000"
echo "  Console: http://localhost:9001"
echo "  Access Key: minioadmin"
echo "  Secret Key: minioadmin"
echo ""

# Инициализация DVC (если еще не инициализирован)
if [ ! -d ".dvc" ] || [ ! -f ".dvc/config" ]; then
    echo "📦 Инициализация DVC..."
    dvc init --no-scm
fi

# Настройка MinIO как remote storage
echo "💾 Настройка MinIO как remote storage..."

# Удаляем старый minio remote, если есть
dvc remote remove minio 2>/dev/null || true

# Добавляем MinIO remote
dvc remote add minio s3://engineering-practices-ml/dvc
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio --local access_key_id minioadmin
dvc remote modify minio --local secret_access_key minioadmin

# Создаем bucket через MinIO client (mc) или через API
echo "📦 Создание bucket в MinIO..."

# Используем MinIO client для создания bucket
docker compose exec -T minio sh -c "
  mc alias set local http://localhost:9000 minioadmin minioadmin && \
  mc mb local/engineering-practices-ml 2>/dev/null || echo 'Bucket уже существует'
" || echo "  → Bucket будет создан при первом использовании"

echo "✅ MinIO настроен как remote storage для DVC!"
echo ""
echo "Для использования MinIO:"
echo "  dvc remote default minio"
echo ""
echo "Для загрузки данных:"
echo "  dvc push --remote minio"
echo ""
echo "Для скачивания данных:"
echo "  dvc pull --remote minio"
