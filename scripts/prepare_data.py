"""Скрипт для подготовки данных."""

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

# Пути к данным
RAW_DATA = Path("data/raw/WineQT.csv")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")

# Создаем директории
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)

# Загружаем данные
print("📊 Загрузка данных...")
df = pd.read_csv(RAW_DATA)

# Базовая предобработка
print("🔧 Предобработка данных...")
# Удаляем дубликаты, если есть
df = df.drop_duplicates()

# Разделяем на train/test (пример)

train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["quality"] if "quality" in df.columns else None,
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
    "target": "quality" if "quality" in df.columns else None,
}

with open(REPORTS_DIR / "metrics" / "data_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

print("✅ Данные подготовлены!")
print(f"  Train: {len(train_df)} записей")
print(f"  Test: {len(test_df)} записей")
