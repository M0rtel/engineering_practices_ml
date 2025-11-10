"""Скрипт для оценки модели."""

import argparse
import json
import pickle  # nosec B403
from pathlib import Path

import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.data_science_project.config_models import TrainingConfig

# Пути
MODEL_PATH = Path("models/model.pkl")
TEST_DATA = Path("data/processed/test.csv")
REPORTS_DIR = Path("reports")

# Создаем директории
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "plots").mkdir(parents=True, exist_ok=True)


def evaluate_model(config_file: Path) -> None:
    """
    Оценить модель.

    Args:
        config_file: Путь к файлу конфигурации
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

    data_config = training_config.data

    # Загружаем модель
    print("🤖 Загрузка модели...")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)  # nosec B301

    # Загружаем тестовые данные
    print("📊 Загрузка тестовых данных...")
    test_df = pd.read_csv(TEST_DATA)

    # Подготовка данных
    feature_cols = data_config.feature_columns
    target_col = data_config.target_column

    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    # Предсказания
    print("🔮 Предсказания...")
    y_pred = model.predict(X_test)

    # Метрики
    metrics = {
        "test_mse": float(mean_squared_error(y_test, y_pred)),
        "test_rmse": float(mean_squared_error(y_test, y_pred) ** 0.5),
        "test_mae": float(mean_absolute_error(y_test, y_pred)),
        "test_r2": float(r2_score(y_test, y_pred)),
    }

    # Сохраняем метрики
    with open(REPORTS_DIR / "metrics" / "evaluation.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # Создаем данные для confusion matrix (для регрессии - распределение ошибок)
    # Округляем предсказания до целых для создания "confusion matrix"
    y_pred_rounded = y_pred.round().astype(int)
    y_test_int = y_test.astype(int)

    # Создаем матрицу совпадений (для регрессии это распределение ошибок)
    confusion_data = {
        "actual": y_test_int.tolist(),
        "predicted": y_pred_rounded.tolist(),
        "errors": (y_pred_rounded - y_test_int).tolist(),
    }

    with open(REPORTS_DIR / "plots" / "confusion_matrix.json", "w") as f:
        json.dump(confusion_data, f, indent=2)

    print("✅ Модель оценена!")
    print(f"  Test R²: {metrics['test_r2']:.4f}")
    print(f"  Test RMSE: {metrics['test_rmse']:.4f}")


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Оценка модели")
    parser.add_argument("--config", type=str, default="config/train_params.yaml")
    args = parser.parse_args()

    config_file = Path(args.config)
    if not config_file.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_file}")

    evaluate_model(config_file)


if __name__ == "__main__":
    main()
