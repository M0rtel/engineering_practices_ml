"""Генератор конфигураций для экспериментов."""

import json
from pathlib import Path

import yaml

# Директория для конфигов экспериментов
EXPERIMENTS_CONFIG_DIR = Path("config/experiments")
EXPERIMENTS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Определение экспериментов
EXPERIMENTS = [
    # Linear models
    {"model": "linear", "params": {}, "id": "exp_001_linear"},
    {"model": "ridge", "params": {"alpha": 1.0}, "id": "exp_002_ridge_1.0"},
    {"model": "ridge", "params": {"alpha": 0.1}, "id": "exp_003_ridge_0.1"},
    {"model": "ridge", "params": {"alpha": 10.0}, "id": "exp_004_ridge_10.0"},
    {"model": "lasso", "params": {"alpha": 1.0}, "id": "exp_005_lasso_1.0"},
    {"model": "lasso", "params": {"alpha": 0.1}, "id": "exp_006_lasso_0.1"},
    {
        "model": "elasticnet",
        "params": {"alpha": 1.0, "l1_ratio": 0.5},
        "id": "exp_007_elasticnet",
    },
    # KNN
    {"model": "knn", "params": {"n_neighbors": 5}, "id": "exp_008_knn_5"},
    {"model": "knn", "params": {"n_neighbors": 10}, "id": "exp_009_knn_10"},
    {"model": "knn", "params": {"n_neighbors": 20}, "id": "exp_010_knn_20"},
    # SVR
    {"model": "svr", "params": {"C": 1.0, "kernel": "rbf"}, "id": "exp_011_svr_rbf"},
    {
        "model": "svr",
        "params": {"C": 10.0, "kernel": "rbf"},
        "id": "exp_012_svr_rbf_c10",
    },
    {
        "model": "svr",
        "params": {"C": 1.0, "kernel": "linear"},
        "id": "exp_013_svr_linear",
    },
    # Decision Tree
    {"model": "dt", "params": {"max_depth": 5}, "id": "exp_014_dt_depth5"},
    {"model": "dt", "params": {"max_depth": 10}, "id": "exp_015_dt_depth10"},
    {"model": "dt", "params": {"max_depth": 20}, "id": "exp_016_dt_depth20"},
    # Random Forest
    {
        "model": "rf",
        "params": {"n_estimators": 50, "max_depth": 10},
        "id": "exp_017_rf_50_10",
    },
    {
        "model": "rf",
        "params": {"n_estimators": 100, "max_depth": 10},
        "id": "exp_018_rf_100_10",
    },
    {
        "model": "rf",
        "params": {"n_estimators": 200, "max_depth": 10},
        "id": "exp_019_rf_200_10",
    },
    {
        "model": "rf",
        "params": {"n_estimators": 100, "max_depth": 5},
        "id": "exp_020_rf_100_5",
    },
    {
        "model": "rf",
        "params": {"n_estimators": 100, "max_depth": 20},
        "id": "exp_021_rf_100_20",
    },
    # AdaBoost
    {"model": "ada", "params": {"n_estimators": 50}, "id": "exp_022_ada_50"},
    {"model": "ada", "params": {"n_estimators": 100}, "id": "exp_023_ada_100"},
    # Gradient Boosting
    {
        "model": "gb",
        "params": {"n_estimators": 50, "max_depth": 3},
        "id": "exp_024_gb_50_3",
    },
    {
        "model": "gb",
        "params": {"n_estimators": 100, "max_depth": 3},
        "id": "exp_025_gb_100_3",
    },
    {
        "model": "gb",
        "params": {"n_estimators": 100, "max_depth": 5},
        "id": "exp_026_gb_100_5",
    },
]


def generate_experiment_configs() -> None:
    """Генерировать конфигурационные файлы для всех экспериментов."""
    for exp in EXPERIMENTS:
        config = {
            "experiment_id": exp["id"],
            "model": exp["model"],
            "params": exp["params"],
        }

        # Сохраняем в YAML
        yaml_file = EXPERIMENTS_CONFIG_DIR / f"{exp['id']}.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        # Сохраняем в JSON
        json_file = EXPERIMENTS_CONFIG_DIR / f"{exp['id']}.json"
        with open(json_file, "w") as f:
            json.dump(config, f, indent=2)

    print(f"✅ Создано {len(EXPERIMENTS)} конфигураций экспериментов")
    print(f"   YAML: {EXPERIMENTS_CONFIG_DIR}/*.yaml")
    print(f"   JSON: {EXPERIMENTS_CONFIG_DIR}/*.json")


if __name__ == "__main__":
    generate_experiment_configs()
