#!/bin/bash
# Скрипт для настройки ClearML

set -e

echo "🚀 Настройка ClearML..."

# Проверка наличия UV
if ! command -v uv &> /dev/null; then
    echo "❌ UV не установлен. Устанавливаю..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Установка зависимостей
echo "📦 Установка ClearML..."
uv sync

# Инициализация ClearML
echo "🔧 Инициализация ClearML..."
echo ""
echo "Для настройки ClearML выполните:"
echo "  uv run clearml-init"
echo ""
echo "Или используйте переменные окружения:"
echo "  export CLEARML_API_HOST=http://localhost:8008"
echo "  export CLEARML_WEB_HOST=http://localhost:8080"
echo "  export CLEARML_API_ACCESS_KEY=<your-access-key>"
echo "  export CLEARML_API_SECRET_KEY=<your-secret-key>"
echo ""
echo "Для запуска ClearML Server:"
echo "  docker compose up -d clearml-server"
echo ""
echo "ClearML Web UI будет доступен по адресу: http://localhost:8080"
