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


def create_ml_pipeline() -> PipelineController:
    """
    Создать ML пайплайн в ClearML.

    Returns:
        Контроллер пайплайна
    """
    pipeline = create_clearml_pipeline(
        pipeline_name="ML Training Pipeline",
        project_name="Engineering Practices ML",
    )

    # Стадия 1: Подготовка данных
    prepare_data_step = pipeline.add_step(
        name="prepare_data",
        base_task_project="Engineering Practices ML",
        base_task_name="prepare_data_template",
        parameter_override={
            "General/script_path": "scripts/data/prepare_data.py",
            "General/script_arguments": ["--config", "config/train_params.yaml"],
        },
    )

    # Стадия 2: Валидация данных
    pipeline.add_step(
        name="validate_data",
        base_task_project="Engineering Practices ML",
        base_task_name="validate_data_template",
        parents=[prepare_data_step],
        parameter_override={
            "General/script_path": "scripts/data/validate_data.py",
            "General/script_arguments": ["--config", "config/train_params.yaml"],
        },
    )

    # Стадия 3: Обучение модели
    train_model_step = pipeline.add_step(
        name="train_model",
        base_task_project="Engineering Practices ML",
        base_task_name="train_model_template",
        parents=[prepare_data_step],
        parameter_override={
            "General/script_path": "scripts/clearml/train_with_clearml.py",
            "General/script_arguments": [
                "--config",
                "config/train_params.yaml",
                "--model-type",
                "${pipeline.model_type}",
            ],
        },
    )

    # Стадия 4: Оценка модели
    pipeline.add_step(
        name="evaluate_model",
        base_task_project="Engineering Practices ML",
        base_task_name="evaluate_model_template",
        parents=[train_model_step],
        parameter_override={
            "General/script_path": "scripts/models/evaluate_model.py",
            "General/script_arguments": ["--config", "config/train_params.yaml"],
        },
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

    # Создаем пайплайн
    pipeline = create_ml_pipeline()

    # Устанавливаем параметры
    pipeline.set_parameter("model_type", args.model_type)

    # Запускаем пайплайн
    print(f"🚀 Запуск ClearML пайплайна с моделью: {args.model_type}")
    pipeline.start(queue=args.queue)

    print("✅ Пайплайн запущен!")
    print(f"📊 Отслеживание: {pipeline.get_output_log_web_page()}")


if __name__ == "__main__":
    main()
