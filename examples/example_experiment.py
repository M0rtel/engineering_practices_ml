"""Пример использования системы трекинга экспериментов."""


from src.data_science_project.experiment_tracker import (
    DVCExperimentTracker,
    experiment,
    track_experiment,
)

# Пример 1: Использование класса трекера
tracker = DVCExperimentTracker()

# Логирование параметров
tracker.log_params("exp_example_1", {"alpha": 1.0, "max_depth": 10})

# Логирование метрик
tracker.log_metrics("exp_example_1", {"test_r2": 0.85, "test_rmse": 0.5})

# Логирование артефакта
# tracker.log_artifact("exp_example_1", "models/model.pkl")


# Пример 2: Использование декоратора
@track_experiment(experiment_id="exp_example_2")
def train_model_example(alpha: float = 1.0, max_depth: int = 10) -> dict[str, float]:
    """Пример функции с автоматическим трекингом."""
    # Симуляция обучения модели
    metrics = {"test_r2": 0.87, "test_rmse": 0.48}
    return metrics


# Пример 3: Использование контекстного менеджера
def train_with_context() -> dict[str, float]:
    """Пример использования контекстного менеджера."""
    params = {"alpha": 1.0, "max_depth": 10}

    with experiment("exp_example_3", params=params) as tracker:
        # Код обучения модели
        metrics = {"test_r2": 0.86, "test_rmse": 0.49}
        tracker.log_metrics("exp_example_3", metrics)
        return metrics


# Пример 4: Сравнение экспериментов
def compare_examples() -> None:
    """Пример сравнения экспериментов."""
    tracker = DVCExperimentTracker()

    # Получить данные экспериментов
    tracker.get_experiment("exp_example_1")
    tracker.get_experiment("exp_example_2")

    # Сравнить
    comparison = tracker.compare_experiments("exp_example_1", "exp_example_2")
    print("Сравнение:", comparison)

    # Список всех экспериментов
    all_experiments = tracker.list_experiments()
    print("Все эксперименты:", all_experiments)


if __name__ == "__main__":
    # Запуск примеров
    print("Пример 1: Класс трекера")
    tracker = DVCExperimentTracker()
    tracker.log_params("exp_demo", {"alpha": 1.0})
    tracker.log_metrics("exp_demo", {"test_r2": 0.85})

    print("\nПример 2: Декоратор")
    result = train_model_example(alpha=1.0, max_depth=10)
    print(f"Результат: {result}")

    print("\nПример 3: Контекстный менеджер")
    result = train_with_context()
    print(f"Результат: {result}")

    print("\nПример 4: Сравнение")
    compare_examples()
