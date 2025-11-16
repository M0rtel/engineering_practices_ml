"""Утилиты для трекинга экспериментов с DVC."""

import json
import subprocess  # nosec B404
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar, cast


class DVCExperimentTracker:
    """Трекер экспериментов на основе DVC."""

    def __init__(self, experiments_dir: str = "experiments"):
        """
        Инициализация трекера.

        Args:
            experiments_dir: Директория для хранения экспериментов
        """
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)

    def log_params(self, experiment_id: str, params: dict[str, Any]) -> None:
        """
        Логировать параметры эксперимента.

        Args:
            experiment_id: ID эксперимента
            params: Словарь параметров
        """
        params_file = self.experiments_dir / f"{experiment_id}_params.json"
        with open(params_file, "w") as f:
            json.dump(params, f, indent=2)
        print(f"📝 Параметры сохранены: {params_file}")

    def log_metrics(self, experiment_id: str, metrics: dict[str, float]) -> None:
        """
        Логировать метрики эксперимента.

        Args:
            experiment_id: ID эксперимента
            metrics: Словарь метрик
        """
        metrics_file = self.experiments_dir / f"{experiment_id}_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"📊 Метрики сохранены: {metrics_file}")

    def log_artifact(self, experiment_id: str, artifact_path: str) -> None:
        """
        Логировать артефакт (модель, график и т.д.).

        Args:
            experiment_id: ID эксперимента
            artifact_path: Путь к артефакту
        """
        artifact_file = Path(artifact_path)
        if not artifact_file.exists():
            raise FileNotFoundError(f"Артефакт не найден: {artifact_path}")

        # Добавляем артефакт в DVC
        subprocess.run(
            ["dvc", "add", str(artifact_file)], check=True
        )  # nosec B603, B607
        print(f"📦 Артефакт добавлен в DVC: {artifact_path}")

    def get_experiment(self, experiment_id: str) -> dict[str, Any]:
        """
        Получить данные эксперимента.

        Args:
            experiment_id: ID эксперимента

        Returns:
            Словарь с данными эксперимента
        """
        params_file = self.experiments_dir / f"{experiment_id}_params.json"
        metrics_file = self.experiments_dir / f"{experiment_id}_metrics.json"

        experiment = {"experiment_id": experiment_id}

        if params_file.exists():
            with open(params_file) as f:
                experiment["params"] = json.load(f)

        if metrics_file.exists():
            with open(metrics_file) as f:
                experiment["metrics"] = json.load(f)

        return experiment

    def list_experiments(self) -> list[str]:
        """
        Получить список всех экспериментов.

        Returns:
            Список ID экспериментов
        """
        experiment_ids = set()
        for file in self.experiments_dir.glob("*_params.json"):
            experiment_id = file.stem.replace("_params", "")
            experiment_ids.add(experiment_id)
        return sorted(experiment_ids)

    def compare_experiments(
        self, experiment_id1: str, experiment_id2: str
    ) -> dict[str, Any]:
        """
        Сравнить два эксперимента.

        Args:
            experiment_id1: ID первого эксперимента
            experiment_id2: ID второго эксперимента

        Returns:
            Словарь с результатами сравнения
        """
        exp1 = self.get_experiment(experiment_id1)
        exp2 = self.get_experiment(experiment_id2)

        metrics_diff: dict[str, float] = {}
        if "metrics" in exp1 and "metrics" in exp2:
            for key in set(exp1["metrics"].keys()) | set(exp2["metrics"].keys()):
                val1 = exp1["metrics"].get(key, 0)
                val2 = exp2["metrics"].get(key, 0)
                metrics_diff[key] = val2 - val1

        comparison = {
            "experiment1": exp1,
            "experiment2": exp2,
            "metrics_diff": metrics_diff,
        }

        return comparison


# Глобальный экземпляр трекера
_tracker = DVCExperimentTracker()


@contextmanager
def experiment(
    experiment_id: str, params: dict[str, Any] | None = None
) -> Generator[DVCExperimentTracker, None, None]:
    """
    Контекстный менеджер для эксперимента.

    Args:
        experiment_id: ID эксперимента
        params: Параметры эксперимента
    """
    if params:
        _tracker.log_params(experiment_id, params)

    try:
        yield _tracker
    finally:
        pass


F = TypeVar("F", bound=Callable[..., Any])


def track_experiment(experiment_id: str | None = None) -> Callable[[F], F]:
    """
    Декоратор для автоматического трекинга эксперимента.

    Args:
        experiment_id: ID эксперимента (если None, генерируется автоматически)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import uuid

            exp_id = experiment_id or f"exp_{uuid.uuid4().hex[:8]}"

            # Извлекаем параметры из kwargs
            params = {k: v for k, v in kwargs.items() if not k.startswith("_")}

            with experiment(exp_id, params):
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Если функция возвращает метрики, логируем их
                if isinstance(result, dict) and any(
                    key in result for key in ["metrics", "test_r2", "train_r2"]
                ):
                    metrics = result if "metrics" not in result else result["metrics"]
                    _tracker.log_metrics(exp_id, metrics)

                return result

        return cast(F, wrapper)

    return decorator


def run_dvc_experiment(
    script_path: str, params_file: str, experiment_name: str
) -> None:
    """
    Запустить эксперимент через DVC.

    Args:
        script_path: Путь к скрипту
        params_file: Путь к файлу с параметрами
        experiment_name: Имя эксперимента
    """
    cmd = [
        "dvc",
        "exp",
        "run",
        "-n",
        experiment_name,
        "-S",
        f"params={params_file}",
        script_path,
    ]
    subprocess.run(cmd, check=True)  # nosec B603, B607
    print(f"✅ Эксперимент {experiment_name} запущен через DVC")


def list_dvc_experiments() -> list[str]:
    """
    Получить список экспериментов DVC.

    Returns:
        Список имен экспериментов
    """
    result = subprocess.run(
        ["dvc", "exp", "list"], capture_output=True, text=True, check=False
    )  # nosec B603, B607
    experiments = []
    for line in result.stdout.split("\n"):
        if line.strip():
            experiments.append(line.strip())
    return experiments


def compare_dvc_experiments(exp1: str, exp2: str) -> str:
    """
    Сравнить два эксперимента DVC.

    Args:
        exp1: Имя первого эксперимента
        exp2: Имя второго эксперимента

    Returns:
        Результаты сравнения
    """
    result = subprocess.run(
        ["dvc", "exp", "diff", exp1, exp2],
        capture_output=True,
        text=True,
        check=False,
    )  # nosec B603, B607
    return result.stdout
