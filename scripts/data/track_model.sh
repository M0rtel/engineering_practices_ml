#!/bin/bash
# Скрипт для добавления модели в DVC с метаданными

set -e

MODEL_FILE=${1:-"models/model.pkl"}
METRICS_FILE=${2:-"reports/metrics.json"}

if [ ! -f "$MODEL_FILE" ]; then
    echo "❌ Файл модели $MODEL_FILE не найден"
    exit 1
fi

echo "🤖 Добавление модели $MODEL_FILE в DVC..."

# Добавляем модель в DVC
dvc add "$MODEL_FILE"

# Если есть файл с метриками, добавляем его тоже
if [ -f "$METRICS_FILE" ]; then
    echo "📈 Добавление метрик $METRICS_FILE в DVC..."
    dvc add "$METRICS_FILE"
fi

# Создаем файл метаданных для модели
METADATA_FILE="${MODEL_FILE}.meta"
cat > "$METADATA_FILE" << EOF
{
    "model_name": "$(basename $MODEL_FILE)",
    "created_at": "$(date -Iseconds)",
    "version": "$(git describe --tags --always 2>/dev/null || echo 'dev')",
    "metrics_file": "$METRICS_FILE",
    "description": "ML model trained on WineQT dataset"
}
EOF

echo "✅ Модель $MODEL_FILE добавлена в DVC"
echo "✅ Метаданные сохранены в $METADATA_FILE"
echo ""
echo "Для коммита изменений:"
echo "  git add $MODEL_FILE.dvc $METADATA_FILE .gitignore"
echo "  git commit -m 'model: add $MODEL_FILE'"
