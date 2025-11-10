"""Скрипт для запуска ML экспериментов с трекингом через DVC."""

import argparse
import json
import pickle  # nosec B403
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
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

# Пути
DATA_DIR = Path("data/processed")
MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")
CONFIG_DIR = Path("config")

# Создаем директории
MODELS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "experiments").mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Загрузить данные для обучения."""
    train_df = pd.read_csv(DATA_DIR / "train.csv")
    test_df = pd.read_csv(DATA_DIR / "test.csv")

    feature_cols = [
        "fixed acidity",
        "volatile acidity",
        "citric acid",
        "residual sugar",
        "chlorides",
        "free sulfur dioxide",
        "total sulfur dioxide",
        "density",
        "pH",
        "sulphates",
        "alcohol",
    ]
    target_col = "quality"

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    return X_train, X_test, y_train, y_test


def get_model(model_name: str, **params: Any) -> Any:
    """Создать модель по имени."""
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

    if model_name not in models:
        raise ValueError(f"Unknown model: {model_name}")

    return models[model_name](**params)


def train_and_evaluate(
    model_name: str, params: dict[str, Any], experiment_id: str
) -> tuple[dict[str, float], Path]:
    """Обучить модель и оценить её."""
    # Загружаем данные
    X_train, X_test, y_train, y_test = load_data()

    # Создаем модель
    model = get_model(model_name, **params)

    # Устанавливаем random_state только для моделей, которые его поддерживают
    if "random_state" in model.get_params():
        model.set_params(random_state=42)

    # Обучаем
    print(f"🤖 Обучение {model_name}...")
    model.fit(X_train, y_train)

    # Предсказания
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Метрики
    metrics = {
        "train_mse": float(mean_squared_error(y_train, y_pred_train)),
        "train_rmse": float(mean_squared_error(y_train, y_pred_train) ** 0.5),
        "train_mae": float(mean_absolute_error(y_train, y_pred_train)),
        "train_r2": float(r2_score(y_train, y_pred_train)),
        "test_mse": float(mean_squared_error(y_test, y_pred_test)),
        "test_rmse": float(mean_squared_error(y_test, y_pred_test) ** 0.5),
        "test_mae": float(mean_absolute_error(y_test, y_pred_test)),
        "test_r2": float(r2_score(y_test, y_pred_test)),
    }

    # Сохраняем модель
    model_path = MODELS_DIR / f"{experiment_id}_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)  # nosec B301

    # Сохраняем метрики
    metrics_path = REPORTS_DIR / "metrics" / f"{experiment_id}_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    # Сохраняем параметры
    params_path = REPORTS_DIR / "experiments" / f"{experiment_id}_params.json"
    experiment_data = {
        "experiment_id": experiment_id,
        "model_name": model_name,
        "params": params,
        "metrics": metrics,
    }
    with open(params_path, "w") as f:
        json.dump(experiment_data, f, indent=2)

    print(f"✅ Эксперимент {experiment_id} завершен")
    print(f"  Test R²: {metrics['test_r2']:.4f}")
    print(f"  Test RMSE: {metrics['test_rmse']:.4f}")

    return metrics, model_path


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Запуск ML эксперимента")
    parser.add_argument("--model", type=str, required=True, help="Название модели")
    parser.add_argument("--params", type=str, help="JSON строка с параметрами")
    parser.add_argument("--experiment-id", type=str, help="ID эксперимента")
    parser.add_argument("--config", type=str, help="Путь к YAML конфигу")

    args = parser.parse_args()

    # Загружаем параметры
    if args.config:
        with open(args.config) as f:
            config = yaml.safe_load(f)
        params = config.get("params", {})
        experiment_id = config.get("experiment_id", args.experiment_id or "exp_1")
    elif args.params:
        params = json.loads(args.params)
        experiment_id = args.experiment_id or "exp_1"
    else:
        params = {}
        experiment_id = args.experiment_id or "exp_1"

    # Запускаем эксперимент
    train_and_evaluate(args.model, params, experiment_id)


if __name__ == "__main__":
    main()
