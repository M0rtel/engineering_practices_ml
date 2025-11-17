"""Скрипт для генерации отчетов об экспериментах в формате Markdown."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tabulate import tabulate

# Настройка стиля для графиков
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10

REPORTS_DIR = Path("reports")
EXPERIMENTS_DIR = Path("experiments")
OUTPUT_DIR = REPORTS_DIR / "experiments"


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

        # Загружаем метрики
        if metrics_file.exists():
            with open(metrics_file) as f:
                exp_data["metrics"] = json.load(f)

        experiments.append(exp_data)

    return experiments


def create_comparison_table(experiments: list[dict[str, Any]]) -> pd.DataFrame:
    """Создать сравнительную таблицу экспериментов."""
    rows = []
    for exp in experiments:
        row = {"Experiment ID": exp.get("experiment_id", "N/A")}
        row["Model"] = exp.get("model_name", "N/A")

        # Параметры
        if "params" in exp:
            for key, value in exp["params"].items():
                row[key] = value

        # Метрики
        if "metrics" in exp:
            for key, value in exp["metrics"].items():
                row[key] = value

        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def create_metrics_visualization(
    experiments: list[dict[str, Any]], output_path: Path
) -> None:
    """Создать визуализацию метрик."""
    df = create_comparison_table(experiments)

    if df.empty:
        return

    # Фильтруем только эксперименты с метриками
    metric_cols = [col for col in df.columns if col not in ["Experiment ID", "Model"]]
    if not metric_cols:
        return

    # Создаем графики для основных метрик
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle("Сравнение метрик экспериментов", fontsize=16, fontweight="bold")

    # График R²
    if "test_r2" in df.columns:
        ax = axes[0, 0]
        df_sorted = df.sort_values("test_r2", ascending=False)
        ax.barh(
            df_sorted["Experiment ID"].astype(str),
            df_sorted["test_r2"],
            color="steelblue",
        )
        ax.set_xlabel("R² Score")
        ax.set_title("R² Score по экспериментам")
        ax.grid(axis="x", alpha=0.3)

    # График RMSE
    if "test_rmse" in df.columns:
        ax = axes[0, 1]
        df_sorted = df.sort_values("test_rmse", ascending=True)
        ax.barh(
            df_sorted["Experiment ID"].astype(str),
            df_sorted["test_rmse"],
            color="coral",
        )
        ax.set_xlabel("RMSE")
        ax.set_title("RMSE по экспериментам")
        ax.grid(axis="x", alpha=0.3)

    # График MAE
    if "test_mae" in df.columns:
        ax = axes[1, 0]
        df_sorted = df.sort_values("test_mae", ascending=True)
        ax.barh(
            df_sorted["Experiment ID"].astype(str),
            df_sorted["test_mae"],
            color="mediumseagreen",
        )
        ax.set_xlabel("MAE")
        ax.set_title("MAE по экспериментам")
        ax.grid(axis="x", alpha=0.3)

    # Scatter plot R² vs RMSE
    if "test_r2" in df.columns and "test_rmse" in df.columns:
        ax = axes[1, 1]
        ax.scatter(df["test_rmse"], df["test_r2"], s=100, alpha=0.6, c=range(len(df)))
        ax.set_xlabel("RMSE")
        ax.set_ylabel("R² Score")
        ax.set_title("R² vs RMSE")
        ax.grid(alpha=0.3)

        # Добавляем подписи
        for _idx, row in df.iterrows():
            ax.annotate(
                row["Experiment ID"],
                (row["test_rmse"], row["test_r2"]),
                fontsize=8,
                alpha=0.7,
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def create_model_comparison_plot(
    experiments: list[dict[str, Any]], output_path: Path
) -> None:
    """Создать график сравнения моделей."""
    df = create_comparison_table(experiments)

    if df.empty or "Model" not in df.columns:
        return

    # Группируем по моделям
    if "test_r2" in df.columns:
        model_metrics = df.groupby("Model")["test_r2"].agg(["mean", "std", "count"])

        fig, ax = plt.subplots(figsize=(12, 6))
        x_pos = range(len(model_metrics))
        ax.bar(
            x_pos,
            model_metrics["mean"],
            yerr=model_metrics["std"],
            capsize=5,
            color="steelblue",
            alpha=0.7,
        )
        ax.set_xticks(x_pos)
        ax.set_xticklabels(model_metrics.index, rotation=45, ha="right")
        ax.set_ylabel("Mean R² Score")
        ax.set_title("Сравнение моделей по среднему R² Score")
        ax.grid(axis="y", alpha=0.3)

        # Добавляем количество экспериментов
        for i, (_idx, row) in enumerate(model_metrics.iterrows()):
            ax.text(
                i,
                row["mean"] + row["std"] + 0.01,
                f"n={int(row['count'])}",
                ha="center",
                fontsize=9,
            )

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()


def generate_markdown_report(
    experiments: list[dict[str, Any]],
    output_path: Path,
    include_visualizations: bool = True,
) -> None:
    """Сгенерировать отчет в формате Markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# Отчет об экспериментах

