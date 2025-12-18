## Быстрый старт: ДЗ 5 — ClearML и MLOps

Этот `QUICKSTART.md` описывает, как запустить **ClearML-инфраструктуру и базовые сценарии из ДЗ 5**.

### 1. Базовая подготовка

```bash
git clone https://github.com/M0rtel/engineering_practices_ml.git
cd engineering_practices_ml

uv venv
source .venv/bin/activate

uv sync --all-extras
```

Убедитесь, что Docker и Docker Compose установлены.

### 2. Запуск ClearML Server через docker-compose

Запустите связку сервисов (MongoDB, Elasticsearch, Redis, ClearML API, File Server, Web UI, MinIO и т.д.):

```bash
docker compose up -d clearml-mongo clearml-elastic clearml-redis clearml-server clearml-fileserver clearml-webserver
```

Проверьте веб-интерфейс ClearML:

- Web UI: `http://localhost:8080`
- API: `http://localhost:8008`

### 3. Настройка учётной записи и credentials

1. Зайдите в ClearML Web UI (`http://localhost:8080`)
2. Создайте **обычного пользователя** (не системного)
3. В профиле пользователя сгенерируйте **Access Key / Secret Key**
4. Настройте креденшелы:

```bash
clearml-init
```

или заполните файл `~/.clearml/clearml.conf` вручную.

### 4. Инициализация проекта и проверка скриптов ClearML

Быстрый запуск инициализационного скрипта:

```bash
python scripts/clearml/init_clearml.py
```

Он проверит соединение с ClearML и поможет создать/проверить проект.

### 5. Запуск обучения с трекингом в ClearML

Скрипт обучения с логированием в ClearML:

```bash
python scripts/clearml/train_with_clearml.py --config config/train_params.yaml --model-type ridge
```

Выполняет:
- загрузку данных,
- обучение модели,
- логирование параметров и метрик через `ClearMLTracker`,
- регистрацию модели (через `ClearMLModelManager`, если настроено).

После запуска зайдите в Web UI и убедитесь, что:

- появился новый **Project**,
- видны **Tasks / Experiments**,
- отображаются графики метрик.

### 6. Управление моделями и пайплайнами ClearML

- Скрипт управления моделями: `scripts/clearml/manage_models.py`
- Скрипт пайплайна: `scripts/clearml/ml_pipeline.py`

Пример запуска пайплайна:

```bash
python scripts/clearml/ml_pipeline.py --model-type ridge --queue default
```

В Web UI после запуска появится ClearML Pipeline с узлами:
- `prepare_data`
- `validate_data`
- `train_model`
- `evaluate_model`

### 7. Где смотреть детали по ДЗ 5

- Описание настройки ClearML и сценариев: `docs/homework_5/REPORT.md`
- Скриншоты: `docs/homework_5/screenshots/`
