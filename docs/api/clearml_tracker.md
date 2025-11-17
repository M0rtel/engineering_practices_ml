# API Reference: ClearML Tracker

Модуль `src.data_science_project.clearml_tracker` предоставляет интеграцию с ClearML для трекинга экспериментов и управления моделями.

## Классы

### ClearMLTracker

Класс для трекинга экспериментов с ClearML.

#### Методы

##### `__init__(self, project_name: str, task_name: str, tags: list[str] | None = None)`

Инициализация трекера.

**Параметры:**
- `project_name` (str): Название проекта в ClearML
- `task_name` (str): Название задачи
- `tags` (list[str], optional): Теги для задачи

**Пример:**
```python
from src.data_science_project.clearml_tracker import ClearMLTracker

tracker = ClearMLTracker(
    project_name="Engineering Practices ML",
    task_name="ridge_experiment_001",
    tags=["ridge", "training"]
)
```

##### `log_params(self, params: dict[str, Any]) -> None`

Логирование параметров.

**Параметры:**
- `params` (dict): Словарь параметров

##### `log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None`

Логирование метрик.

**Параметры:**
- `metrics` (dict): Словарь метрик
- `step` (int, optional): Шаг итерации

##### `log_model(self, model_path: str, model_name: str, metadata: dict[str, Any] | None = None) -> None`

Логирование модели.

**Параметры:**
- `model_path` (str): Путь к файлу модели
- `model_name` (str): Название модели
- `metadata` (dict, optional): Метаданные модели

##### `close(self) -> None`

Закрытие задачи.

### ClearMLModelManager

Класс для управления моделями в ClearML.

#### Методы

##### `register_model(self, model_path: str, model_name: str, metadata: dict[str, Any] | None = None) -> str`

Регистрация модели в ClearML.

**Параметры:**
- `model_path` (str): Путь к файлу модели
- `model_name` (str): Название модели
- `metadata` (dict, optional): Метаданные модели

**Возвращает:**
- `str`: ID модели в ClearML

##### `list_models(self, project_name: str | None = None) -> list[dict[str, Any]]`

Получить список моделей.

**Параметры:**
- `project_name` (str, optional): Название проекта

**Возвращает:**
- `list[dict]`: Список моделей

##### `compare_models(self, model_id1: str, model_id2: str) -> dict[str, Any]`

Сравнить две модели.

**Параметры:**
- `model_id1` (str): ID первой модели
- `model_id2` (str): ID второй модели

**Возвращает:**
- `dict`: Сравнение моделей

## Функции

### `create_clearml_pipeline(model_type: str, queue: str = "default") -> None`

Создать и запустить ClearML пайплайн.

**Параметры:**
- `model_type` (str): Тип модели
- `queue` (str): Очередь для выполнения

**Пример:**
```python
from src.data_science_project.clearml_tracker import create_clearml_pipeline

create_clearml_pipeline(model_type="rf", queue="default")
```

## Примеры использования

### Базовое использование

```python
from src.data_science_project.clearml_tracker import ClearMLTracker

# Создание трекера
tracker = ClearMLTracker(
    project_name="Engineering Practices ML",
    task_name="my_experiment",
    tags=["training", "ridge"]
)

# Логирование параметров
tracker.log_params({
    "alpha": 1.0,
    "max_depth": 10
})

# Логирование метрик
tracker.log_metrics({
    "test_r2": 0.85,
    "test_rmse": 0.5
})

# Логирование модели
tracker.log_model(
    model_path="models/model.pkl",
    model_name="wine_quality_model",
    metadata={"version": "1.0.0"}
)

# Закрытие задачи
tracker.close()
```

### Управление моделями

```python
from src.data_science_project.clearml_tracker import ClearMLModelManager

# Создание менеджера моделей
manager = ClearMLModelManager()

# Регистрация модели
model_id = manager.register_model(
    model_path="models/model.pkl",
    model_name="wine_quality_model",
    metadata={"version": "1.0.0", "accuracy": 0.85}
)

# Список моделей
models = manager.list_models(project_name="Engineering Practices ML")
for model in models:
    print(f"Model: {model['name']}, ID: {model['id']}")

# Сравнение моделей
comparison = manager.compare_models(model_id1, model_id2)
```
