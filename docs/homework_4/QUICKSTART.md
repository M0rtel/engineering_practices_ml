## Быстрый старт: ДЗ 4 — DVC Pipelines и Pydantic конфигурации

Этот `QUICKSTART.md` показывает, как запустить **ML-пайплайн из ДЗ 4**.

### 1. Базовая подготовка

```bash
git clone https://github.com/M0rtel/engineering_practices_ml.git
cd engineering_practices_ml

uv venv
source .venv/bin/activate

uv sync --all-extras
```

Убедитесь, что:

- данные и DVC настроены (см. `docs/homework_2/QUICKSTART.md`),
- конфигурация обучения есть в `config/train_params.yaml`.

### 2. Проверка конфигурации (Pydantic)

Pydantic-модели описаны в `src/data_science_project/config_models.py` и используются во всех скриптах пайплайна.

Быстрая проверка корректности конфигурации:

```bash
cat config/train_params.yaml
```

При запуске стадий пайплайна ошибки в конфиге (типы, диапазоны) будут отловлены автоматически.

### 3. Запуск стадий DVC-пайплайна

Полный пайплайн описан в `dvc.yaml` и включает:

1. `prepare_data`
2. `validate_data`
3. `train_model`
4. `evaluate_model`
5. `monitor_pipeline`

Запуск всех стадий:

```bash
dvc repro
```

Запуск отдельных стадий:

```bash
dvc repro prepare_data
dvc repro validate_data
dvc repro train_model
dvc repro evaluate_model
dvc repro monitor_pipeline
```

Просмотр графа:

```bash
dvc dag
```

### 4. Изменение параметров через DVC

Параметры пайплайна хранятся в `params.yaml`. Можно:

- отредактировать файл вручную;
- или использовать утилиту для изменения параметров (если она включена в текущую версию проекта).

После изменения параметров:

```bash
dvc repro
```

DVC автоматически пересчитает только необходимые стадии.

### 5. Мониторинг выполнения пайплайна

Модуль `src/data_science_project/pipeline_monitor.py`:

- логирует статусы стадий,
- измеряет время,
- сохраняет отчёт в JSON,
- печатает краткую сводку.

Отчёты и метрики:

- `reports/metrics/`
- `reports/plots/`
- `reports/monitoring/` (если используется).

### 6. Где смотреть детали по ДЗ 4

- Подробное описание пайплайна и конфигураций: `docs/homework_4/REPORT.md`
- Скриншоты: `docs/homework_4/screenshots/`
