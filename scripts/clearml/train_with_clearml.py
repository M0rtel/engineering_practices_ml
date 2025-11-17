"""Скрипт для обучения модели с трекингом в ClearML."""

import argparse
import json
import os
import pickle  # nosec B403
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sklearn.base import BaseEstimator
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

# Загружаем credentials из конфигурационного файла, если переменные окружения не установлены
if "CLEARML_API_ACCESS_KEY" not in os.environ:
    config_file = Path.home() / ".clearml" / "clearml.conf"
    if config_file.exists():
        # Парсим конфигурационный файл и устанавливаем переменные окружения
        with open(config_file) as f:
            content = f.read()
            # Извлекаем access_key
            access_key_match = re.search(r'"access_key"\s*=\s*"([^"]+)"', content)
            if access_key_match:
                os.environ["CLEARML_API_ACCESS_KEY"] = access_key_match.group(1)
            # Извлекаем secret_key
            secret_key_match = re.search(r'"secret_key"\s*=\s*"([^"]+)"', content)
            if secret_key_match:
                os.environ["CLEARML_API_SECRET_KEY"] = secret_key_match.group(1)
            # Извлекаем api_server host
            api_host_match = re.search(
                r'api_server\s*\{[^}]*host\s*=\s*"([^"]+)"', content, re.DOTALL
            )
            if api_host_match:
                os.environ["CLEARML_API_HOST"] = api_host_match.group(1)
            # Извлекаем web_server host
            web_host_match = re.search(
                r'web_server\s*\{[^}]*host\s*=\s*"([^"]+)"', content, re.DOTALL
            )
            if web_host_match:
                os.environ["CLEARML_WEB_HOST"] = web_host_match.group(1)

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_science_project.clearml_tracker import ClearMLTracker  # noqa: E402
from src.data_science_project.config_models import TrainingConfig  # noqa: E402

# Пути
TRAIN_DATA = Path("data/processed/train.csv")
TEST_DATA = Path("data/processed/test.csv")
MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")

MODELS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)


def get_model(model_type: str, params: dict[str, Any]) -> BaseEstimator:
    """
    Создать модель по типу.

    Args:
        model_type: Тип модели
        params: Параметры модели

    Returns:
        Объект модели scikit-learn
    """
    models = {
        "linear": LinearRegression,
        "ridge": Ridge,
        "lasso": Lasso,
        "elasticnet": ElasticNet,
        "knn": KNeighborsRegressor,
        "svr": SVR,
        "dt": DecisionTreeRegressor,
        "rf": RandomForestRegressor,
        "ada": AdaBoostRegressor,
        "gb": GradientBoostingRegressor,
    }

    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}")

    model = models[model_type](**params)
    if "random_state" in model.get_params() and "random_state" not in params:
        model.set_params(random_state=42)

    return model


