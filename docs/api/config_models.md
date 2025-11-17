# API Reference: Config Models

Модуль `src.data_science_project.config_models` предоставляет Pydantic модели для валидации конфигураций ML пайплайна.

## Модели

### DataConfig

Конфигурация данных.

**Поля:**
- `raw_data_path` (str): Путь к исходным данным
- `processed_data_path` (str): Путь к обработанным данным
- `target_column` (str): Название целевой переменной
- `test_size` (float): Размер тестовой выборки (0.0-1.0)
- `random_state` (int): Seed для воспроизводимости

**Пример:**
```python
from src.data_science_project.config_models import DataConfig

data_config = DataConfig(
    raw_data_path="data/raw/WineQT.csv",
    processed_data_path="data/processed",
    target_column="quality",
    test_size=0.2,
    random_state=42
)
```

### ModelConfig

Конфигурация модели.

**Поля:**
- `model_type` (str): Тип модели (linear, ridge, lasso, rf, gb, etc.)
- `params` (dict): Параметры модели

**Пример:**
```python
from src.data_science_project.config_models import ModelConfig

model_config = ModelConfig(
    model_type="rf",
    params={
        "n_estimators": 100,
        "max_depth": 10
    }
)
```

### TrainingConfig

Конфигурация обучения.

**Поля:**
- `data` (DataConfig): Конфигурация данных
- `model` (ModelConfig): Конфигурация модели
- `enable_validation` (bool): Включить валидацию

**Пример:**
```python
from src.data_science_project.config_models import TrainingConfig

training_config = TrainingConfig(
    data=data_config,
    model=model_config,
    enable_validation=True
)
```

### PipelineConfig

Конфигурация пайплайна.

**Поля:**
- `config_file` (str): Путь к конфигурационному файлу
- `stages` (list[str]): Список стадий для выполнения

**Пример:**
```python
from src.data_science_project.config_models import PipelineConfig

pipeline_config = PipelineConfig(
    config_file="config/train_params.yaml",
    stages=["prepare_data", "train_model", "evaluate_model"]
)
```

## Загрузка из файла

```python
from src.data_science_project.config_models import TrainingConfig
from pathlib import Path
import yaml

# Загрузка из YAML
with open("config/train_params.yaml") as f:
    config_data = yaml.safe_load(f)
    config = TrainingConfig(**config_data)
```

## Валидация

Pydantic автоматически валидирует данные:

```python
from src.data_science_project.config_models import ModelConfig

# Это вызовет ValidationError
try:
    model_config = ModelConfig(
        model_type="invalid_model",
        params={}
    )
except ValidationError as e:
    print(f"Ошибка валидации: {e}")
```

## Поддерживаемые типы моделей

- `linear` - Linear Regression
- `ridge` - Ridge Regression
- `lasso` - Lasso Regression
- `elasticnet` - ElasticNet Regression
- `knn` - K-Nearest Neighbors
- `svr` - Support Vector Regression
- `dt` - Decision Tree
- `rf` - Random Forest
- `ada` - AdaBoost
- `gb` - Gradient Boosting
