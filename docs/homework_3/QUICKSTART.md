## Быстрый старт: ДЗ 3 — DVC Experiments и трекинг экспериментов

Этот `QUICKSTART.md` описывает, как воспроизвести **систему экспериментов из ДЗ 3**.

### 1. Базовая подготовка

```bash
git clone https://github.com/M0rtel/engineering_practices_ml.git
cd engineering_practices_ml

uv venv
source .venv/bin/activate

uv sync --all-extras
```

Убедитесь, что DVC уже настроен и данные добавлены (см. `docs/homework_2/QUICKSTART.md`).

### 2. Структура для экспериментов

В проекте уже подготовлены директории:

- `config/experiments/` — конфигурации экспериментов
- `reports/experiments/` — параметры/результаты экспериментов
- `reports/metrics/` — метрики моделей

Проверьте их наличие:

```bash
ls config/experiments || echo "Каталог с конфигами экспериментов может быть пустым"
ls reports/experiments
```

### 3. Запуск экспериментов через DVC Experiments

Пример запуска одного эксперимента (через DVC):

```bash
dvc exp run
```

Если в текущей версии репозитория экспериментальные конфиги не активны, вы всё равно можете:

- изменить параметры в `params.yaml` (например, `model_type`)
- запустить `dvc repro` и считать это отдельным экспериментом

### 4. Список и сравнение экспериментов

```bash
# Список экспериментов
dvc exp list

# Разница по метрикам
dvc metrics diff

# Разница по параметрам
dvc params diff
```

Дополнительно можно использовать Python API из модуля `src/data_science_project/experiment_tracker.py` (описан в `docs/homework_3/REPORT.md`).

### 5. Отчёты и визуализация экспериментов

Сводные результаты и скриншоты:

- Отчёт: `docs/homework_3/REPORT.md`
- Скриншоты: `docs/homework_3/screenshots/`

Там показаны:
- примеры запусков большого числа экспериментов,
- сравнение метрик,
- фильтрация и поиск по экспериментам.
