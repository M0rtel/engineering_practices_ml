# Git Workflow для проекта

## Структура веток

Проект использует Git Flow модель с следующими ветками:

- **main** - основная ветка с рабочим, стабильным кодом
- **develop** - ветка разработки, где собираются все изменения
- **feature/*** - ветки для разработки новых функций
- **bugfix/*** - ветки для исправления ошибок
- **hotfix/*** - ветки для срочных исправлений в production

## Рабочий процесс

### Создание новой функции

```bash
# Переключиться на develop
git checkout develop
git pull origin develop

# Создать ветку для новой функции
git checkout -b feature/new-feature-name

# Внести изменения и закоммитить
git add .
git commit -m "feat: описание новой функции"

# Отправить ветку в репозиторий
git push origin feature/new-feature-name

# Создать Pull Request в GitHub
```

### Исправление ошибки

```bash
# Переключиться на develop
git checkout develop
git pull origin develop

# Создать ветку для исправления
git checkout -b bugfix/bug-description

# Внести исправления и закоммитить
git add .
git commit -m "fix: описание исправления"

# Отправить ветку
git push origin bugfix/bug-description
```

### Срочное исправление (hotfix)

```bash
# Переключиться на main
git checkout main
git pull origin main

# Создать ветку hotfix
git checkout -b hotfix/urgent-fix

# Внести исправления
git add .
git commit -m "hotfix: описание срочного исправления"

# Отправить и создать MR в main и develop
git push origin hotfix/urgent-fix
```

## Правила коммитов

Используем Conventional Commits:

- `feat:` - новая функция
- `fix:` - исправление ошибки
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, конфигурации

Примеры:
```
feat: добавить предобработку данных для модели
fix: исправить ошибку в расчете метрик
docs: обновить README с инструкциями по установке
```

## Pre-commit hooks

Все коммиты автоматически проверяются через pre-commit hooks:
- Форматирование кода (Black, isort, Ruff)
- Линтинг (Ruff, MyPy)
- Проверка безопасности (Bandit)

Если проверки не проходят, коммит будет отклонен.