def train_with_clearml(
    config_file: Path,
    model_type: str | None = None,
    experiment_name: str | None = None,
) -> None:
    """
    Обучить модель с трекингом в ClearML.

    Args:
        config_file: Путь к файлу конфигурации
        model_type: Тип модели (переопределяет конфигурацию)
        experiment_name: Название эксперимента в ClearML
    """
    # Загружаем конфигурацию
    with open(config_file) as f:
        config_dict = yaml.safe_load(f)

    training_config_dict = {"data": config_dict["data"]}
    if "model" in config_dict:
        training_config_dict["model"] = config_dict["model"]

    training_config = TrainingConfig(**training_config_dict)

    # Определяем тип модели
    if model_type:
        model_type_final = model_type
    elif "model" in config_dict and "model_type" in config_dict["model"]:
        model_type_final = config_dict["model"]["model_type"]
    else:
        model_type_final = "rf"

    # Получаем параметры модели
    if "model" in config_dict and "params" in config_dict["model"]:
        model_params = config_dict["model"]["params"]
    elif "train" in config_dict:
        if model_type_final == "rf":
            model_params = {
                "n_estimators": config_dict["train"].get("n_estimators", 100),
                "max_depth": config_dict["train"].get("max_depth", 10),
                "min_samples_split": config_dict["train"].get("min_samples_split", 2),
                "min_samples_leaf": config_dict["train"].get("min_samples_leaf", 1),
                "random_state": config_dict["train"].get("random_state", 42),
            }
        else:
            model_params = {}
            if config_dict["train"].get("random_state"):
                model_params["random_state"] = config_dict["train"]["random_state"]
    else:
        model_params = {}

    # Инициализируем ClearML трекер
    exp_name = experiment_name or f"train_{model_type_final}"
    tracker = ClearMLTracker(
        project_name="Engineering Practices ML",
        task_name=exp_name,
        tags=[model_type_final, "training"],
    )

    # Логируем параметры
    tracker.log_params(
        {
            "model_type": model_type_final,
            "model_params": model_params,
            "config_file": str(config_file),
        }
    )

    # Загружаем данные
    print("📊 Загрузка данных для обучения...")
    train_df = pd.read_csv(TRAIN_DATA)
    test_df = pd.read_csv(TEST_DATA)

    data_config = training_config.data
    target_col = data_config.target_column
    feature_cols = data_config.feature_columns

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    # Обучение модели
    print(f"🤖 Обучение модели: {model_type_final}...")
    model = get_model(model_type_final, model_params)
    model.fit(X_train, y_train)

    # Предсказания
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Метрики
    train_metrics = {
        "train_mse": float(mean_squared_error(y_train, y_pred_train)),
        "train_rmse": float(mean_squared_error(y_train, y_pred_train) ** 0.5),
        "train_mae": float(mean_absolute_error(y_train, y_pred_train)),
        "train_r2": float(r2_score(y_train, y_pred_train)),
    }

    test_metrics = {
        "test_mse": float(mean_squared_error(y_test, y_pred_test)),
        "test_rmse": float(mean_squared_error(y_test, y_pred_test) ** 0.5),
        "test_mae": float(mean_absolute_error(y_test, y_pred_test)),
        "test_r2": float(r2_score(y_test, y_pred_test)),
    }

    # Логируем метрики в ClearML
    tracker.log_metrics(train_metrics)
    tracker.log_metrics(test_metrics)

    # Сохраняем модель
    model_path = MODELS_DIR / f"{exp_name}_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)  # nosec B301

    # Регистрируем модель в ClearML
    tracker.log_model(
        model_path=model_path,
        model_name=f"{exp_name}_model",
        metadata={
            "model_type": model_type_final,
            "train_metrics": train_metrics,
            "test_metrics": test_metrics,
            "model_params": model_params,
        },
    )

    # Сохраняем метрики
    all_metrics = {
        "model_type": model_type_final,
        **train_metrics,
        **test_metrics,
    }

    metrics_path = REPORTS_DIR / "metrics" / f"{exp_name}_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)

    # Логируем артефакты
    tracker.log_artifact(metrics_path, name="metrics")

    print("✅ Модель обучена и зарегистрирована в ClearML!")
    print(f"  Model: {model_type_final}")
    print(f"  Test R²: {test_metrics['test_r2']:.4f}")
    print(f"  Test RMSE: {test_metrics['test_rmse']:.4f}")
    print(f"  Модель сохранена: {model_path}")
    print(f"  ClearML Task URL: {tracker.get_task_url()}")

    # Закрываем задачу (может быть попытка загрузить артефакты, ошибки не критичны)
    try:
        tracker.close()
    except Exception as e:
        # Игнорируем ошибки при закрытии (обычно это попытки загрузить артефакты на fileserver)
        print(
            f"⚠️  Предупреждение при закрытии задачи (не критично): {type(e).__name__}"
        )


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Обучение модели с ClearML")
    parser.add_argument("--config", type=str, default="config/train_params.yaml")
    parser.add_argument("--model-type", type=str, help="Тип модели")
    parser.add_argument("--experiment-name", type=str, help="Название эксперимента")
    args = parser.parse_args()

    config_file = Path(args.config)
    if not config_file.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_file}")

    train_with_clearml(
        config_file=config_file,
        model_type=args.model_type,
        experiment_name=args.experiment_name,
    )


if __name__ == "__main__":
    main()
