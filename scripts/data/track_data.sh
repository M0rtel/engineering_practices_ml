#!/bin/bash
# Скрипт для добавления данных в DVC

set -e

DATA_FILE=${1:-"data/raw/WineQT.csv"}

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ Файл $DATA_FILE не найден"
    exit 1
fi

echo "📊 Добавление $DATA_FILE в DVC..."

# Добавляем файл в DVC (используем poetry run если доступно)
if command -v poetry &> /dev/null; then
    poetry run dvc add "$DATA_FILE"
else
    dvc add "$DATA_FILE"
fi

echo "✅ Файл $DATA_FILE добавлен в DVC"
echo ""
echo "Для коммита изменений:"
echo "  git add $DATA_FILE.dvc .gitignore"
echo "  git commit -m 'data: add $DATA_FILE'"
