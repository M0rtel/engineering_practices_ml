"""Интеграция ClearML для трекинга экспериментов и управления моделями."""

import json
from pathlib import Path
from typing import Any

try:
    from clearml import OutputModel, PipelineController, Task
except ImportError:
    Task = None
    OutputModel = None
    PipelineController = None


class ClearMLTracker:
    """Трекер экспериментов на базе ClearML."""

    def __init__(
        self,
        project_name: str = "Engineering Practices ML",
        task_name: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """
        Инициализация трекера ClearML.

        Args:
            project_name: Название проекта в ClearML
            task_name: Название задачи (эксперимента)
            tags: Теги для задачи
        """
        if Task is None:
            raise ImportError(
                "ClearML не установлен. Установите через: poetry add clearml"
            )

        self.task = Task.init(
            project_name=project_name,
            task_name=task_name,
            tags=tags or [],
        )
        self.project_name = project_name
        self.task_name = task_name

    def log_params(self, params: dict[str, Any]) -> None:
        """
        Логировать параметры эксперимента.

        Args:
            params: Словарь с параметрами
        """
        self.task.connect(params)

    def log_metrics(self, metrics: dict[str, float], step: int | None = None) -> None:
        """
        Логировать метрики эксперимента.

        Args:
            metrics: Словарь с метриками
            step: Шаг итерации (опционально)
        """
        for metric_name, metric_value in metrics.items():
            if step is not None:
                self.task.get_logger().report_scalar(
                    title="Metrics",
                    series=metric_name,
                    value=metric_value,
                    iteration=step,
                )
            else:
                self.task.logger.report_single_value(
                    name=metric_name, value=metric_value
                )

    def log_artifact(self, artifact_path: str | Path, name: str | None = None) -> None:
        """
        Логировать артефакт (файл).

        Args:
            artifact_path: Путь к файлу
            name: Имя артефакта (если не указано, используется имя файла)
        """
        artifact_path = Path(artifact_path)
        if not artifact_path.exists():
            raise FileNotFoundError(f"Артефакт не найден: {artifact_path}")

        name = name or artifact_path.name
        self.task.upload_artifact(name=name, artifact_object=str(artifact_path))

    def log_model(
        self,
        model_path: str | Path,
        model_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Зарегистрировать модель в ClearML.

        Args:
            model_path: Путь к файлу модели
            model_name: Имя модели
            metadata: Метаданные модели
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Модель не найдена: {model_path}")

        model_name = model_name or model_path.stem

        # Создаем OutputModel для регистрации модели
        output_model = OutputModel(task=self.task, name=model_name)
        output_model.update_weights(weights_filename=str(model_path))

        if metadata:
            # Преобразуем метаданные в формат, ожидаемый ClearML
            # set_all_metadata ожидает Dict[key, Dict[value, type]]
            # Используем set_metadata для каждого ключа
            for key, value in metadata.items():
                # Преобразуем значение в строку, если это не строка
                if isinstance(value, dict | list):
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                output_model.set_metadata(key=key, value=value_str)

        self.task.logger.report_text(f"Модель зарегистрирована: {model_name}")

    def log_plot(self, plot_name: str, plot_data: Any) -> None:
        """
        Логировать график.

        Args:
            plot_name: Название графика
            plot_data: Данные для графика
        """
        self.task.logger.report_matplotlib_figure(
            title=plot_name, series="plots", iteration=0, figure=plot_data
        )

    def close(self) -> None:
        """Закрыть задачу (завершить эксперимент)."""
        self.task.close()

    def get_task_id(self) -> str:
        """
        Получить ID задачи.

        Returns:
            ID задачи в ClearML
        """
        task_id = self.task.id
        return str(task_id) if task_id is not None else ""

    def get_task_url(self) -> str:
        """
        Получить URL задачи в веб-интерфейсе.

        Returns:
            URL задачи
        """
        url = self.task.get_output_log_web_page()
        return str(url) if url is not None else ""


class ClearMLModelManager:
    """Менеджер моделей ClearML."""

    def __init__(self, project_name: str = "Engineering Practices ML") -> None:
        """
        Инициализация менеджера моделей.

        Args:
            project_name: Название проекта
        """
        if OutputModel is None:
            raise ImportError(
                "ClearML не установлен. Установите через: poetry add clearml"
            )

        self.project_name = project_name

    def register_model(
        self,
        model_path: str | Path,
        model_name: str,
        task_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> OutputModel:
        """
        Зарегистрировать модель в ClearML.

        Args:
            model_path: Путь к файлу модели
            model_name: Имя модели
            task_id: ID задачи, связанной с моделью
            metadata: Метаданные модели
            tags: Теги модели

        Returns:
            Объект OutputModel
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Модель не найдена: {model_path}")

        # Получаем задачу, если указан task_id
        task = None
        if task_id:
            task = Task.get_task(task_id=task_id)

        output_model = OutputModel(task=task, name=model_name)
        output_model.update_weights(weights_filename=str(model_path))

        if metadata:
            # Преобразуем метаданные в формат, ожидаемый ClearML
            # set_all_metadata ожидает Dict[key, Dict[value, type]]
            # Используем set_metadata для каждого ключа
            for key, value in metadata.items():
                # Преобразуем значение в строку, если это не строка
                if isinstance(value, dict | list):
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                output_model.set_metadata(key=key, value=value_str)

        if tags:
            output_model.add_tags(tags)

        return output_model

    def compare_models(self, model_ids: list[str]) -> dict[str, dict[str, Any]]:
        """
        Сравнить модели по метаданным.

        Args:
            model_ids: Список ID моделей для сравнения

        Returns:
            Словарь с метаданными моделей
        """
        models_data: dict[str, dict[str, Any]] = {}

        for model_id in model_ids:
            model = OutputModel(model_id=model_id)
            models_data[model_id] = {
                "name": model.name,
                "metadata": model.metadata,
                "tags": model.tags,
                "created": model.created,
            }

        return models_data


def create_clearml_pipeline(
    pipeline_name: str,
    project_name: str = "Engineering Practices ML",
) -> PipelineController:
    """
    Создать ClearML пайплайн.

    Args:
        pipeline_name: Название пайплайна
        project_name: Название проекта

    Returns:
        Контроллер пайплайна
    """
    if PipelineController is None:
        raise ImportError("ClearML не установлен. Установите через: poetry add clearml")

    pipeline = PipelineController(
        name=pipeline_name,
        project=project_name,
        version="1.0.0",
    )

    return pipeline


if __name__ == "__main__":
    # Пример использования ClearMLTracker
    tracker = ClearMLTracker(
        project_name="Engineering Practices ML",
        task_name="experiment_001",
        tags=["ridge", "training"],
    )

    # Логирование параметров
    tracker.log_params({"alpha": 1.0, "max_depth": 10})

    # Логирование метрик
    tracker.log_metrics({"test_r2": 0.85, "test_rmse": 0.5})

    # Логирование артефактов (если файл существует)
    model_path = Path("models/model.pkl")
    if model_path.exists():
        tracker.log_artifact(str(model_path))

    tracker.close()
    print("✅ Пример использования ClearMLTracker выполнен")
