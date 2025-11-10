"""Pydantic модели для конфигураций ML пайплайна."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    """Конфигурация данных."""

    target_column: str = Field(..., description="Название целевой переменной")
    feature_columns: list[str] = Field(..., description="Список признаков")
    test_size: float = Field(
        default=0.2, ge=0.0, le=1.0, description="Размер тестовой выборки"
    )
    random_state: int = Field(default=42, description="Seed для воспроизводимости")
    stratify: bool = Field(default=False, description="Стратификация при разделении")


class ModelParams(BaseModel):
    """Базовые параметры модели."""

    random_state: int | None = Field(
        default=42, description="Seed для воспроизводимости"
    )


class LinearModelParams(ModelParams):
    """Параметры линейных моделей."""

    fit_intercept: bool = Field(default=True, description="Использовать intercept")
    normalize: bool = Field(default=False, description="Нормализация данных")


class RidgeParams(LinearModelParams):
    """Параметры Ridge регрессии."""

    alpha: float = Field(default=1.0, gt=0.0, description="Параметр регуляризации")


class LassoParams(LinearModelParams):
    """Параметры Lasso регрессии."""

    alpha: float = Field(default=1.0, gt=0.0, description="Параметр регуляризации")


class ElasticNetParams(LinearModelParams):
    """Параметры ElasticNet регрессии."""

    alpha: float = Field(default=1.0, gt=0.0, description="Параметр регуляризации")
    l1_ratio: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Соотношение L1/L2"
    )


class KNNParams(ModelParams):
    """Параметры KNN."""

    n_neighbors: int = Field(default=5, ge=1, description="Количество соседей")
    weights: Literal["uniform", "distance"] = Field(
        default="uniform", description="Весовая функция"
    )
    algorithm: Literal["auto", "ball_tree", "kd_tree", "brute"] = Field(
        default="auto", description="Алгоритм поиска"
    )


class SVRParams(ModelParams):
    """Параметры SVR."""

    C: float = Field(default=1.0, gt=0.0, description="Параметр регуляризации")
    kernel: Literal["linear", "poly", "rbf", "sigmoid"] = Field(
        default="rbf", description="Тип ядра"
    )
    gamma: str | float = Field(default="scale", description="Параметр gamma")
    epsilon: float = Field(default=0.1, gt=0.0, description="Параметр epsilon")


class DecisionTreeParams(ModelParams):
    """Параметры Decision Tree."""

    max_depth: int | None = Field(
        default=None, ge=1, description="Максимальная глубина"
    )
    min_samples_split: int = Field(
        default=2, ge=2, description="Минимум образцов для разделения"
    )
    min_samples_leaf: int = Field(
        default=1, ge=1, description="Минимум образцов в листе"
    )
    criterion: Literal[
        "squared_error", "friedman_mse", "absolute_error", "poisson"
    ] = Field(default="squared_error", description="Критерий разделения")


class RandomForestParams(ModelParams):
    """Параметры Random Forest."""

    n_estimators: int = Field(default=100, ge=1, description="Количество деревьев")
    max_depth: int | None = Field(
        default=None, ge=1, description="Максимальная глубина"
    )
    min_samples_split: int = Field(
        default=2, ge=2, description="Минимум образцов для разделения"
    )
    min_samples_leaf: int = Field(
        default=1, ge=1, description="Минимум образцов в листе"
    )
    criterion: Literal[
        "squared_error", "absolute_error", "friedman_mse", "poisson"
    ] = Field(default="squared_error", description="Критерий разделения")


class AdaBoostParams(ModelParams):
    """Параметры AdaBoost."""

    n_estimators: int = Field(default=50, ge=1, description="Количество оценщиков")
    learning_rate: float = Field(default=1.0, gt=0.0, description="Скорость обучения")
    loss: Literal["linear", "square", "exponential"] = Field(
        default="linear", description="Функция потерь"
    )


class GradientBoostingParams(ModelParams):
    """Параметры Gradient Boosting."""

    n_estimators: int = Field(default=100, ge=1, description="Количество оценщиков")
    max_depth: int = Field(default=3, ge=1, description="Максимальная глубина")
    learning_rate: float = Field(default=0.1, gt=0.0, description="Скорость обучения")
    min_samples_split: int = Field(
        default=2, ge=2, description="Минимум образцов для разделения"
    )
    min_samples_leaf: int = Field(
        default=1, ge=1, description="Минимум образцов в листе"
    )


class ModelConfig(BaseModel):
    """Конфигурация модели."""

    model_type: Literal[
        "linear",
        "ridge",
        "lasso",
        "elasticnet",
        "knn",
        "svr",
        "dt",
        "rf",
        "ada",
        "gb",
    ] = Field(..., description="Тип модели")
    params: dict[str, Any] = Field(default_factory=dict, description="Параметры модели")


class TrainingConfig(BaseModel):
    """Конфигурация обучения."""

    data: DataConfig = Field(..., description="Конфигурация данных")
    model: ModelConfig | dict[str, Any] | None = Field(
        default=None, description="Конфигурация модели"
    )
    experiment_id: str | None = Field(default=None, description="ID эксперимента")


class PipelineConfig(BaseModel):
    """Полная конфигурация пайплайна."""

    pipeline_name: str = Field(default="ml_pipeline", description="Название пайплайна")
    training: TrainingConfig = Field(..., description="Конфигурация обучения")
    enable_feature_engineering: bool = Field(
        default=False, description="Включить feature engineering"
    )
    enable_validation: bool = Field(default=True, description="Включить валидацию")
    enable_monitoring: bool = Field(default=True, description="Включить мониторинг")
