"""Скрипт для валидации данных."""

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.data_science_project.config_models import TrainingConfig
from src.data_science_project.pipeline_monitor import PipelineMonitor

# Пути
TRAIN_DATA = Path("data/processed/train.csv")
TEST_DATA = Path("data/processed/test.csv")
REPORTS_DIR = Path("reports")

# Создаем директории
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)

# Мониторинг
monitor = PipelineMonitor()


def validate_data(config_file: Path) -> dict[str, bool]:
    """
    Валидировать данные.

    Args:
        config_file: Путь к файлу конфигурации

    Returns:
        Словарь с результатами валидации
    """
    monitor.start_stage("validate_data")

    try:
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

        # Загружаем данные
        print("📊 Загрузка данных для валидации...")
        train_df = pd.read_csv(TRAIN_DATA)
        test_df = pd.read_csv(TEST_DATA)

        validation_results = {
            "train_has_target": data_config.target_column in train_df.columns,
            "test_has_target": data_config.target_column in test_df.columns,
            "train_has_features": all(
                col in train_df.columns for col in data_config.feature_columns
            ),
            "test_has_features": all(
                col in test_df.columns for col in data_config.feature_columns
            ),
            "train_no_nulls": train_df[data_config.feature_columns].isnull().sum().sum()
            == 0,
            "test_no_nulls": test_df[data_config.feature_columns].isnull().sum().sum()
            == 0,
            "train_size_valid": len(train_df) > 0,
            "test_size_valid": len(test_df) > 0,
        }

        all_valid = all(validation_results.values())

        if all_valid:
            print("✅ Валидация данных пройдена успешно")
        else:
            failed = [k for k, v in validation_results.items() if not v]
            print(f"❌ Валидация не пройдена. Ошибки: {', '.join(failed)}")

        # Сохраняем результаты (конвертируем numpy типы в Python типы)
        validation_results_serializable: dict[str, Any] = {}
        for k, v in validation_results.items():
            if isinstance(v, np.bool_):
                validation_results_serializable[k] = bool(v)
            elif isinstance(v, bool):
                validation_results_serializable[k] = v
            else:
                validation_results_serializable[k] = v

        with open(REPORTS_DIR / "metrics" / "data_validation.json", "w") as f:
            json.dump(validation_results_serializable, f, indent=2)

        monitor.complete_stage(
            "validate_data", {"valid": all_valid, **validation_results}
        )
        return validation_results

    except Exception as e:
        monitor.fail_stage("validate_data", str(e))
        raise


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Валидация данных")
    parser.add_argument("--config", type=str, default="config/train_params.yaml")
    args = parser.parse_args()

    config_file = Path(args.config)
    if not config_file.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_file}")

    validate_data(config_file)


if __name__ == "__main__":
    main()
