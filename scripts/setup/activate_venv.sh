#!/bin/bash
# Скрипт для активации виртуального окружения

# Определяем путь к скрипту активации в зависимости от ОС
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT=".venv/Scripts/activate"
else
    ACTIVATE_SCRIPT=".venv/bin/activate"
fi

# Проверяем существование виртуального окружения
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo ""
    echo "Создайте виртуальное окружение:"
    echo "  uv venv"
    echo ""
    echo "Или запустите полную настройку:"
    echo "  ./scripts/setup/setup.sh"
    exit 1
fi

# Активация окружения
echo "✅ Активирую виртуальное окружение..."
source "$ACTIVATE_SCRIPT"

echo ""
echo "✅ Виртуальное окружение активировано!"
echo ""
echo "Проверка:"
python --version
which python
echo ""
echo "Для деактивации выполните: deactivate"
