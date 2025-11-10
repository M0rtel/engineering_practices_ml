"""Скрипт для оценки модели."""

import json
import pickle  # nosec B403
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Пути
MODEL_PATH = Path("models/model.pkl")
TEST_DATA = Path("data/processed/test.csv")
REPORTS_DIR = Path("reports")

# Создаем директории
(REPORTS_DIR / "metrics").mkdir(parents=True, exist_ok=True)
(REPORTS_DIR / "plots").mkdir(parents=True, exist_ok=True)

# Загружаем модель
print("🤖 Загрузка модели...")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)  # nosec B301

# Загружаем тестовые данные
print("📊 Загрузка тестовых данных...")
test_df = pd.read_csv(TEST_DATA)

# Подготовка данных
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
