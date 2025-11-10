"""Система мониторинга выполнения ML пайплайна."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel


class StageStatus(BaseModel):
    """Статус выполнения стадии пайплайна."""

    stage_name: str
    status: Literal["pending", "running", "completed", "failed", "skipped"]
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: float | None = None
    error: str | None = None
    metrics: dict[str, Any] | None = None


class PipelineMonitor:
    """Мониторинг выполнения пайплайна."""

    def __init__(self, reports_dir: Path | str = "reports"):
        """
        Инициализация монитора.

        Args:
            reports_dir: Директория для сохранения отчетов
        """
        self.reports_dir = Path(reports_dir)
        self.monitoring_dir = self.reports_dir / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        self.stages: dict[str, StageStatus] = {}

    def start_stage(self, stage_name: str) -> None:
        """
        Начать выполнение стадии.

        Args:
            stage_name: Название стадии
        """
        self.stages[stage_name] = StageStatus(
            stage_name=stage_name,
            status="running",
            start_time=datetime.now(),
        )
        print(f"🚀 Начало выполнения стадии: {stage_name}")

    def complete_stage(
        self, stage_name: str, metrics: dict[str, Any] | None = None
    ) -> None:
        """
        Завершить выполнение стадии.

        Args:
            stage_name: Название стадии
            metrics: Метрики стадии
        """
        if stage_name not in self.stages:
            self.start_stage(stage_name)

        stage = self.stages[stage_name]
        stage.status = "completed"
        stage.end_time = datetime.now()
        if stage.start_time:
            stage.duration = (stage.end_time - stage.start_time).total_seconds()
        stage.metrics = metrics

        print(f"✅ Стадия завершена: {stage_name} (время: {stage.duration:.2f}с)")

    def fail_stage(self, stage_name: str, error: str) -> None:
        """
        Отметить стадию как неудачную.

        Args:
            stage_name: Название стадии
            error: Сообщение об ошибке
        """
        if stage_name not in self.stages:
            self.start_stage(stage_name)

        stage = self.stages[stage_name]
        stage.status = "failed"
        stage.end_time = datetime.now()
        if stage.start_time:
            stage.duration = (stage.end_time - stage.start_time).total_seconds()
        stage.error = error

        print(f"❌ Стадия завершена с ошибкой: {stage_name}")
        print(f"   Ошибка: {error}")

    def skip_stage(
        self, stage_name: str, metrics: dict[str, Any] | None = None
    ) -> None:
        """
        Отметить стадию как пропущенную (cached).

        Args:
            stage_name: Название стадии
            metrics: Метрики стадии
        """
        self.stages[stage_name] = StageStatus(
            stage_name=stage_name,
            status="skipped",
            start_time=None,
            end_time=None,
            duration=0.0,
            metrics=metrics,
        )
        reason = metrics.get("reason", "unknown") if metrics else "unknown"
        print(f"⏭️  Стадия пропущена: {stage_name} (причина: {reason})")

    def complete_stage_unknown_time(
        self, stage_name: str, metrics: dict[str, Any] | None = None
    ) -> None:
        """
        Завершить стадию без измерения времени (стадия была выполнена ранее).

        Args:
            stage_name: Название стадии
            metrics: Метрики стадии
        """
        self.stages[stage_name] = StageStatus(
            stage_name=stage_name,
            status="completed",
            start_time=None,
            end_time=None,
            duration=None,  # Время неизвестно
            metrics=metrics,
        )
        reason = metrics.get("reason", "unknown") if metrics else "unknown"
        print(f"✅ Стадия завершена ранее: {stage_name} (время: неизвестно, {reason})")

    def save_report(self, pipeline_name: str = "ml_pipeline") -> Path:
        """
        Сохранить отчет о выполнении пайплайна.

        Args:
            pipeline_name: Название пайплайна

        Returns:
            Путь к сохраненному отчету
        """
        report = {
            "pipeline_name": pipeline_name,
            "timestamp": datetime.now().isoformat(),
            "stages": [stage.model_dump() for stage in self.stages.values()],
            "summary": self._generate_summary(),
        }

        report_file = (
            self.monitoring_dir
            / f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"📊 Отчет сохранен: {report_file}")
        return report_file

    def _generate_summary(self) -> dict[str, Any]:
        """Генерировать сводку выполнения."""
        total_stages = len(self.stages)
        completed = sum(1 for s in self.stages.values() if s.status == "completed")
        failed = sum(1 for s in self.stages.values() if s.status == "failed")
        skipped = sum(1 for s in self.stages.values() if s.status == "skipped")
        total_duration = sum(
            s.duration or 0 for s in self.stages.values() if s.duration is not None
        )

        return {
            "total_stages": total_stages,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "pending": total_stages - completed - failed - skipped,
            "total_duration": total_duration,
            "success_rate": (completed + skipped) / total_stages
            if total_stages > 0
            else 0.0,
        }

    def print_summary(self) -> None:
        """Вывести сводку выполнения."""
        summary = self._generate_summary()
        print("\n" + "=" * 50)
        print("📊 Сводка выполнения пайплайна")
        print("=" * 50)
        print(f"Всего стадий: {summary['total_stages']}")
        print(f"Завершено: {summary['completed']}")
        print(f"Пропущено (cached): {summary['skipped']}")
        print(f"Ошибок: {summary['failed']}")
        print(f"Ожидает: {summary['pending']}")
        print(f"Общее время: {summary['total_duration']:.2f}с")
        print(f"Успешность: {summary['success_rate']*100:.1f}%")
        print("=" * 50)

        for stage_name, stage in self.stages.items():
            status_icon = {
                "completed": "✅",
                "failed": "❌",
                "running": "🔄",
                "pending": "⏳",
                "skipped": "⏭️",
            }.get(stage.status, "❓")
            if stage.status == "skipped":
                duration_str = "cached"
            elif stage.duration is None:
                duration_str = "unknown"
            else:
                duration_str = f"{stage.duration:.2f}с"
            print(f"{status_icon} {stage_name}: {stage.status} ({duration_str})")


def notify_completion(
    pipeline_name: str, status: str, report_path: Path | None = None
) -> None:
    """
    Уведомить о завершении пайплайна.

    Args:
        pipeline_name: Название пайплайна
        status: Статус завершения
        report_path: Путь к отчету
    """
    print("\n" + "=" * 50)
    if status == "success":
        print(f"✅ Пайплайн '{pipeline_name}' успешно завершен!")
    else:
        print(f"❌ Пайплайн '{pipeline_name}' завершен с ошибками!")
    if report_path:
        print(f"📊 Отчет: {report_path}")
    print("=" * 50)
