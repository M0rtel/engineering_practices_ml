"""ClearML Pipeline для ML workflow."""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from clearml import PipelineController  # noqa: E402

from src.data_science_project.clearml_tracker import (  # noqa: E402
    create_clearml_pipeline,
)


def create_ml_pipeline(queue: str = "default") -> PipelineController:
    """
    Создать ML пайплайн в ClearML.

    Args:
        queue: Очередь для выполнения узлов пайплайна

    Returns:
        Контроллер пайплайна
    """
    pipeline = create_clearml_pipeline(
        pipeline_name="ML Training Pipeline",
        project_name="Engineering Practices ML",
    )

    # Стадия 1: Подготовка данных
    pipeline.add_step(
        name="prepare_data",
        base_task_project="Engineering Practices ML",
        base_task_name="prepare_data_template",
        parameter_override={
            "General/script_path": "scripts/data/prepare_data.py",
            "General/script_arguments": ["--config", "config/train_params.yaml"],
        },
        execution_queue=queue,  # Устанавливаем очередь для узла
    )

    # Стадия 2: Валидация данных
    pipeline.add_step(
        name="validate_data",
        base_task_project="Engineering Practices ML",
        base_task_name="validate_data_template",
        parents=["prepare_data"],  # Используем строковое имя узла
        parameter_override={
            "General/script_path": "scripts/data/validate_data.py",
            "General/script_arguments": ["--config", "config/train_params.yaml"],
        },
        execution_queue=queue,  # Устанавливаем очередь для узла
    )

    # Стадия 3: Обучение модели
    pipeline.add_step(
        name="train_model",
        base_task_project="Engineering Practices ML",
        base_task_name="train_model_template",
        parents=["prepare_data"],  # Используем строковое имя узла
        parameter_override={
            "General/script_path": "scripts/clearml/train_with_clearml.py",
            "General/script_arguments": [
                "--config",
                "config/train_params.yaml",
                "--model-type",
                "${pipeline.model_type}",
            ],
        },
        execution_queue=queue,  # Устанавливаем очередь для узла
    )

    # Стадия 4: Оценка модели
    pipeline.add_step(
        name="evaluate_model",
        base_task_project="Engineering Practices ML",
        base_task_name="evaluate_model_template",
        parents=["train_model"],  # Используем строковое имя узла
        parameter_override={
            "General/script_path": "scripts/models/evaluate_model.py",
            "General/script_arguments": ["--config", "config/train_params.yaml"],
        },
        execution_queue=queue,  # Устанавливаем очередь для узла
    )

    # Параметры пайплайна
    pipeline.add_parameter(
        name="model_type",
        default="rf",
        description="Тип модели для обучения",
    )

    return pipeline


def main() -> None:
    """Главная функция."""
    import argparse

    parser = argparse.ArgumentParser(description="Создать и запустить ClearML пайплайн")
    parser.add_argument(
        "--model-type",
        type=str,
        default="rf",
        help="Тип модели для обучения",
    )
    parser.add_argument(
        "--queue",
        type=str,
        default="default",
        help="Очередь для выполнения пайплайна",
    )
    args = parser.parse_args()

    # Создаем пайплайн с указанием очереди для узлов
    pipeline = create_ml_pipeline(queue=args.queue)

    # Устанавливаем параметры пайплайна через Task
    # В ClearML параметры пайплайна устанавливаются через Task.connect()
    # после добавления через add_parameter()
    try:
        if hasattr(pipeline, "_task") and pipeline._task is not None:
            # Устанавливаем параметр через Task с префиксом "pipeline/"
            pipeline._task.connect({"pipeline/model_type": args.model_type})
            print(f"✅ Параметр model_type установлен: {args.model_type}")
        else:
            # Если Task недоступен, параметр будет использован из значения по умолчанию
            print(
                "ℹ️  Параметр model_type будет использован из значения по умолчанию: rf"
            )
    except Exception as e:
        print(f"⚠️  Не удалось установить параметр: {e}")
        print(
            "ℹ️  Будет использовано значение по умолчанию или значение из аргументов скрипта"
        )

    # Запускаем пайплайн
    print(f"🚀 Запуск ClearML пайплайна с моделью: {args.model_type}")
    pipeline.start(queue=args.queue)

    print("✅ Пайплайн запущен!")
    # Получаем URL для отслеживания пайплайна
    if hasattr(pipeline, "_task") and pipeline._task is not None:
        task_url = pipeline._task.get_output_log_web_page()
        print(f"📊 Отслеживание: {task_url}")
    else:
        print("📊 Отслеживание: Проверьте веб-интерфейс ClearML")


if __name__ == "__main__":
    main()
