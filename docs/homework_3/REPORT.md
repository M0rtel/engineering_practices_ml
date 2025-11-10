# Отчет о настройке системы трекинга экспериментов с DVC

## Введение

Настроена система трекинга экспериментов с использованием DVC Experiments. Система позволяет отслеживать параметры, метрики и артефакты экспериментов, сравнивать результаты и фильтровать по различным критериям.

## 1. Настройка выбранного инструмента (4 балла)

### 1.1. Установка и настройка DVC

DVC уже установлен и настроен (см. ДЗ 2). Для трекинга экспериментов используется встроенная функциональность DVC Experiments.

**Проверка версии:**
```bash
dvc --version
```

**Скриншот:** Версия DVC и проверка настроек
*(Здесь должен быть скриншот вывода `dvc --version` и `dvc remote list`)*

### 1.2. Настройка базы данных/облачного хранилища

Для хранения артефактов экспериментов используется remote storage, настроенное в ДЗ 2:
- **Local storage:** `storage/local` - для локальной разработки
- **MinIO:** S3-совместимое хранилище через docker-compose
- **AWS S3:** для production (требует credentials)

Эксперименты используют существующую конфигурацию DVC remote storage.

**Скриншот:** Конфигурация remote storage
*(Здесь должен быть скриншот `.dvc/config`)*

### 1.3. Создание проекта и экспериментов

Создана структура для экспериментов:

```
experiments/              # Директория для экспериментов
config/experiments/       # Конфигурации экспериментов
reports/experiments/      # Параметры экспериментов
reports/metrics/          # Метрики экспериментов
```

**Генерация конфигураций:**
```bash
python scripts/experiments/generate_experiments.py
```

Создано 26 конфигураций экспериментов с разными алгоритмами и параметрами.

**Скриншот:** Структура экспериментов
*(Здесь должен быть скриншот директории `config/experiments/` с файлами)*

### 1.4. Настройка аутентификации и доступа

Аутентификация настроена через DVC remote storage (см. ДЗ 2):
- **MinIO:** credentials настраиваются через `.dvc/config.local`
- **Local storage:** не требует аутентификации
- **AWS S3:** требует credentials через переменные окружения или `.dvc/config.local`

**Скриншот:** Настройка аутентификации
*(Здесь должен быть скриншот настройки DVC remote или MinIO Console)*

## 2. Проведение экспериментов (4 балла)

### 2.1. Проведение 15+ экспериментов

Создано 26 экспериментов с разными алгоритмами:

- **Linear models:** Linear, Ridge (3 варианта), Lasso (2 варианта), ElasticNet
- **KNN:** 3 варианта (n_neighbors: 5, 10, 20)
- **SVR:** 3 варианта (разные C и kernel)
- **Decision Tree:** 3 варианта (max_depth: 5, 10, 20)
- **Random Forest:** 5 вариантов (разные n_estimators и max_depth)
- **AdaBoost:** 2 варианта
- **Gradient Boosting:** 3 варианта

**Запуск всех экспериментов:**
```bash
python scripts/experiments/run_all_experiments.py
```

**Скриншот:** Результаты запуска экспериментов
*(Здесь должен быть скриншот вывода `run_all_experiments.py`)*

### 2.2. Логирование метрик, параметров и артефактов

**Логирование через DVC:**
- Параметры сохраняются в `reports/experiments/{exp_id}_params.json`
- Метрики сохраняются в `reports/metrics/{exp_id}_metrics.json`
- Модели сохраняются в `models/{exp_id}_model.pkl` и версионируются через DVC

**Python API:**
```python
from src.data_science_project import experiment_tracker

tracker = experiment_tracker.DVCExperimentTracker()
tracker.log_params("exp_001", {"alpha": 1.0})
tracker.log_metrics("exp_001", {"test_r2": 0.85})
tracker.log_artifact("exp_001", "models/model.pkl")
```

