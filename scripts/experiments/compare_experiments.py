"""Скрипт для сравнения и фильтрации экспериментов."""

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

REPORTS_DIR = Path("reports")
EXPERIMENTS_DIR = Path("experiments")

# Маппинг названий моделей для поиска
MODEL_NAME_MAPPING = {
    "randomforest": "rf",
    "random_forest": "rf",
    "rf": "rf",
    "ridge": "ridge",
    "lasso": "lasso",
    "elasticnet": "elasticnet",
    "elastic_net": "elasticnet",
    "linear": "linear",
    "linearregression": "linear",
    "knn": "knn",
    "kneighbors": "knn",
    "svr": "svr",
    "supportvectormachine": "svr",
    "dt": "dt",
    "decisiontree": "dt",
    "ada": "ada",
    "adaboost": "ada",
    "gb": "gb",
    "gradientboosting": "gb",
    "gradient_boosting": "gb",
}


def normalize_model_name(model_name: str) -> str:
    """Нормализовать название модели для поиска."""
    return MODEL_NAME_MAPPING.get(
        model_name.lower().replace(" ", "").replace("_", ""), model_name.lower()
    )


def load_all_experiments() -> list[dict[str, Any]]:
    """Загрузить все эксперименты."""
    experiments = []

    # Загружаем из reports/experiments
    for params_file in (REPORTS_DIR / "experiments").glob("*_params.json"):
        exp_id = params_file.stem.replace("_params", "")
        metrics_file = REPORTS_DIR / "metrics" / f"{exp_id}_metrics.json"

        exp_data = {"experiment_id": exp_id}

        # Загружаем параметры
        with open(params_file) as f:
            params_data = json.load(f)
            exp_data.update(params_data)

        # Загружаем метрики (приоритет у отдельного файла метрик)
        if metrics_file.exists():
            with open(metrics_file) as f:
                exp_data["metrics"] = json.load(f)
        # Если метрики уже есть в params_data, но нет отдельного файла, используем их
        elif "metrics" in params_data:
            exp_data["metrics"] = params_data["metrics"]

        experiments.append(exp_data)

    return experiments


def compare_experiments(exp_id1: str, exp_id2: str) -> None:
    """Сравнить два эксперимента."""
    experiments = load_all_experiments()
    exp1 = next((e for e in experiments if e["experiment_id"] == exp_id1), None)
    exp2 = next((e for e in experiments if e["experiment_id"] == exp_id2), None)

    if not exp1 or not exp2:
        print("❌ Один или оба эксперимента не найдены")
        return

    print("\n📊 Сравнение экспериментов:")
    print(f"  {exp_id1} vs {exp_id2}\n")

    # Сравнение параметров
    print("Параметры:")
    print(
        f"  Модель: {exp1.get('model_name', 'N/A')} vs {exp2.get('model_name', 'N/A')}"
    )
    if "params" in exp1 and "params" in exp2:
        all_params = set(exp1["params"].keys()) | set(exp2["params"].keys())
        for param in sorted(all_params):
            val1 = exp1["params"].get(param, "N/A")
            val2 = exp2["params"].get(param, "N/A")
            if val1 != val2:
                print(f"  {param}: {val1} → {val2}")

    # Сравнение метрик
    if "metrics" in exp1 and "metrics" in exp2:
        print("\nМетрики:")
        for key in sorted(set(exp1["metrics"].keys()) | set(exp2["metrics"].keys())):
            val1 = exp1["metrics"].get(key, 0)
            val2 = exp2["metrics"].get(key, 0)
            diff = val2 - val1
            sign = "+" if diff >= 0 else ""
            print(f"  {key}: {val1:.4f} → {val2:.4f} ({sign}{diff:.4f})")


def filter_experiments(
    model_name: str | None = None,
    min_test_r2: float | None = None,
    max_test_rmse: float | None = None,
) -> list[dict[str, Any]]:
    """Фильтровать эксперименты по критериям."""
    experiments = load_all_experiments()

    # Нормализуем название модели для поиска
    normalized_model_name = None
    if model_name:
        normalized_model_name = normalize_model_name(model_name)

    filtered = []
    for exp in experiments:
        # Фильтр по модели (нечувствительный к регистру и с маппингом)
        if normalized_model_name:
            exp_model_name = exp.get("model_name", "").lower()
            exp_id = exp.get("experiment_id", "").lower()

            # Проверяем точное совпадение или через маппинг
            model_matches = (
                exp_model_name == normalized_model_name
                or normalized_model_name in exp_model_name
                or exp_model_name in normalized_model_name
            )

            # Также проверяем в experiment_id
            id_matches = normalized_model_name in exp_id

            if not (model_matches or id_matches):
                continue

        # Фильтр по метрикам
        if min_test_r2 or max_test_rmse:
            if "metrics" not in exp:
                # Если нужны метрики, но их нет, пропускаем эксперимент
                continue

            metrics = exp["metrics"]
            test_r2 = metrics.get("test_r2")
            test_rmse = metrics.get("test_rmse")

            if min_test_r2 is not None:
                if test_r2 is None or test_r2 < min_test_r2:
                    continue

            if max_test_rmse is not None:
                if test_rmse is None or test_rmse > max_test_rmse:
                    continue

        filtered.append(exp)

    return filtered


