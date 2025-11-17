"""Скрипт для сравнения экспериментов в ClearML."""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Загружаем credentials из конфигурационного файла, если переменные окружения не установлены
if "CLEARML_API_ACCESS_KEY" not in os.environ:
    config_file = Path.home() / ".clearml" / "clearml.conf"
    if config_file.exists():
        # Парсим конфигурационный файл и устанавливаем переменные окружения
        with open(config_file) as f:
            content = f.read()
            # Извлекаем access_key
            access_key_match = re.search(r'"access_key"\s*=\s*"([^"]+)"', content)
            if access_key_match:
                os.environ["CLEARML_API_ACCESS_KEY"] = access_key_match.group(1)
            # Извлекаем secret_key
            secret_key_match = re.search(r'"secret_key"\s*=\s*"([^"]+)"', content)
            if secret_key_match:
                os.environ["CLEARML_API_SECRET_KEY"] = secret_key_match.group(1)
            # Извлекаем api_server host
            api_host_match = re.search(r'host\s*=\s*"([^"]+)"', content)
            if api_host_match:
                os.environ["CLEARML_API_HOST"] = api_host_match.group(1)
            # Извлекаем web_server host
            web_host_match = re.search(
                r'web_server\s*\{[^}]*host\s*=\s*"([^"]+)"', content, re.DOTALL
            )
            if web_host_match:
                os.environ["CLEARML_WEB_HOST"] = web_host_match.group(1)

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from clearml import Task  # noqa: E402


def compare_experiments(task_ids: list[str]) -> dict[str, Any]:
    """
    Сравнить эксперименты по их ID.

    Args:
        task_ids: Список ID задач (экспериментов)

    Returns:
        Словарь с результатами сравнения
    """
    experiments_data: dict[str, dict[str, Any]] = {}

    for task_id in task_ids:
        try:
            task = Task.get_task(task_id=task_id)
            experiments_data[task_id] = {
                "name": task.name,
                "status": task.status,
                "parameters": task.get_parameters(),
                "metrics": task.get_last_scalar_metrics(),
                "artifacts": [art.name for art in task.artifacts],
                "url": task.get_output_log_web_page(),
            }
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке задачи {task_id}: {e}")
            experiments_data[task_id] = {"error": str(e)}

    return experiments_data


def list_experiments(
    project_name: str = "Engineering Practices ML",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Получить список экспериментов проекта.

    Args:
        project_name: Название проекта
        limit: Максимальное количество экспериментов

    Returns:
        Список экспериментов
    """
    # Инициализируем временную задачу для получения сессии
    # Используем offline режим, чтобы не создавать новую задачу в ClearML
    temp_task = Task.init(
        project_name=project_name,
        task_name="temp_list_query",
        auto_connect_streams=False,
        auto_connect_frameworks=False,
        auto_connect_arg_parser=False,
        output_uri=None,
    )
    try:
        tasks = Task.get_tasks(project_name=project_name)
    finally:
        # Закрываем временную задачу
        temp_task.close()

    experiments = []
    for i, task in enumerate(tasks):
        if i >= limit:
            break
        try:
            # Получаем дату создания из метаданных задачи
            created_time = None
            if hasattr(task, "data"):
                created_time = (
                    task.data.created if hasattr(task.data, "created") else None
                )
            elif hasattr(task, "created"):
                created_time = task.created

            experiments.append(
                {
                    "id": task.id,
                    "name": task.name,
                    "status": task.status,
                    "created": str(created_time) if created_time else "N/A",
                    "url": task.get_output_log_web_page(),
                }
            )
        except Exception as e:
            print(f"⚠️ Ошибка при обработке задачи {task.id}: {e}")
            continue

    return experiments


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(description="Сравнение экспериментов ClearML")
    parser.add_argument(
        "--compare",
        nargs="+",
        help="ID задач для сравнения",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показать список всех экспериментов",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="Engineering Practices ML",
        help="Название проекта",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Максимальное количество экспериментов для списка",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Экспортировать результаты в JSON файл",
    )
    args = parser.parse_args()

    if args.list:
        print(f"📊 Список экспериментов проекта '{args.project}':")
        experiments = list_experiments(project_name=args.project, limit=args.limit)

        if not experiments:
            print("  Нет экспериментов")
            return

        for exp in experiments:
            print(f"\n  ID: {exp['id']}")
            print(f"  Название: {exp['name']}")
            print(f"  Статус: {exp['status']}")
            print(f"  Создан: {exp['created']}")
            print(f"  URL: {exp['url']}")

        if args.export:
            with open(args.export, "w") as f:
                json.dump(experiments, f, indent=2)
            print(f"\n✅ Результаты экспортированы в {args.export}")

    elif args.compare:
        print(f"🔍 Сравнение экспериментов: {', '.join(args.compare)}")
        comparison = compare_experiments(args.compare)

        for task_id, data in comparison.items():
            print(f"\n📊 Эксперимент {task_id}:")
            if "error" in data:
                print(f"  ❌ Ошибка: {data['error']}")
            else:
                print(f"  Название: {data['name']}")
                print(f"  Статус: {data['status']}")
                print(f"  URL: {data['url']}")
                if data.get("metrics"):
                    print("  Метрики:")
                    for metric_name, metric_value in data["metrics"].items():
                        print(f"    {metric_name}: {metric_value}")

        if args.export:
            with open(args.export, "w") as f:
                json.dump(comparison, f, indent=2)
            print(f"\n✅ Результаты сравнения экспортированы в {args.export}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
