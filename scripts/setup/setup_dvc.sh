#!/bin/bash
# Скрипт для настройки DVC

set -e

echo "🔧 Настройка DVC..."

# Проверка наличия DVC
if ! command -v dvc &> /dev/null; then
    echo "❌ DVC не установлен. Устанавливаю через Poetry..."
    poetry install
fi

# Инициализация DVC (если еще не инициализирован)
if [ ! -d ".dvc" ] || [ ! -f ".dvc/config" ]; then
    echo "📦 Инициализация DVC..."
    dvc init --no-scm
fi

# Настройка remote storage
echo "💾 Настройка remote storage..."

# Local storage
if ! dvc remote list | grep -q "local"; then
    echo "  → Настройка local storage..."
    dvc remote add -d local storage/local || echo "  → Local storage уже настроен"
fi

# S3 storage (опционально, требует настройки credentials)
if ! dvc remote list | grep -q "s3"; then
    echo "  → Настройка S3 storage (требует credentials)..."
    echo "  → Для настройки S3 скопируйте .dvc/config.local.example в .dvc/config.local"
    echo "  → и заполните AWS credentials"
    dvc remote add s3 s3://engineering-practices-ml/dvc || echo "  → S3 storage уже настроен"
fi

echo "✅ DVC настроен!"
echo ""
echo "Для работы с данными:"
echo "  dvc add data/raw/WineQT.csv"
echo ""
echo "Для работы с моделями:"
echo "  dvc add models/model.pkl"
echo ""
echo "Для загрузки данных:"
echo "  dvc pull"
