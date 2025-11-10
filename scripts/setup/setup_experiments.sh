#!/bin/bash
# Скрипт для настройки системы трекинга экспериментов

set -e

echo "🔧 Настройка системы трекинга экспериментов..."

# Генерируем конфигурации экспериментов
echo "📝 Генерация конфигураций экспериментов..."
python scripts/experiments/generate_experiments.py

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p experiments
mkdir -p reports/experiments
mkdir -p reports/plots

echo "✅ Система трекинга экспериментов настроена!"
echo ""
echo "Для запуска всех экспериментов:"
echo "  python scripts/experiments/run_all_experiments.py"
echo ""
echo "Для сравнения экспериментов:"
echo "  python scripts/experiments/compare_experiments.py --compare exp_001_linear exp_002_ridge_1.0"
echo ""
echo "Для фильтрации:"
echo "  python scripts/experiments/compare_experiments.py --filter-model rf --min-r2 0.5"
