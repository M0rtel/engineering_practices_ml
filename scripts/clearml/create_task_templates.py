"""Скрипт для создания шаблонных задач ClearML для пайплайна."""

import argparse
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Any  # noqa: E402

from clearml import Task  # noqa: E402


def create_task_template(
    project: str,
    name: str,
    script: str,
    task_type: str = "data_processing",
    queue: str | None = None,
) -> str:
    """
    Создать шаблонную задачу ClearML.

    Args:
        project: Название проекта
        name: Название задачи
        script: Путь к скрипту
        task_type: Тип задачи (data_processing, training, testing)
        queue: Очередь для выполнения (опционально)

    Returns:
        ID созданной задачи
    """
    # Проверяем существование скрипта
    script_path = Path(script)
    if not script_path.exists():
        raise FileNotFoundError(f"Скрипт не найден: {script}")

    # Создаем задачу с указанием скрипта и рабочей директории
    # Task.create() сам проверит конфигурацию ClearML
    try:
        task: Any = Task.create(
            project_name=project,
            task_name=name,
            task_type=task_type,
            script=str(script_path.absolute()),
            working_directory=str(project_root.absolute()),
            add_task_init_call=False,  # Не добавляем Task.init() автоматически
        )
    except Exception as e:
        error_msg = str(e)
        # Проверяем, запущен ли ClearML Server
        import subprocess  # noqa: S404  # nosec B404

        try:
            result = subprocess.run(  # nosec B603, B607
                ["docker", "compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            clearml_running = (
                "clearml-server" in result.stdout
                or "clearml-webserver" in result.stdout
            )
        except Exception:
            clearml_running = False

        if "not configured" in error_msg.lower() or "not setup" in error_msg.lower():
            instructions = []
            if not clearml_running:
                instructions.append(
                    "1. Запустите ClearML Server: docker compose up -d clearml-server clearml-webserver"
                )
                instructions.append("2. Дождитесь запуска сервисов (1-2 минуты)")
            else:
                instructions.append("1. ✅ ClearML Server запущен")

            instructions.extend(
                [
                    "2. Откройте веб-интерфейс: http://localhost:8080",
                    "3. Создайте НОВЫЙ пользовательский аккаунт (не используйте системный __allegroai__):",
                    "   - Нажмите 'Sign Up' или 'Create Account'",
                    "   - Заполните форму регистрации",
                    "4. Войдите в созданный аккаунт",
                    "5. Перейдите в Settings > Workspace > Create new credentials",
                    "6. Скопируйте Access Key и Secret Key",
                    "7. Настройте credentials:",
                    "   python scripts/clearml/init_clearml.py \\",
                    "     --api-host http://localhost:8008 \\",
                    "     --web-host http://localhost:8080 \\",
                    "     --access-key <your-access-key> \\",
                    "     --secret-key <your-secret-key>",
                    "",
                    "Или установите переменные окружения:",
                    "   export CLEARML_API_HOST=http://localhost:8008",
                    "   export CLEARML_WEB_HOST=http://localhost:8080",
                    "   export CLEARML_API_ACCESS_KEY=<your-access-key>",
                    "   export CLEARML_API_SECRET_KEY=<your-secret-key>",
                    "",
                    "Или используйте облачный ClearML: https://app.clear.ml",
                    "",
                    "Подробнее: https://clear.ml/docs",
                ]
            )

            raise RuntimeError(
                "ClearML не настроен на этой машине!\n\n" + "\n".join(instructions)
            ) from e
        # Если это другая ошибка, пробрасываем её дальше
        raise

    # Устанавливаем Docker окружение (опционально)
    # task.set_base_docker(
    #     docker_image="python:3.10",
    #     docker_arguments="",
    #     docker_setup_bash_script="pip install uv && uv sync --all-extras",
    # )

    # Примечание: Очередь для шаблонных задач можно установить позже в веб-интерфейсе
    # или при запуске через пайплайн. Для шаблонов очередь не критична.

    # Сохраняем как шаблон (завершаем задачу без выполнения)
    task.mark_started(False)
    task.mark_completed()

    task_id: str = str(task.id)  # Преобразуем в строку для типизации
    print(f"✅ Создана шаблонная задача: {name}")
    print(f"   ID: {task_id}")
    print(f"   Проект: {project}")
    print(f"   Скрипт: {script}")
    print(f"   Тип: {task_type}")
    if queue:
        print(f"   Очередь: {queue}")

    return task_id


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Создать шаблонные задачи ClearML для пайплайна"
    )
    parser.add_argument(
        "--project",
        type=str,
        default="Engineering Practices ML",
        help="Название проекта",
    )
    parser.add_argument(
        "--queue",
        type=str,
        default=None,
        help="Очередь для выполнения задач",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Создать все шаблонные задачи",
    )

    args = parser.parse_args()

    # Определяем задачи для создания
    tasks = [
        {
            "name": "prepare_data_template",
            "script": "scripts/data/prepare_data.py",
            "task_type": "data_processing",
        },
        {
            "name": "validate_data_template",
            "script": "scripts/data/validate_data.py",
            "task_type": "data_processing",
        },
        {
            "name": "train_model_template",
            "script": "scripts/clearml/train_with_clearml.py",
            "task_type": "training",
        },
        {
            "name": "evaluate_model_template",
            "script": "scripts/models/evaluate_model.py",
            "task_type": "testing",
        },
    ]

    if args.all:
        # Создаем все задачи
        print("🚀 Создание всех шаблонных задач...")
        task_ids = []
        for task_config in tasks:
            try:
                task_id = create_task_template(
                    project=args.project,
                    name=task_config["name"],
                    script=task_config["script"],
                    task_type=task_config["task_type"],
                    queue=args.queue,
                )
                task_ids.append(task_id)
            except (RuntimeError, FileNotFoundError) as e:
                # RuntimeError - ошибка конфигурации ClearML
                # FileNotFoundError - скрипт не найден
                print(f"❌ Ошибка при создании задачи {task_config['name']}: {e}")
                if isinstance(e, RuntimeError) and "не настроен" in str(e):
                    print(
                        "\n⚠️  Прерываем создание остальных задач из-за проблемы с конфигурацией ClearML"
                    )
                    break
                continue
            except Exception as e:
                print(f"❌ Ошибка при создании задачи {task_config['name']}: {e}")
                continue

        print(f"\n✅ Создано {len(task_ids)} шаблонных задач")
        print("\n📋 Список созданных задач:")
        for task_config, task_id in zip(tasks, task_ids, strict=False):
            print(f"  - {task_config['name']}: {task_id}")
    else:
        # Интерактивный режим
        print("Доступные задачи для создания:")
        for i, task_config in enumerate(tasks, 1):
            print(f"  {i}. {task_config['name']} ({task_config['task_type']})")

        choice = input("\nВыберите номер задачи (или 'all' для всех): ").strip()

        if choice.lower() == "all":
            # Создаем все задачи
            for task_config in tasks:
                try:
                    create_task_template(
                        project=args.project,
                        name=task_config["name"],
                        script=task_config["script"],
                        task_type=task_config["task_type"],
                        queue=args.queue,
                    )
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(tasks):
                    task_config = tasks[idx]
                    create_task_template(
                        project=args.project,
                        name=task_config["name"],
                        script=task_config["script"],
                        task_type=task_config["task_type"],
                        queue=args.queue,
                    )
                else:
                    print("❌ Неверный номер задачи")
            except ValueError:
                print("❌ Неверный ввод")


if __name__ == "__main__":
    main()
