"""Утилиты для работы с DVC."""

import json
import subprocess  # nosec B404
from pathlib import Path
from typing import Any


def track_data(data_path: str, message: str | None = None) -> None:
    """
    Добавить данные в DVC.

    Args:
        data_path: Путь к файлу данных
        message: Сообщение для коммита (опционально)
    """
    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Файл {data_path} не найден")

    # Добавляем файл в DVC
    subprocess.run(["dvc", "add", str(data_file)], check=True)  # nosec B603, B607
    print(f"✅ Файл {data_path} добавлен в DVC")


def track_model(
    model_path: str,
    metrics_path: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Добавить модель в DVC с метаданными.

    Args:
        model_path: Путь к файлу модели
        metrics_path: Путь к файлу с метриками (опционально)
        metadata: Дополнительные метаданные модели (опционально)
    """
    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(f"Файл модели {model_path} не найден")

    # Добавляем модель в DVC
    subprocess.run(["dvc", "add", str(model_file)], check=True)  # nosec B603, B607

    # Добавляем метрики, если указаны
    if metrics_path and Path(metrics_path).exists():
        subprocess.run(["dvc", "add", metrics_path], check=True)  # nosec B603, B607

    # Создаем файл метаданных
    metadata_file = Path(f"{model_path}.meta")
    model_metadata = {
        "model_name": model_file.name,
        "model_path": str(model_file),
        "metrics_path": metrics_path,
        **(metadata or {}),
    }
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(model_metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Модель {model_path} добавлена в DVC")
    print(f"✅ Метаданные сохранены в {metadata_file}")


def compare_versions(
    file_path: str, version1: str | None = None, version2: str | None = None
) -> dict[str, Any]:
    """
    Сравнить версии файла в DVC.

    Args:
        file_path: Путь к файлу
        version1: Первая версия (git commit/tag, опционально)
        version2: Вторая версия (git commit/tag, опционально)

    Returns:
        Словарь с результатами сравнения
    """
    cmd = ["dvc", "diff", file_path]
    if version1:
        cmd.extend([version1])
    if version2:
        cmd.extend([version2])

    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False
    )  # nosec B603, B607
    return {
        "file": file_path,
        "version1": version1 or "HEAD",
        "version2": version2 or "working tree",
        "diff": result.stdout,
        "changed": result.returncode == 0 and result.stdout.strip() != "",
    }


def pull_data(remote: str | None = None) -> None:
    """
    Загрузить данные из remote storage.

    Args:
        remote: Имя remote storage (опционально)
    """
    cmd = ["dvc", "pull"]
    if remote:
        cmd.extend(["--remote", remote])

    subprocess.run(cmd, check=True)  # nosec B603, B607
    print("✅ Данные загружены из remote storage")


def push_data(remote: str | None = None) -> None:
    """
    Отправить данные в remote storage.

    Args:
        remote: Имя remote storage (опционально)
    """
    cmd = ["dvc", "push"]
    if remote:
        cmd.extend(["--remote", remote])

    subprocess.run(cmd, check=True)  # nosec B603, B607
    print("✅ Данные отправлены в remote storage")
