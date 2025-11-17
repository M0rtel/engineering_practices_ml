"""Скрипт для запуска всех экспериментов."""

import subprocess  # nosec B404
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.experiments.generate_experiments import EXPERIMENTS  # noqa: E402

CONFIG_DIR = Path("config/experiments")


def run_all_experiments() -> None:
    """Запустить все эксперименты."""
    print(f"🚀 Запуск {len(EXPERIMENTS)} экспериментов...\n")

    for i, exp in enumerate(EXPERIMENTS, 1):
        exp_id = exp["id"]
        config_file = CONFIG_DIR / f"{exp_id}.yaml"

        if not config_file.exists():
            print(f"⚠️  Конфиг не найден: {config_file}, пропускаем")
            continue

        print(f"[{i}/{len(EXPERIMENTS)}] Запуск {exp_id}...")

        # Запускаем эксперимент
        cmd: list[str] = [
            "python",
            "scripts/experiments/run_experiment.py",
            "--model",
            str(exp["model"]),
            "--config",
            str(config_file),
        ]

        try:
            subprocess.run(cmd, check=True)  # nosec B603, B607
            print(f"✅ {exp_id} завершен\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка в {exp_id}: {e}\n")

    print("✅ Все эксперименты завершены!")

    # Генерируем отчет об экспериментах
    try:
        print("\n📊 Генерация отчета об экспериментах...")
        from scripts.reports.generate_experiment_report import (  # noqa: E402
            generate_markdown_report,
            load_all_experiments,
        )

        experiments = load_all_experiments()
        if experiments:
            report_path = Path("reports/experiments/latest.md")
            generate_markdown_report(
                experiments, report_path, include_visualizations=True
            )
            print(f"✅ Отчет сохранен: {report_path}")
        else:
            print("⚠️  Эксперименты не найдены для генерации отчета")
    except Exception as e:
        print(f"⚠️  Ошибка при генерации отчета: {e}")


if __name__ == "__main__":
    run_all_experiments()
