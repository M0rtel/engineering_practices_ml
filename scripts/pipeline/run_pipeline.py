"""Скрипт для запуска полного ML пайплайна с мониторингом."""

import argparse
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_science_project.pipeline_monitor import (  # noqa: E402
    PipelineMonitor,
    notify_completion,
)


def create_monitoring_report(config_file: str = "config/train_params.yaml") -> None:
    """
    Создать отчет мониторинга о выполнении пайплайна.

    Args:
        config_file: Путь к конфигурационному файлу
    """
    monitor = PipelineMonitor()

    # Запускаем dvc repro --dry для определения статуса стадий
    try:
        result = subprocess.run(
            ["dvc", "repro", "--dry"], capture_output=True, text=True, check=False
        )  # nosec B603, B607
        dvc_output = result.stdout + result.stderr
    except Exception:
        dvc_output = ""

    # Проверяем результаты выполнения стадий
    stages_to_check = ["prepare_data", "validate_data", "train_model", "evaluate_model"]

    for stage_name in stages_to_check:
        # Проверяем, была ли стадия пропущена DVC
        is_skipped = f"Stage '{stage_name}' didn't change" in dvc_output

        # Проверяем наличие выходных файлов для определения статуса
        stage_completed = False
        if stage_name == "prepare_data":
            stage_completed = (
                Path("data/processed/train.csv").exists()
                and Path("data/processed/test.csv").exists()
            )
        elif stage_name == "validate_data":
            stage_completed = Path("reports/metrics/data_validation.json").exists()
        elif stage_name == "train_model":
            stage_completed = Path("models/model.pkl").exists()
        elif stage_name == "evaluate_model":
            stage_completed = Path("reports/metrics/evaluation.json").exists()

        if stage_completed:
            # Если стадия была пропущена, помечаем как skipped с нулевым временем
            if is_skipped:
                monitor.skip_stage(
                    stage_name, {"status": "skipped", "reason": "cached"}
                )
            else:
                # Стадия выполнена ранее, но мы не знаем точное время выполнения
                # Помечаем как completed без измерения времени
                monitor.complete_stage_unknown_time(
                    stage_name, {"status": "completed", "reason": "executed_earlier"}
                )
        else:
            monitor.start_stage(stage_name)
            monitor.fail_stage(stage_name, "Output files not found")

    # Сохраняем отчет
    report_path = monitor.save_report()
    monitor.print_summary()

    # Сохраняем отчет для DVC
    reports_dir = Path("reports/monitoring")
    reports_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(report_path, reports_dir / "pipeline_report.json")

    print(f"✅ Отчет мониторинга создан: {reports_dir / 'pipeline_report.json'}")


def run_pipeline(
    config_file: str = "config/train_params.yaml",
    monitor: bool = True,
    stages: list[str] | None = None,
) -> None:
    """
    Запустить ML пайплайн.

    Args:
        config_file: Путь к конфигурационному файлу
        monitor: Включить мониторинг
        stages: Список стадий для выполнения (None = все)
    """
    monitor_obj = PipelineMonitor() if monitor else None

    if monitor_obj:
        monitor_obj.start_stage("pipeline_start")

    # Определяем стадии для выполнения
    if stages is None:
        stages = ["prepare_data", "validate_data", "train_model", "evaluate_model"]

    print(f"🚀 Запуск пайплайна с конфигурацией: {config_file}")
    print(f"📋 Стадии: {', '.join(stages)}")

    # Запускаем DVC pipeline
    try:
        if stages:
            # Запускаем указанные стадии
            cmd = ["dvc", "repro"] + stages
        else:
            # Запускаем все стадии
            cmd = ["dvc", "repro"]

        print(f"🔧 Выполнение команды: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, check=False, capture_output=True, text=True
        )  # nosec B603, B607

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)

        if monitor_obj:
            monitor_obj.complete_stage("pipeline_start", {"stages": stages})
            report_path = monitor_obj.save_report()
            monitor_obj.print_summary()
            notify_completion("ml_pipeline", "success", report_path)

            # Сохраняем отчет для DVC
            reports_dir = Path("reports/monitoring")
            reports_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(report_path, reports_dir / "pipeline_report.json")
        else:
            print("✅ Пайплайн успешно завершен!")

    except subprocess.CalledProcessError as e:
        if monitor_obj:
            monitor_obj.fail_stage("pipeline_start", str(e))
            report_path = monitor_obj.save_report()
            monitor_obj.print_summary()
            notify_completion("ml_pipeline", "failed", report_path)
        else:
            print(f"❌ Ошибка выполнения пайплайна: {e}")
        raise


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Запуск ML пайплайна")
    parser.add_argument("--config", type=str, default="config/train_params.yaml")
    parser.add_argument("--monitor", action="store_true", help="Включить мониторинг")
    parser.add_argument(
        "--stages", nargs="+", help="Стадии для выполнения (по умолчанию все)"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Только создать отчет мониторинга без запуска стадий",
    )
    args = parser.parse_args()

    if args.report_only:
        create_monitoring_report(config_file=args.config)
    else:
        run_pipeline(
            config_file=args.config,
            monitor=args.monitor,
            stages=args.stages,
        )


if __name__ == "__main__":
    main()