**Дата генерации:** {timestamp}
**Количество экспериментов:** {len(experiments)}

## Содержание

- [Сводка](#сводка)
- [Сравнительная таблица](#сравнительная-таблица)
- [Визуализации](#визуализации)
- [Детали экспериментов](#детали-экспериментов)

## Сводка

"""

    # Создаем сравнительную таблицу
    df = create_comparison_table(experiments)

    if not df.empty:
        # Статистика по моделям
        if "Model" in df.columns:
            report += "### Статистика по моделям\n\n"
            # Выбираем только числовые метрики для статистики
            numeric_cols = [
                col
                for col in df.columns
                if col not in ["Experiment ID", "Model"]
                and df[col].dtype in ["float64", "int64"]
            ]
            if numeric_cols:
                model_stats = df.groupby("Model")[numeric_cols].agg(
                    ["mean", "std", "count"]
                )
                # Используем tabulate для лучшей совместимости
                report += (
                    tabulate(
                        model_stats, headers="keys", tablefmt="pipe", floatfmt=".4f"
                    )
                    + "\n\n"
                )

        # Лучшие эксперименты
        if "test_r2" in df.columns:
            report += "### Топ-5 экспериментов по R² Score\n\n"
            top5 = df.nlargest(5, "test_r2")[
                ["Experiment ID", "Model", "test_r2", "test_rmse"]
            ]
            report += (
                tabulate(
                    top5,
                    headers="keys",
                    tablefmt="pipe",
                    showindex=False,
                    floatfmt=".4f",
                )
                + "\n\n"
            )

    # Сравнительная таблица
    report += """## Сравнительная таблица

"""

    if not df.empty:
        # Ограничиваем количество столбцов для читаемости
        display_cols = ["Experiment ID", "Model"]
        metric_cols = [col for col in df.columns if col.startswith("test_")]
        display_cols.extend(metric_cols[:10])  # Первые 10 метрик

        report += (
            tabulate(
                df[display_cols],
                headers="keys",
                tablefmt="pipe",
                showindex=False,
                floatfmt=".4f",
            )
            + "\n\n"
        )

        # Полная таблица в отдельном разделе
        report += """### Полная таблица

<details>
<summary>Развернуть полную таблицу</summary>

"""
        report += (
            tabulate(
                df, headers="keys", tablefmt="pipe", showindex=False, floatfmt=".4f"
            )
            + "\n\n"
        )
        report += "</details>\n\n"

    # Визуализации
    if include_visualizations:
        report += """## Визуализации

"""

        # Создаем графики
        metrics_plot_path = OUTPUT_DIR / "metrics_comparison.png"
        model_plot_path = OUTPUT_DIR / "model_comparison.png"

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        create_metrics_visualization(experiments, metrics_plot_path)
        create_model_comparison_plot(experiments, model_plot_path)

        if metrics_plot_path.exists():
            report += """### Сравнение метрик

![Сравнение метрик](metrics_comparison.png)

"""

        if model_plot_path.exists():
            report += """### Сравнение моделей

![Сравнение моделей](model_comparison.png)

"""

    # Детали экспериментов
    report += """## Детали экспериментов

"""

    for exp in experiments:
        exp_id = exp.get("experiment_id", "N/A")
        model_name = exp.get("model_name", "N/A")

        report += f"""### {exp_id}

**Модель:** {model_name}

**Параметры:**
"""
        if "params" in exp:
            for key, value in exp["params"].items():
                report += f"- `{key}`: {value}\n"

        report += "\n**Метрики:**\n"
        if "metrics" in exp:
            for key, value in exp["metrics"].items():
                if isinstance(value, float):
                    report += f"- `{key}`: {value:.4f}\n"
                else:
                    report += f"- `{key}`: {value}\n"

        report += "\n"

    # Сохраняем отчет
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Отчет сохранен: {output_path}")


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Генерация отчета об экспериментах в формате Markdown"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/experiments/latest.md",
        help="Путь к выходному файлу",
    )
    parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Не создавать визуализации",
    )
    args = parser.parse_args()

    # Загружаем эксперименты
    experiments = load_all_experiments()

    if not experiments:
        print("⚠️  Эксперименты не найдены")
        return

    # Генерируем отчет
    output_path = Path(args.output)
    generate_markdown_report(
        experiments, output_path, include_visualizations=not args.no_visualizations
    )

    print(f"📊 Обработано экспериментов: {len(experiments)}")


if __name__ == "__main__":
    main()
