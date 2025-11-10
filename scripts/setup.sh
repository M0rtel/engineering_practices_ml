#!/bin/bash
# Скрипт для автоматической настройки проекта

set -e

echo "🚀 Настройка проекта Engineering Practices ML..."

# Проверка наличия Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry не установлен. Устанавливаю..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Установка зависимостей
echo "📦 Установка зависимостей..."
poetry install

# Настройка pre-commit hooks
echo "🔧 Настройка pre-commit hooks..."
poetry run pre-commit install

# Создание виртуального окружения (если еще не создано)
echo "🐍 Создание виртуального окружения..."
poetry env info

echo "✅ Настройка завершена!"
echo ""
echo "Для активации виртуального окружения выполните:"
echo "  poetry shell"
echo ""
echo "Для запуска pre-commit на всех файлах:"
echo "  poetry run pre-commit run --all-files"
