"""Утилита для запуска DVC pipeline с изменением параметров."""

import argparse
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Any

import yaml

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def update_params_file(params_file: Path, updates: dict[str, str]) -> None:
    """
    Обновить параметры в params.yaml.

    Args:
        params_file: Путь к файлу params.yaml
        updates: Словарь с обновлениями параметров
    """
    # Загружаем текущие параметры
    with open(params_file) as f:
        params = yaml.safe_load(f) or {}

    # Обновляем параметры
    for key, value_str in updates.items():
        # Преобразуем значение в правильный тип
        value: Any
        if value_str.lower() == "true":
            value = True
        elif value_str.lower() == "false":
            value = False
        elif value_str.isdigit():
            value = int(value_str)
        else:
            try:
                value = float(value_str)
            except ValueError:
                value = value_str  # Оставляем как строку

        params[key] = value

    # Сохраняем обновленные параметры
    with open(params_file, "w") as f:
        yaml.dump(params, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Параметры обновлены в {params_file}")
    for key, value in updates.items():
        print(f"   {key} = {value}")


def run_dvc_repro(stages: list[str] | None = None, force: bool = False) -> None:
    """
    Запустить dvc repro.

    Args:
        stages: Список стадий для выполнения (None = все)
        force: Принудительно перезапустить стадии
    """
    cmd = ["dvc", "repro"]
    if force:
        cmd.append("--force")
    if stages:
        cmd.extend(stages)

    print(f"🔧 Выполнение: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)  # nosec B603, B607
    print("✅ Pipeline выполнен успешно!")


def main() -> None:
    """Главная функция."""
    parser = argparse.ArgumentParser(
        description="Запуск DVC pipeline с изменением параметров"
    )
    parser.add_argument(
        "stages",
        nargs="*",
        help="Стадии для выполнения (по умолчанию все)",
    )
    parser.add_argument(
        "-S",
        "--set-param",
        action="append",
        metavar="PARAM=VALUE",
        help="Установить параметр (можно использовать несколько раз)",
        dest="params",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Принудительно перезапустить стадии",
    )
    parser.add_argument(
        "--params-file",
        type=str,
        default="params.yaml",
        help="Путь к файлу params.yaml",
    )
    args = parser.parse_args()

    params_file = Path(args.params_file)

    # Парсим параметры из -S
    param_updates: dict[str, str] = {}
    if args.params:
        for param_str in args.params:
            if "=" not in param_str:
                print(
                    f"❌ Неверный формат параметра: {param_str}. Используйте PARAM=VALUE"
                )
                sys.exit(1)
            key, value = param_str.split("=", 1)
            param_updates[key] = value

    # Обновляем параметры, если указаны
    if param_updates:
        update_params_file(params_file, param_updates)

    # Запускаем dvc repro
    stages = args.stages if args.stages else None
    run_dvc_repro(stages=stages, force=args.force)


if __name__ == "__main__":
    main()
