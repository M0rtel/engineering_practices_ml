# Отчет о настройке системы трекинга экспериментов с DVC

## Введение

Настроена система трекинга экспериментов с использованием DVC Experiments. Система позволяет отслеживать параметры, метрики и артефакты экспериментов, сравнивать результаты и фильтровать по различным критериям.

> **Примечание:** Для получения пошаговых инструкций по настройке и использованию системы трекинга экспериментов см. [`docs/homework_3/QUICKSTART.md`](QUICKSTART.md) или общий [`docs/QUICKSTART.md`](../QUICKSTART.md) (Шаг 12). Данный отчет описывает **что было настроено**, а не **как это настроить**.

## 1. Настройка выбранного инструмента (4 балла)

### 1.1. Установка и настройка DVC

DVC уже установлен и настроен (см. ДЗ 2). Для трекинга экспериментов используется встроенная функциональность DVC Experiments.

**Примечание:** Пошаговые инструкции по установке и настройке DVC см. в `docs/QUICKSTART.md` (Шаг 5) и `docs/homework_2/REPORT.md`.

### 1.2. Настройка базы данных/облачного хранилища

Для хранения артефактов экспериментов используется remote storage, настроенное в ДЗ 2:
- **Local storage:** `storage/local` - для локальной разработки
- **MinIO:** S3-совместимое хранилище через docker-compose
- **AWS S3:** для production (требует credentials)

Эксперименты используют существующую конфигурацию DVC remote storage.

### 1.3. Создание проекта и экспериментов

Создана структура для экспериментов:
- `config/experiments/` - конфигурации экспериментов (YAML и JSON)
- `reports/experiments/` - параметры экспериментов
- `reports/metrics/` - метрики экспериментов

Создано 26 конфигураций экспериментов с разными алгоритмами и параметрами через скрипт `scripts/experiments/generate_experiments.py`. Эксперименты включают: Linear, Ridge, Lasso, ElasticNet, KNN, SVR, Decision Tree, Random Forest, AdaBoost, Gradient Boosting.

**Примечание:** Пошаговые инструкции по генерации и запуску экспериментов см. в `docs/QUICKSTART.md` (Шаг 12).

### 1.4. Настройка аутентификации и доступа

Аутентификация настроена через DVC remote storage (см. ДЗ 2):
- **MinIO:** credentials настраиваются через `.dvc/config.local`
- **Local storage:** не требует аутентификации
- **AWS S3:** требует credentials через переменные окружения или `.dvc/config.local`

## 2. Проведение экспериментов (4 балла)

### 2.1. Проведение 15+ экспериментов

Создано 26 экспериментов (больше требуемых 15) с разными алгоритмами:
- **Linear models:** Linear, Ridge (3 варианта), Lasso (2 варианта), ElasticNet
- **KNN:** 3 варианта (n_neighbors: 5, 10, 20)
- **SVR:** 3 варианта (разные C и kernel)
- **Decision Tree:** 3 варианта (max_depth: 5, 10, 20)
- **Random Forest:** 5 вариантов (разные n_estimators и max_depth)
- **AdaBoost:** 2 варианта
- **Gradient Boosting:** 3 варианта

Все эксперименты запускаются через скрипт `scripts/experiments/run_all_experiments.py`. Найдено 26 файлов с параметрами экспериментов в `reports/experiments/`.

![img.png](screenshots/experiments.png)

### 2.2. Логирование метрик, параметров и артефактов

Настроено логирование через DVC и Python API:
- Параметры сохраняются в `reports/experiments/{exp_id}_params.json`
- Метрики сохраняются в `reports/metrics/{exp_id}_metrics.json`
- Модели сохраняются в `models/{exp_id}_model.pkl` и версионируются через DVC

Python API реализован в классе `DVCExperimentTracker` с методами `log_params()`, `log_metrics()`, `log_artifact()`.

**Примечание:** Примеры использования Python API см. в `docs/QUICKSTART.md` (Шаг 12.4).

![img.png](screenshots/img7.png)

![img_1.png](screenshots/img_8.png)

![img_2.png](screenshots/img_29.png)

### 2.3. Система сравнения экспериментов

Реализована система сравнения экспериментов:
- Скрипт: `scripts/experiments/compare_experiments.py --compare`
- Python API: `tracker.compare_experiments(exp1, exp2)`
- DVC команды: `dvc metrics diff`, `dvc params diff`, `dvc exp diff`

Сравнение включает параметры и метрики с вычислением разницы.

![img.png](screenshots/compare_experiments.png)

### 2.4. Фильтрация и поиск экспериментов

Реализована система фильтрации и поиска в скрипте `scripts/experiments/compare_experiments.py`:

**Механизм работы:**

