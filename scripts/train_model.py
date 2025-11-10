"""Скрипт для обучения модели."""

import json
import pickle  # nosec B403
from pathlib import Path

import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Пути
TRAIN_DATA = Path("data/processed/train.csv")
MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")
CONFIG_FILE = Path("config/train_params.yaml")

# Создаем директории
MODELS_DIR.mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)

# Загружаем конфигурацию
with open(CONFIG_FILE) as f:
    config = yaml.safe_load(f)

# Загружаем данные
print("📊 Загрузка данных для обучения...")
train_df = pd.read_csv(TRAIN_DATA)

# Подготовка данных
target_col = config["data"]["target_column"]
feature_cols = config["data"]["feature_columns"]

X_train = train_df[feature_cols]
y_train = train_df[target_col]

# Обучение модели
print("🤖 Обучение модели...")
model = RandomForestRegressor(
    n_estimators=config["train"]["n_estimators"],
    max_depth=config["train"]["max_depth"],
    min_samples_split=config["train"]["min_samples_split"],
    min_samples_leaf=config["train"]["min_samples_leaf"],
    random_state=config["train"]["random_state"],
)

model.fit(X_train, y_train)

# Предсказания на train
y_pred_train = model.predict(X_train)

# Метрики
metrics = {
    "train_mse": float(mean_squared_error(y_train, y_pred_train)),
    "train_rmse": float(mean_squared_error(y_train, y_pred_train) ** 0.5),
    "train_mae": float(mean_absolute_error(y_train, y_pred_train)),
    "train_r2": float(r2_score(y_train, y_pred_train)),
}

# Сохраняем модель
model_path = MODELS_DIR / "model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(model, f)  # nosec B301

# Сохраняем метрики
with open(REPORTS_DIR / "metrics" / "model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("✅ Модель обучена!")
print(f"  Train R²: {metrics['train_r2']:.4f}")
print(f"  Train RMSE: {metrics['train_rmse']:.4f}")
print(f"  Модель сохранена: {model_path}")
