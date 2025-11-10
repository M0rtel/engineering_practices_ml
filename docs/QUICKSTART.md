# Быстрый старт

## Автоматическая настройка (рекомендуется)

```bash
# Запустить скрипт автоматической настройки
./scripts/setup.sh
```

## Ручная настройка

### 1. Установка Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Установка зависимостей

```bash
# Через Poetry (рекомендуется)
poetry install

# Или через pip
pip install -r requirements.txt
```

### 3. Активация виртуального окружения

```bash
poetry shell
```

### 4. Настройка pre-commit hooks

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

### 5. Проверка установки

```bash
# Форматирование
make format

# Линтинг
make lint

# Тесты
make test
```

## Использование Docker

```bash
# Сборка образа
docker build -t engineering-practices-ml .

# Запуск контейнера
docker run -it engineering-practices-ml

# Или через docker-compose
docker-compose up
```

## Полезные команды

```bash
# Показать все доступные команды
make help

# Форматировать код
make format

# Запустить линтеры
make lint

# Запустить тесты
make test

# Очистить временные файлы
make clean
```