1. **Загрузка данных:**
   - Функция `load_all_experiments()` сканирует директории `reports/experiments/` и `reports/metrics/`
   - Объединяет параметры (`*_params.json`) с метриками (`*_metrics.json`) для каждого эксперимента
   - Возвращает список словарей с полными данными экспериментов

2. **Фильтрация по модели** (`--filter-model`):
   - Функция `filter_experiments()` проверяет поле `model_name`
   - Пример: `--filter-model RandomForest` вернёт только эксперименты с Random Forest

3. **Фильтрация по метрикам** (`--min-r2`, `--max-rmse`):
   - `--min-r2`: фильтрует эксперименты с `test_r2 >= указанное_значение`
   - `--max-rmse`: фильтрует эксперименты с `test_rmse <= указанное_значение`
   - Фильтры можно комбинировать (логическое И)
   - Пример: `--min-r2 0.7 --max-rmse 0.6`

4. **Поиск по запросу** (`--search`):
   - Функция `search_experiments()` выполняет поиск без учёта регистра
   - Ищет вхождение запроса в `experiment_id` или `model_name`
   - Пример: `--search forest` найдёт все эксперименты с "forest" в ID или названии модели

5. **Экспорт в CSV** (`--export`):
   - Функция `export_to_dataframe()` создаёт pandas DataFrame
   - Экспортирует все эксперименты с параметрами и метриками в CSV файл
   - Удобно для анализа в Excel или pandas

6. **Список всех экспериментов** (`--list`):
   - Показывает все доступные эксперименты с их основными метриками
   - Формат: `experiment_id: model_name - R²=value, RMSE=value`

**Примеры использования:**
```bash
# Фильтрация по модели
python scripts/experiments/compare_experiments.py --filter-model RandomForest

# Фильтрация по метрикам
python scripts/experiments/compare_experiments.py --min-r2 0.8 --max-rmse 0.5

# Поиск
python scripts/experiments/compare_experiments.py --search forest

# Экспорт
python scripts/experiments/compare_experiments.py --export results.csv

# Список всех
python scripts/experiments/compare_experiments.py --list
```

![img_3.png](screenshots/img_35.png)

## 3. Интеграция с кодом (2 балла)

### 3.1. Интеграция в Python код

Создан модуль `src/data_science_project/experiment_tracker.py` с классом `DVCExperimentTracker`. Класс предоставляет методы для логирования параметров, метрик и артефактов, получения данных эксперимента, списка экспериментов и сравнения.

**Примечание:** Примеры использования Python API см. в `docs/QUICKSTART.md` (Шаг 12.4).

### 3.2. Декораторы для автоматического логирования

Создан декоратор `@track_experiment(experiment_id)`, который автоматически:
- Логирует параметры из kwargs функции
- Логирует метрики из возвращаемого значения
- Генерирует experiment_id автоматически, если не указан

### 3.3. Контекстные менеджеры

Создан контекстный менеджер `experiment(experiment_id, params)`, который автоматически логирует параметры при входе и возвращает трекер для логирования метрик внутри блока.

### 3.4. Утилиты для работы с экспериментами

Созданы утилиты:
- `DVCExperimentTracker` - основной класс трекера
- `track_experiment()` - декоратор
- `experiment()` - контекстный менеджер
- `run_dvc_experiment()` - запуск через DVC
- `list_dvc_experiments()` - список экспериментов
- `compare_dvc_experiments()` - сравнение через DVC

## 4. Отчет о проделанной работе (2 балла)

### 4.1. Отчет в формате Markdown

Отчет создан в `docs/homework_3/REPORT.md` и включает:
- Описание настройки DVC Experiments
- Описание системы экспериментов
- Примеры использования
- Места для скриншотов

### 4.2. Описание настройки инструментов

В отчете описаны:
1. **DVC Experiments** - настройка и использование
2. **Remote Storage** - MinIO и S3
3. **Система экспериментов** - генерация, запуск, сравнение
4. **Python API** - декораторы, контекстные менеджеры, утилиты
5. **Фильтрация и поиск** - инструменты для анализа

### 4.3. Сохранение в Git репозитории

Отчет сохранен в `docs/homework_3/REPORT.md` и включен в Git репозиторий.

## Заключение

Настроена полноценная система трекинга экспериментов:

✅ **DVC Experiments настроен** - для трекинга экспериментов
✅ **Remote storage настроен** - MinIO и S3
✅ **26 экспериментов создано** - с разными алгоритмами и параметрами
✅ **Логирование настроено** - метрики, параметры, артефакты
✅ **Сравнение и фильтрация** - инструменты для анализа
✅ **Python API создан** - декораторы, контекстные менеджеры, утилиты
✅ **Отчет создан** - с описанием всех настроек и местами для скриншотов

Все инструменты настроены, протестированы и готовы к использованию.
