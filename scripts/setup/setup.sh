#!/bin/bash
# Скрипт для автоматической настройки проекта

set -e

echo "🚀 Настройка проекта Engineering Practices ML..."

# Проверка наличия UV
if ! command -v uv &> /dev/null; then
    echo "❌ UV не установлен. Устанавливаю..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
if [ ! -d ".venv" ]; then
    uv venv
    echo "✅ Виртуальное окружение создано в .venv/"
else
    echo "ℹ️  Виртуальное окружение уже существует"
fi

# Определяем способ активации в зависимости от ОС
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT=".venv/Scripts/activate"
    PYTHON_CMD=".venv/Scripts/python"
else
    ACTIVATE_SCRIPT=".venv/bin/activate"
    PYTHON_CMD=".venv/bin/python"
fi

# Активация виртуального окружения для текущего скрипта
source "$ACTIVATE_SCRIPT"

# Установка зависимостей (включая dev зависимости)
echo "📦 Установка зависимостей..."
uv sync --all-extras

# Настройка pre-commit hooks
echo "🔧 Настройка pre-commit hooks..."
"$PYTHON_CMD" -m pre_commit install

# Проверка версии Python
echo "🐍 Проверка установки..."
"$PYTHON_CMD" --version
uv --version

echo ""
echo "✅ Настройка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo ""
echo "1. Активируйте виртуальное окружение:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   .venv\\Scripts\\activate"
else
    echo "   source .venv/bin/activate"
fi
echo ""
echo "2. После активации все команды можно выполнять напрямую:"
echo "   python script.py"
echo "   dvc repro"
echo "   pytest"
echo ""
echo "3. Для запуска pre-commit на всех файлах:"
echo "   pre-commit run --all-files"
echo ""
echo "4. Для деактивации окружения:"
echo "   deactivate"
