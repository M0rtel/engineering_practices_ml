## Быстрый старт: ДЗ 6 — Документация и GitHub Pages

Этот `QUICKSTART.md` описывает, как воспроизвести **документацию и публикацию на GitHub Pages из ДЗ 6**.

### 1. Базовая подготовка

```bash
git clone https://github.com/M0rtel/engineering_practices_ml.git
cd engineering_practices_ml

uv venv
source .venv/bin/activate

uv sync --all-extras
```

Убедитесь, что у вас настроен доступ к GitHub (SSH или HTTPS) и есть права на репозиторий `M0rtel/engineering_practices_ml`.

### 2. Локальная сборка документации MkDocs

Конфиг документации: `mkdocs.yml`
Исходники: каталог `docs/`

Соберите документацию локально:

```bash
mkdocs build
```

Для локального просмотра:

```bash
mkdocs serve
```

Откройте в браузере:

- `http://127.0.0.1:8000/`

Убедитесь, что:
- главная страница открывается,
- есть разделы Quick Start, Deployment, отчёты по ДЗ, отчёты об экспериментах.

### 3. Настройка GitHub Pages

1. Зайдите в настройки репозитория на GitHub: **Settings → Pages**
2. В разделе **Source** выберите:
   - **Source**: `GitHub Actions`
3. Сохраните настройки.

После этого GitHub Pages будет использовать workflow из `.github/workflows/docs.yml`.

### 4. Проверка workflow публикации документации

Workflow: `.github/workflows/docs.yml`

Триггеры:
- push в `main`,
- изменение файлов в `docs/` или `mkdocs.yml`,
- ручной запуск через `workflow_dispatch`.

Для проверки можно сделать небольшой коммит в документацию и запушить в `main`:

```bash
git add docs/index.md
git commit -m "docs: test docs workflow"
git push origin main
```

Затем:
- откройте вкладку **Actions** в GitHub,
- найдите workflow `Documentation / docs`,
- убедитесь, что все шаги прошли успешно.

### 5. Доступ к опубликованной документации

После успешного workflow GitHub Pages будет доступен по адресу:

- `https://M0rtel.github.io/engineering_practices_ml/`

Проверьте:
- открывается главная страница,
- работают ссылки на отчёты по ДЗ,
- отображаются отчёты об экспериментах и графики.

### 6. Где смотреть детали по ДЗ 6

- Описание устройства документации и GitHub Pages: `docs/homework_6/REPORT.md`
- Скриншоты: `docs/homework_6/screenshots/`
