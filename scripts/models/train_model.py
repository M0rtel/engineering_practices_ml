"""Скрипт для обучения модели."""

import argparse
import json
import pickle  # nosec B403
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

from src.data_science_project.config_models import TrainingConfig

# Пути
TRAIN_DATA = Path("data/processed/train.csv")
MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")

# Создаем директории
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

    # Устанавливаем random_state только для моделей, которые его поддерживают
    model = models[model_type](**params)
    if "random_state" in model.get_params() and "random_state" not in params:
        model.set_params(random_state=42)

    return model


def train_model(config_file: Path, model_type: str | None = None) -> None:
    """
    Обучить модель.

    Args:
        config_file: Путь к файлу конфигурации
        model_type: Тип модели (переопределяет конфигурацию)
    """
    # Загружаем конфигурацию
    with open(config_file) as f:
        config_dict = yaml.safe_load(f)

    # Создаем конфигурацию с опциональной моделью
    training_config_dict = {
        "data": config_dict["data"],
    }
    if "model" in config_dict:
        training_config_dict["model"] = config_dict["model"]

    training_config = TrainingConfig(**training_config_dict)

    # Определяем тип модели
    if model_type:
        model_type_final = model_type
    elif "model" in config_dict and "model_type" in config_dict["model"]:
        model_type_final = config_dict["model"]["model_type"]
    else:
        # Используем параметры из train для обратной совместимости
        model_type_final = "rf"
        if "train" in config_dict:
            {
                "n_estimators": config_dict["train"].get("n_estimators", 100),
                "max_depth": config_dict["train"].get("max_depth", 10),
                "min_samples_split": config_dict["train"].get("min_samples_split", 2),
                "min_samples_leaf": config_dict["train"].get("min_samples_leaf", 1),
                "random_state": config_dict["train"].get("random_state", 42),
            }
        else:
            pass

    # Получаем параметры модели
    if "model" in config_dict and "params" in config_dict["model"]:
        model_params = config_dict["model"]["params"]
    elif "train" in config_dict:
        # Параметры из train подходят только для Random Forest
        # Для других моделей используем только random_state, если поддерживается
        if model_type_final == "rf":
            model_params = {
                "n_estimators": config_dict["train"].get("n_estimators", 100),
                "max_depth": config_dict["train"].get("max_depth", 10),
                "min_samples_split": config_dict["train"].get("min_samples_split", 2),
                "min_samples_leaf": config_dict["train"].get("min_samples_leaf", 1),
                "random_state": config_dict["train"].get("random_state", 42),
            }
        else:
            # Для других моделей используем только random_state, если есть
            model_params = {}
            if config_dict["train"].get("random_state"):
                model_params["random_state"] = config_dict["train"]["random_state"]
    else:
        model_params = {}

    # Загружаем данные
    print("📊 Загрузка данных для обучения...")
    train_df = pd.read_csv(TRAIN_DATA)

    # Подготовка данных
    data_config = training_config.data
    target_col = data_config.target_column
    feature_cols = data_config.feature_columns

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]

    # Обучение модели
    print(f"🤖 Обучение модели: {model_type_final}...")
    model = get_model(model_type_final, model_params)
    model.fit(X_train, y_train)

    # Предсказания на train
    y_pred_train = model.predict(X_train)

    # Метрики
    metrics = {
        "train_mse": float(mean_squared_error(y_train, y_pred_train)),
        "train_rmse": float(mean_squared_error(y_train, y_pred_train) ** 0.5),
        "train_mae": float(mean_absolute_error(y_train, y_pred_train)),
        "train_r2": float(r2_score(y_train, y_pred_train)),
        "model_type": model_type_final,
    }

    # Сохраняем модель
    model_path = MODELS_DIR / "model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)  # nosec B301

    # Сохраняем метрики
    with open(REPORTS_DIR / "metrics" / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("✅ Модель обучена!")
    print(f"  Model: {model_type_final}")
    print(f"  Train R²: {metrics['train_r2']:.4f}")
    print(f"  Train RMSE: {metrics['train_rmse']:.4f}")
    print(f"  Модель сохранена: {model_path}")


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Обучение модели")
    parser.add_argument("--config", type=str, default="config/train_params.yaml")
    parser.add_argument("--model-type", type=str, help="Тип модели")
    args = parser.parse_args()

    config_file = Path(args.config)
    if not config_file.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_file}")

    train_model(config_file, args.model_type)


if __name__ == "__main__":
    main()
