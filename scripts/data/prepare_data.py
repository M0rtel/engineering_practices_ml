"""Скрипт для подготовки данных."""

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

from src.data_science_project.config_models import TrainingConfig

# Пути к данным
RAW_DATA = Path("data/raw/WineQT.csv")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")


def prepare_data(config_file: Path) -> None:
    """
    Подготовить данные.

    Args:
        config_file: Путь к файлу конфигурации
    """
    # Создаем директории
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "plots").mkdir(parents=True, exist_ok=True)

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
    print("📊 Загрузка данных...")
    df = pd.read_csv(RAW_DATA)

    # Базовая предобработка
    print("🔧 Предобработка данных...")
    # Удаляем дубликаты, если есть
    df = df.drop_duplicates()

    # Разделяем на train/test
    train_df, test_df = train_test_split(
        df,
        test_size=data_config.test_size,
        random_state=data_config.random_state,
        stratify=(
            df[data_config.target_column]
            if data_config.stratify and data_config.target_column in df.columns
            else None
        ),
    )

    # Сохраняем обработанные данные
    print("💾 Сохранение обработанных данных...")
    train_df.to_csv(PROCESSED_DIR / "train.csv", index=False)
    test_df.to_csv(PROCESSED_DIR / "test.csv", index=False)

    # Сохраняем статистику
    stats = {
        "train_size": len(train_df),
        "test_size": len(test_df),
        "total_size": len(df),
        "features": list(df.columns),
        "target": data_config.target_column,
    }

    with open(REPORTS_DIR / "metrics" / "data_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    # Создаем данные для графика распределения
    distribution_data: dict[str, Any]
    if data_config.target_column in df.columns:
        distribution = (
            df[data_config.target_column].value_counts().sort_index().to_dict()
        )
        distribution_data = {
            data_config.target_column: list(distribution.keys()),
            "count": list(distribution.values()),
        }
    else:
        distribution_data = {
            "message": f"Target column '{data_config.target_column}' not found"
        }

    with open(REPORTS_DIR / "plots" / "data_distribution.json", "w") as f:
        json.dump(distribution_data, f, indent=2)

    print("✅ Данные подготовлены!")
    print(f"  Train: {len(train_df)} записей")
    print(f"  Test: {len(test_df)} записей")


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Подготовка данных")
    parser.add_argument("--config", type=str, default="config/train_params.yaml")
    args = parser.parse_args()

    config_file = Path(args.config)
    if not config_file.exists():
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_file}")

    prepare_data(config_file)


if __name__ == "__main__":
    main()
