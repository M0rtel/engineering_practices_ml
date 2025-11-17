"""Скрипт для управления моделями в ClearML."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from clearml import OutputModel  # noqa: E402

from src.data_science_project.clearml_tracker import ClearMLModelManager  # noqa: E402


def register_model(
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
    manager = ClearMLModelManager()
    return manager.register_model(
        model_path=model_path,
        model_name=model_name,
        task_id=task_id,
        metadata=metadata,
        tags=tags,
    )


def list_models(project_name: str = "Engineering Practices ML") -> list[dict[str, Any]]:
    """
    Получить список моделей проекта.

    Args:
        project_name: Название проекта

    Returns:
        Список моделей
    """
    models = OutputModel.query_models(project_name=project_name)

    models_list = []
    for model in models:
        models_list.append(
            {
                "id": model.id,
                "name": model.name,
                "created": str(model.created),
                "tags": model.tags,
                "metadata": model.metadata,
            }
        )

    return models_list


def compare_models(model_ids: list[str]) -> dict[str, dict[str, Any]]:
    """
    Сравнить модели.

    Args:
        model_ids: Список ID моделей

    Returns:
        Словарь с метаданными моделей
    """
    manager = ClearMLModelManager()
    return manager.compare_models(model_ids)


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Управление моделями в ClearML")
    parser.add_argument(
        "--register",
        type=str,
        help="Зарегистрировать модель (путь к файлу)",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Имя модели",
    )
    parser.add_argument(
        "--task-id",
        type=str,
        help="ID задачи, связанной с моделью",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        help="Метаданные модели (JSON строка)",
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        help="Теги модели",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показать список всех моделей",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="Engineering Practices ML",
        help="Название проекта",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        help="ID моделей для сравнения",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Экспортировать результаты в JSON файл",
    )
    args = parser.parse_args()

    if args.register:
        if not args.name:
            print("❌ Ошибка: необходимо указать --name для регистрации модели")
            return

        model_path = Path(args.register)
        if not model_path.exists():
            print(f"❌ Ошибка: файл модели не найден: {model_path}")
            return

        metadata = None
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("❌ Ошибка: неверный формат JSON для метаданных")
                return

        print(f"📦 Регистрация модели: {args.name}")
        model = register_model(
            model_path=model_path,
            model_name=args.name,
            task_id=args.task_id,
            metadata=metadata,
            tags=args.tags,
        )
        print(f"✅ Модель зарегистрирована с ID: {model.id}")

    elif args.list:
        print(f"📊 Список моделей проекта '{args.project}':")
        models = list_models(project_name=args.project)

        if not models:
            print("  Нет моделей")
            return

        for model in models:
            print(f"\n  ID: {model['id']}")
            print(f"  Название: {model['name']}")
            print(f"  Создан: {model['created']}")
            if model.get("tags"):
                print(f"  Теги: {', '.join(model['tags'])}")

        if args.export:
            with open(args.export, "w") as f:
                json.dump(models, f, indent=2)
            print(f"\n✅ Результаты экспортированы в {args.export}")

    elif args.compare:
        print(f"🔍 Сравнение моделей: {', '.join(args.compare)}")
        comparison = compare_models(args.compare)

        for model_id, data in comparison.items():
            print(f"\n📊 Модель {model_id}:")
            print(f"  Название: {data['name']}")
            print(f"  Создан: {data['created']}")
            if data.get("tags"):
                print(f"  Теги: {', '.join(data['tags'])}")
            if data.get("metadata"):
                print(f"  Метаданные: {json.dumps(data['metadata'], indent=4)}")

        if args.export:
            with open(args.export, "w") as f:
                json.dump(comparison, f, indent=2)
            print(f"\n✅ Результаты сравнения экспортированы в {args.export}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