**Скриншот:** Пример логирования метрик и параметров
*(Здесь должен быть скриншот содержимого JSON файлов с метриками и параметрами)*

### 2.3. Система сравнения экспериментов

**Сравнение через скрипт:**
```bash
python scripts/experiments/compare_experiments.py --compare exp_001_linear exp_002_ridge_1.0
```

**Python API:**
```python
comparison = tracker.compare_experiments("exp_001", "exp_002")
```

**DVC команды:**
```bash
dvc metrics diff
dvc params diff
dvc exp diff exp1 exp2
```

**Скриншот:** Результаты сравнения экспериментов
*(Здесь должен быть скриншот вывода `compare_experiments.py --compare`)*

### 2.4. Фильтрация и поиск экспериментов

**Фильтрация:**
```bash
# По модели
python scripts/experiments/compare_experiments.py --filter-model rf

# По метрикам
python scripts/experiments/compare_experiments.py --min-r2 0.5 --max-rmse 0.8
```

**Поиск:**
```bash
python scripts/experiments/compare_experiments.py --search ridge
```

**Экспорт в CSV:**
```bash
python scripts/experiments/compare_experiments.py --export experiments.csv
```

**Скриншот:** Результаты фильтрации и поиска
*(Здесь должен быть скриншот вывода команд фильтрации и CSV файла)*

## 3. Интеграция с кодом (2 балла)

### 3.1. Интеграция в Python код

Создан модуль `src/data_science_project/experiment_tracker.py` с классом `DVCExperimentTracker`:

```python
from src.data_science_project import experiment_tracker

tracker = experiment_tracker.DVCExperimentTracker()
tracker.log_params("exp_001", params)
tracker.log_metrics("exp_001", metrics)
```

**Скриншот:** Пример использования Python API
*(Здесь должен быть скриншот кода с использованием трекера)*

### 3.2. Декораторы для автоматического логирования

Создан декоратор `@track_experiment`:

```python
from src.data_science_project.experiment_tracker import track_experiment

@track_experiment(experiment_id="exp_001")
def train_model(**params):
    # Код обучения
    return {"test_r2": 0.85, "test_rmse": 0.5}
```

**Скриншот:** Пример использования декоратора
*(Здесь должен быть скриншот кода с декоратором)*

### 3.3. Контекстные менеджеры

Создан контекстный менеджер `experiment()`:

```python
from src.data_science_project.experiment_tracker import experiment

with experiment("exp_001", params={"alpha": 1.0}) as tracker:
    # Код эксперимента
    tracker.log_metrics("exp_001", metrics)
```

**Скриншот:** Пример использования контекстного менеджера
*(Здесь должен быть скриншот кода с контекстным менеджером)*

### 3.4. Утилиты для работы с экспериментами

Созданы утилиты:
- `DVCExperimentTracker` - основной класс трекера
- `track_experiment()` - декоратор
- `experiment()` - контекстный менеджер
- `run_dvc_experiment()` - запуск через DVC
- `list_dvc_experiments()` - список экспериментов
- `compare_dvc_experiments()` - сравнение через DVC

**Скриншот:** Структура модуля experiment_tracker
*(Здесь должен быть скриншот структуры файла experiment_tracker.py)*

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

### 4.3. Скриншоты результатов

В отчете предусмотрены места для скриншотов:
1. Версия DVC и проверка настроек
2. Конфигурация remote storage
3. Структура экспериментов
4. Настройка аутентификации
5. Результаты запуска экспериментов
6. Пример логирования метрик и параметров
7. Результаты сравнения экспериментов
8. Результаты фильтрации и поиска
9. Пример использования Python API
10. Пример использования декоратора
11. Пример использования контекстного менеджера
12. Структура модуля experiment_tracker

### 4.4. Сохранение в Git репозитории

Отчет сохранен в `docs/homework_3/REPORT.md` и включен в Git репозиторий.

**Скриншот:** Отчет в Git репозитории
*(Здесь должен быть скриншот файла REPORT.md в GitHub)*

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