def search_experiments(query: str) -> list[dict[str, Any]]:
    """Поиск экспериментов по запросу."""
    experiments = load_all_experiments()
    query_lower = query.lower()
    normalized_query = normalize_model_name(query)

    # Обратный маппинг: находим все модели, которые соответствуют запросу
    matching_models = set()
    for key, value in MODEL_NAME_MAPPING.items():
        if query_lower in key or query_lower in value:
            matching_models.add(value)
            matching_models.add(key)

    results = []
    for exp in experiments:
        exp_id = exp.get("experiment_id", "").lower()
        model_name = exp.get("model_name", "").lower()

        # Поиск в experiment_id, model_name и через маппинг
        matches = (
            query_lower in exp_id
            or query_lower in model_name
            or normalized_query in model_name
            or model_name in normalized_query
            or model_name in matching_models
            or any(match in exp_id for match in matching_models)
        )

        if matches:
            results.append(exp)

    return results


def export_to_dataframe() -> pd.DataFrame:
    """Экспортировать все эксперименты в DataFrame."""
    experiments = load_all_experiments()

    rows = []
    for exp in experiments:
        row = {"experiment_id": exp.get("experiment_id")}
        row["model_name"] = exp.get("model_name", "N/A")

        # Параметры
        if "params" in exp:
            for key, value in exp["params"].items():
                row[f"param_{key}"] = value

        # Метрики
        if "metrics" in exp:
            for key, value in exp["metrics"].items():
                row[key] = value

        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Сравнение и фильтрация экспериментов")
    parser.add_argument(
        "--compare", nargs=2, metavar=("EXP1", "EXP2"), help="Сравнить два эксперимента"
    )
    parser.add_argument("--filter-model", type=str, help="Фильтр по модели")
    parser.add_argument("--min-r2", type=float, help="Минимальный test_r2")
    parser.add_argument("--max-rmse", type=float, help="Максимальный test_rmse")
    parser.add_argument("--search", type=str, help="Поиск по запросу")
    parser.add_argument("--export", type=str, help="Экспорт в CSV файл")
    parser.add_argument("--list", action="store_true", help="Список всех экспериментов")

    args = parser.parse_args()

    if args.compare:
        compare_experiments(args.compare[0], args.compare[1])
    elif args.search:
        results = search_experiments(args.search)
        print(f"\n🔍 Найдено {len(results)} экспериментов:")
        for exp in results:
            print(f"  - {exp.get('experiment_id')} ({exp.get('model_name', 'N/A')})")
    elif args.filter_model or args.min_r2 or args.max_rmse:
        filtered = filter_experiments(
            model_name=args.filter_model,
            min_test_r2=args.min_r2,
            max_test_rmse=args.max_rmse,
        )
        print(f"\n📋 Найдено {len(filtered)} экспериментов:")
        for exp in filtered:
            metrics = exp.get("metrics", {})
            print(
                f"  - {exp.get('experiment_id')}: "
                f"R²={metrics.get('test_r2', 0):.4f}, "
                f"RMSE={metrics.get('test_rmse', 0):.4f}"
            )
    elif args.export:
        df = export_to_dataframe()
        df.to_csv(args.export, index=False)
        print(f"✅ Эксперименты экспортированы в {args.export}")
    elif args.list:
        experiments = load_all_experiments()
        print(f"\n📋 Всего экспериментов: {len(experiments)}\n")
        for exp in experiments:
            metrics = exp.get("metrics", {})
            print(
                f"  {exp.get('experiment_id')}: "
                f"{exp.get('model_name', 'N/A')} - "
                f"R²={metrics.get('test_r2', 0):.4f}, "
                f"RMSE={metrics.get('test_rmse', 0):.4f}"
            )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
