# API Reference: Experiment Tracker

Модуль `src.data_science_project.experiment_tracker` предоставляет функциональность для трекинга экспериментов с использованием DVC.

## Классы

### DVCExperimentTracker

Класс для трекинга экспериментов с DVC.

#### Методы

##### `__init__(self, experiment_id: str)`

Инициализация трекера для эксперимента.

**Параметры:**
- `experiment_id` (str): Уникальный идентификатор эксперимента

**Пример:**
```python
from src.data_science_project.experiment_tracker import DVCExperimentTracker

tracker = DVCExperimentTracker("exp_001")
```

##### `log_params(self, experiment_id: str, params: dict[str, Any]) -> None`

Логирование параметров эксперимента.

**Параметры:**
- `experiment_id` (str): Идентификатор эксперимента
- `params` (dict): Словарь параметров

**Пример:**
```python
tracker.log_params("exp_001", {
    "model_name": "rf",
    "n_estimators": 100,
    "max_depth": 10
})
```

##### `log_metrics(self, experiment_id: str, metrics: dict[str, float]) -> None`

Логирование метрик эксперимента.

**Параметры:**
- `experiment_id` (str): Идентификатор эксперимента
- `metrics` (dict): Словарь метрик

**Пример:**
```python
tracker.log_metrics("exp_001", {
    "test_r2": 0.85,
    "test_rmse": 0.5,
    "test_mae": 0.4
})
```

##### `get_experiment(self, experiment_id: str) -> dict[str, Any] | None`

Получить данные эксперимента.

**Параметры:**
- `experiment_id` (str): Идентификатор эксперимента

**Возвращает:**
- `dict | None`: Данные эксперимента или None, если не найден

##### `list_experiments(self) -> list[str]`

Получить список всех экспериментов.

**Возвращает:**
- `list[str]`: Список идентификаторов экспериментов

##### `compare_experiments(self, exp_id1: str, exp_id2: str) -> dict[str, Any]`

Сравнить два эксперимента.

**Параметры:**
- `exp_id1` (str): Идентификатор первого эксперимента
- `exp_id2` (str): Идентификатор второго эксперимента

**Возвращает:**
- `dict`: Словарь с различиями между экспериментами

## Декораторы

### `@track_experiment`

Декоратор для автоматического трекинга экспериментов.

**Параметры:**
- `experiment_id` (str): Идентификатор эксперимента

**Пример:**
```python
from src.data_science_project.experiment_tracker import track_experiment

@track_experiment(experiment_id="exp_001")
def train_model(**params):
    # Код обучения
    return {"test_r2": 0.85}
```

## Контекстные менеджеры

### `experiment(experiment_id: str, params: dict[str, Any] | None = None)`

Контекстный менеджер для трекинга экспериментов.

**Параметры:**
- `experiment_id` (str): Идентификатор эксперимента
- `params` (dict, optional): Параметры эксперимента

**Пример:**
```python
from src.data_science_project.experiment_tracker import experiment

with experiment("exp_001", params={"alpha": 1.0}) as tracker:
    # Код эксперимента
    tracker.log_metrics("exp_001", {"test_r2": 0.85})
```

## Примеры использования

### Базовое использование

```python
from src.data_science_project.experiment_tracker import DVCExperimentTracker

# Создание трекера
tracker = DVCExperimentTracker("exp_001")

# Логирование параметров
tracker.log_params("exp_001", {
    "model_name": "rf",
    "n_estimators": 100
})

# Логирование метрик
tracker.log_metrics("exp_001", {
    "test_r2": 0.85,
    "test_rmse": 0.5
})
```

### Использование декоратора

```python
from src.data_science_project.experiment_tracker import track_experiment

@track_experiment(experiment_id="exp_001")
def train_and_evaluate(model_name: str, **params):
    # Обучение модели
    model = train_model(model_name, **params)

    # Оценка
    metrics = evaluate_model(model)

    return metrics
```

### Использование контекстного менеджера

```python
from src.data_science_project.experiment_tracker import experiment

with experiment("exp_001", params={"alpha": 1.0}) as tracker:
    # Обучение модели
    model = train_model(alpha=1.0)

    # Оценка
    metrics = evaluate_model(model)

    # Логирование метрик
    tracker.log_metrics("exp_001", metrics)
```
