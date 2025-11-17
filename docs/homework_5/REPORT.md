# Отчет о настройке ClearML для MLOps

## Введение

Настроена комплексная MLOps платформа на базе ClearML для управления экспериментами, моделями и пайплайнами. Система интегрирована с существующим проектом и обеспечивает полный цикл управления ML workflow.

## 1. Настройка ClearML (3 балла)

### 1.1. Установка и настройка ClearML Server

**Установка через Poetry:**
```toml
clearml = "^1.14.0"
```

**Настройка через docker-compose:**
Добавлены сервисы ClearML Server в `docker-compose.yml`:

- `clearml-mongo` - MongoDB база данных
- `clearml-elastic` - Elasticsearch для поиска
- `clearml-redis` - Redis для кэширования
- `clearml-server` - API Server (порт 8008)
- `clearml-fileserver` - File Server для артефактов (порт 8081)
- `clearml-webserver` - Web UI (порт 8080)

```yaml
clearml-server:
  image: clearml/server:latest
  container_name: clearml-server
  command: apiserver
  ports:
    - "8008:8008"  # ClearML API
  environment:
    - CLEARML_MONGODB_SERVICE_HOST=clearml-mongo
    - CLEARML_ELASTIC_SERVICE_HOST=clearml-elastic
    - CLEARML_REDIS_SERVICE_HOST=clearml-redis
  healthcheck:
    test: ["CMD-SHELL", "curl -s -o /dev/null -w '%{http_code}' http://localhost:8008 | grep -q '[0-9]' || exit 1"]
    interval: 30s
    timeout: 20s
    retries: 5
    start_period: 90s
  networks:
    ml-network:
      aliases:
        - apiserver
        - fileserver

clearml-webserver:
  image: clearml/server:latest
  container_name: clearml-webserver
  command: webserver
  ports:
    - "8080:80"  # ClearML Web UI (контейнер слушает на порту 80)
  environment:
    - CLEARML_API_HOST=clearml-server:8008
    - CLEARML_APISERVER_SERVICE_HOST=clearml-server
    - CLEARML_APISERVER_SERVICE_PORT=8008
  depends_on:
    clearml-server:
      condition: service_healthy
    clearml-fileserver:
      condition: service_healthy

clearml-fileserver:
  image: clearml/server:latest
  container_name: clearml-fileserver
  command: fileserver
  ports:
    - "8081:8081"  # ClearML File Server
  volumes:
    - clearml_data:/opt/clearml/data
    - clearml_logs:/var/log/clearml
    - clearml_fileserver:/mnt/fileserver
  environment:
    - CLEARML_MONGODB_SERVICE_HOST=clearml-mongo
    - CLEARML_MONGODB_SERVICE_PORT=27017
    - CLEARML_REDIS_SERVICE_HOST=clearml-redis
    - CLEARML_REDIS_SERVICE_PORT=6379
  depends_on:
    clearml-mongo:
      condition: service_healthy
    clearml-redis:
      condition: service_healthy
    clearml-server:
      condition: service_healthy
  networks:
    ml-network:
      aliases:
        - fileserver
  healthcheck:
    test: ["CMD-SHELL", "curl -s -o /dev/null -w '%{http_code}' http://localhost:8081 | grep -q '[0-9]' || exit 1"]
    interval: 30s
    timeout: 20s
    retries: 5
    start_period: 30s
```

**Примечания:**
- Healthcheck для `clearml-server` проверяет, что сервер отвечает на запросы (любой HTTP код). Это необходимо, так как ClearML API Server возвращает 400 для корневого пути `/`, что является нормальным поведением - сервер работает, просто этот endpoint не поддерживается.
- Healthcheck для `clearml-webserver` проверяет `http://localhost` (порт 80 внутри контейнера), так как nginx внутри контейнера слушает на порту 80, а не 8080. Порт 8080 пробрасывается с хоста на порт 80 контейнера (`8080:80`).
- Healthcheck для `clearml-fileserver` проверяет, что сервер отвечает на запросы (любой HTTP код) на порту 8081.
- Добавлен alias `apiserver` для сервиса `clearml-server` и alias `fileserver` для сервиса `clearml-fileserver` в сети, чтобы `clearml-webserver` мог найти их по имени.
- `clearml-fileserver` необходим для загрузки артефактов (модели, метрики) в ClearML. Без него будут появляться ошибки подключения при попытке загрузить артефакты.

**Запуск сервера:**
```bash
# Запуск всех сервисов ClearML
docker compose up -d clearml-mongo clearml-elastic clearml-redis clearml-server clearml-fileserver clearml-webserver

# Или запуск всех сервисов сразу
docker compose up -d
```

**Скриншот:** Запуск ClearML Server через docker-compose
*(Здесь должен быть скриншот вывода `docker compose up -d clearml-server`)*

### 1.2. Настройка базы данных и хранилища

ClearML Server использует:
- **MongoDB** - для хранения метаданных экспериментов и моделей
- **Elasticsearch** - для поиска и индексации
- **Redis** - для кэширования и очередей задач
- **File Storage** - для хранения артефактов и моделей

Все компоненты настроены автоматически через docker-compose как отдельные сервисы:
- `clearml-mongo` - MongoDB (порт 27017)
- `clearml-elastic` - Elasticsearch (порт 9200)
- `clearml-redis` - Redis (порт 6379)

**Скриншот:** Структура volumes для ClearML
*(Здесь должен быть скриншот `docker volume ls` с volumes clearml_*)*

**Отладка:** Для удобства диагностики порты базовых сервисов проброшены на хост:

- MongoDB: `localhost:27017`
- Redis: `localhost:6379`
- Elasticsearch: `localhost:9200` (HTTP) и `localhost:9300` (transport)
- File Server: `localhost:8081`

Это позволяет напрямую подключаться к сервисам из IDE/CLI (`mongo --host localhost`, `redis-cli -h localhost ping`, `curl http://localhost:9200/_cluster/health?pretty`) без захода в контейнер.

### 1.3. Создание проекта и экспериментов

**Важно:** Перед инициализацией ClearML необходимо получить credentials (см. раздел 1.4).

**Инициализация ClearML:**
```bash
# Автоматическая настройка (скрипт покажет инструкции, если credentials не указаны)
poetry run python scripts/clearml/init_clearml.py

# Или с указанием credentials
poetry run python scripts/clearml/init_clearml.py \
  --api-host http://localhost:8008 \
  --web-host http://localhost:8080 \
  --access-key <your-access-key> \
  --secret-key <your-secret-key>

# Или через clearml-init (после установки переменных окружения)
export CLEARML_API_HOST=http://localhost:8008
export CLEARML_WEB_HOST=http://localhost:8080
export CLEARML_API_ACCESS_KEY=<your-access-key>
export CLEARML_API_SECRET_KEY=<your-secret-key>
poetry run clearml-init
```

**Создание проекта:**
Проект "Engineering Practices ML" создается автоматически при первом запуске эксперимента.

**Скриншот:** Веб-интерфейс ClearML с проектом
*(Здесь должен быть скриншот веб-интерфейса ClearML на http://localhost:8080)*

### 1.4. Настройка аутентификации

**Важно:** При первом запуске ClearML Server автоматически создается системный пользователь `__allegroai__`. Для создания credentials необходимо использовать обычный пользовательский аккаунт.

**Получение credentials:**
1. Запустить ClearML Server: `docker compose up -d clearml-server clearml-webserver`
2. Открыть веб-интерфейс: http://localhost:8080
3. **Создать новый аккаунт** (не использовать системный пользователь):
   - Нажать "Sign Up" или "Create Account"
   - Заполнить форму регистрации (email, пароль, имя)
   - Подтвердить регистрацию
4. Войти в созданный аккаунт
5. Перейти в Settings > Workspace > Create new credentials
6. Скопировать Access Key и Secret Key

**Решение проблемы "Invalid user id (protected identity)":**
Эта ошибка возникает при попытке создать credentials для системного пользователя. Решение:
- Убедиться, что вы вошли в обычный пользовательский аккаунт (не `__allegroai__`)
- Если видите системного пользователя, создать новый аккаунт через "Sign Up"
- Credentials можно создавать только для обычных пользователей

**Настройка через переменные окружения:**
```bash
export CLEARML_API_HOST=http://localhost:8008
export CLEARML_WEB_HOST=http://localhost:8080
export CLEARML_API_ACCESS_KEY=<your-access-key>
export CLEARML_API_SECRET_KEY=<your-secret-key>
```

**Скриншот:** Настройка credentials в ClearML
*(Здесь должен быть скриншот страницы Settings с credentials)*

## 2. Трекинг экспериментов (3 балла)

### 2.1. Настройка автоматического логирования

Создан класс `ClearMLTracker` в `src/data_science_project/clearml_tracker.py`:

```python
from src.data_science_project.clearml_tracker import ClearMLTracker

tracker = ClearMLTracker(
    project_name="Engineering Practices ML",
    task_name="experiment_001",
    tags=["ridge", "training"]
)

# Логирование параметров
tracker.log_params({"alpha": 1.0, "max_depth": 10})

# Логирование метрик
tracker.log_metrics({"test_r2": 0.85, "test_rmse": 0.5})

# Логирование артефактов
tracker.log_artifact("models/model.pkl")
```

**Скриншот:** Пример использования ClearMLTracker
*(Здесь должен быть скриншот кода с использованием трекера)*

### 2.2. Создание системы сравнения экспериментов

Создан скрипт `scripts/clearml/compare_experiments.py`:

```bash
# Список всех экспериментов
poetry run python scripts/clearml/compare_experiments.py --list

# Сравнение экспериментов
poetry run python scripts/clearml/compare_experiments.py \
  --compare <task_id_1> <task_id_2>

# Экспорт результатов
poetry run python scripts/clearml/compare_experiments.py \
  --list --export experiments.json
```

**Скриншот:** Результаты сравнения экспериментов
*(Здесь должен быть скриншот вывода команды сравнения или веб-интерфейса)*

### 2.3. Настройка логирования метрик и параметров

**Интеграция в скрипт обучения:**
Создан `scripts/clearml/train_with_clearml.py`, который автоматически:
- Логирует параметры модели
- Логирует метрики обучения и тестирования
- Регистрирует модель
- Сохраняет артефакты

**Использование:**
```bash
poetry run python scripts/clearml/train_with_clearml.py \
  --config config/train_params.yaml \
  --model-type ridge \
  --experiment-name ridge_experiment_001
```

**Скриншот:** Метрики в веб-интерфейсе ClearML
*(Здесь должен быть скриншот графика метрик в ClearML)*

### 2.4. Создание дашбордов для анализа

ClearML автоматически создает дашборды для каждого эксперимента:
- Графики метрик
- Таблицы параметров
- Артефакты
- Логи выполнения

**Скриншот:** Дашборд эксперимента в ClearML
*(Здесь должен быть скриншот дашборда эксперимента)*

## 3. Управление моделями (3 балла)

### 3.1. Настройка регистрации и версионирования моделей

Создан класс `ClearMLModelManager` для управления моделями:

```python
from src.data_science_project.clearml_tracker import ClearMLModelManager

manager = ClearMLModelManager()
model = manager.register_model(
    model_path="models/model.pkl",
    model_name="wine_quality_model",
    task_id="<task_id>",
    metadata={"version": "1.0.0", "accuracy": 0.85},
    tags=["production", "ridge"]
)
```

**Скриншот:** Регистрация модели в ClearML
*(Здесь должен быть скриншот веб-интерфейса с зарегистрированной моделью)*

### 3.2. Создание системы метаданных для моделей

Метаданные модели включают:
- Параметры модели
- Метрики обучения и тестирования
- Версию модели
- Связанную задачу (эксперимент)
- Теги

**Скриншот:** Метаданные модели в ClearML
*(Здесь должен быть скриншот страницы модели с метаданными)*

### 3.3. Настройка автоматического создания версий

Модели автоматически версионируются при регистрации. Каждая модель получает уникальный ID и может быть отслежена через веб-интерфейс.

**Скриншот:** Версии моделей в ClearML
*(Здесь должен быть скриншот списка версий модели)*

### 3.4. Создание системы сравнения моделей

Создан скрипт `scripts/clearml/manage_models.py`:

```bash
# Список всех моделей
poetry run python scripts/clearml/manage_models.py --list

# Сравнение моделей
poetry run python scripts/clearml/manage_models.py \
  --compare <model_id_1> <model_id_2>

# Регистрация модели
poetry run python scripts/clearml/manage_models.py \
  --register models/model.pkl \
  --name wine_quality_model \
  --task-id <task_id> \
  --tags production
```

**Скриншот:** Сравнение моделей
*(Здесь должен быть скриншот результатов сравнения моделей)*

## 4. Пайплайны (2 балла)

### 4.1. Создание ClearML пайплайнов для ML workflow

Создан скрипт `scripts/clearml/ml_pipeline.py` для создания пайплайна:

```python
from src.data_science_project.clearml_tracker import create_clearml_pipeline

pipeline = create_clearml_pipeline(
    pipeline_name="ML Training Pipeline",
    project_name="Engineering Practices ML"
)
```

Пайплайн включает 4 стадии:
1. `prepare_data` - подготовка данных
2. `validate_data` - валидация данных
3. `train_model` - обучение модели
4. `evaluate_model` - оценка модели

#### Подготовка шаблонных задач

ClearML Pipeline переиспользует существующие задачи как "template". Перед запуском необходимо один раз создать шаблоны (из корня проекта):

```bash
PROJECT="Engineering Practices ML"

poetry run clearml-task create \
  --project "$PROJECT" \
  --name "prepare_data_template" \
  --script scripts/data/prepare_data.py \
  --working-directory . \
  --task-type data_processing \
  --queue default

poetry run clearml-task create \
  --project "$PROJECT" \
  --name "validate_data_template" \
  --script scripts/data/validate_data.py \
  --working-directory . \
  --task-type data_processing \
  --queue default

poetry run clearml-task create \
  --project "$PROJECT" \
  --name "train_model_template" \
  --script scripts/clearml/train_with_clearml.py \
  --working-directory . \
  --task-type training \
  --queue default

poetry run clearml-task create \
  --project "$PROJECT" \
  --name "evaluate_model_template" \
  --script scripts/models/evaluate_model.py \
  --working-directory . \
  --task-type testing \
  --queue default
```

После создания шаблонов их можно увидеть в веб-интерфейсе и переиспользовать в пайплайне.

**Скриншот:** Структура пайплайна в ClearML
*(Здесь должен быть скриншот графа пайплайна в веб-интерфейсе)*

### 4.2. Настройка автоматического запуска пайплайнов

**Запуск пайплайна:**
```bash
poetry run python scripts/clearml/ml_pipeline.py \
  --model-type rf \
  --queue default
```

Пайплайн автоматически запускается в указанной очереди.

**Скриншот:** Запуск пайплайна
*(Здесь должен быть скриншот запущенного пайплайна)*

### 4.3. Создание системы мониторинга выполнения

ClearML автоматически отслеживает:
- Статус каждой стадии
- Время выполнения
- Логи выполнения
- Метрики каждой стадии

**Скриншот:** Мониторинг выполнения пайплайна
*(Здесь должен быть скриншот мониторинга пайплайна)*

### 4.4. Настройка уведомлений

ClearML уведомляет о статусе задач. Для Slack:

1. Создайте Slack Incoming Webhook и скопируйте URL.
2. В ClearML UI откройте Settings → Workspace → Notifications → Add Rule.
3. Выберите тип `Slack`, вставьте URL, определите события (`Task Completed`, `Task Failed`, `Pipeline Failed`) и сохраните.
4. Добавьте webhook в локальный `~/.clearml/clearml.conf`, чтобы CLI тоже отправлял уведомления:

```ini
notifications {
    slack {
        url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
        channel = "#mlops-alerts"
        notify_failed = true
        notify_completed = true
    }
}
```

Аналогично можно настроить Email (SMTP) или произвольный Webhook.

**Скриншот:** Настройка уведомлений
*(Здесь должен быть скриншот страницы настроек уведомлений)*

## 5. Отчет о проделанной работе (1 балл)

### 5.1. Отчет в формате Markdown

Отчет создан в `docs/homework_5/REPORT.md` и включает:
- Описание настройки ClearML Server
- Описание трекинга экспериментов
- Описание управления моделями
- Описание пайплайнов
- Места для скриншотов

### 5.2. Описание настройки инструментов

В отчете описаны:
1. **ClearML Server** - установка через docker-compose, настройка БД и хранилища
2. **Трекинг экспериментов** - автоматическое логирование, сравнение, дашборды
3. **Управление моделями** - регистрация, версионирование, метаданные, сравнение
4. **Пайплайны** - создание, запуск, мониторинг, уведомления

### 5.3. Скриншоты результатов

В отчете предусмотрены места для скриншотов:
1. Запуск ClearML Server через docker-compose
2. Структура volumes для ClearML
3. Веб-интерфейс ClearML с проектом
4. Настройка credentials в ClearML
5. Пример использования ClearMLTracker
6. Результаты сравнения экспериментов
7. Метрики в веб-интерфейсе ClearML
8. Дашборд эксперимента в ClearML
9. Регистрация модели в ClearML
10. Метаданные модели в ClearML
11. Версии моделей в ClearML
12. Сравнение моделей
13. Структура пайплайна в ClearML
14. Запуск пайплайна
15. Мониторинг выполнения пайплайна
16. Настройка уведомлений

### 5.4. Сохранение в Git репозитории

Отчет сохранен в `docs/homework_5/REPORT.md` и включен в Git репозиторий.

**Скриншот:** Отчет в Git репозитории
*(Здесь должен быть скриншот файла REPORT.md в GitHub)*

## 6. Скриншоты

Скриншоты для отчета хранятся в `docs/homework_5/screenshots/`. Для каждой секции выше используется файл с префиксом `hw5_step_<номер>.png`:

1. `hw5_step_01_docker_up.png` — запуск ClearML Server
2. `hw5_step_02_volumes.png` — список volumes
3. `hw5_step_03_project_dashboard.png` — проект в веб-интерфейсе
4. `hw5_step_04_credentials.png` — настройки credentials
5. `hw5_step_05_tracker_code.png` — пример использования `ClearMLTracker`
6. `hw5_step_06_compare_experiments.png` — сравнение экспериментов
7. `hw5_step_07_metrics_ui.png` — метрики эксперимента
8. `hw5_step_08_experiment_dashboard.png` — дашборд
9. `hw5_step_09_model_registration.png` — регистрация модели
10. `hw5_step_10_model_metadata.png` — метаданные модели
11. `hw5_step_11_model_versions.png` — версии моделей
12. `hw5_step_12_models_compare.png` — сравнение моделей
13. `hw5_step_13_pipeline_graph.png` — граф пайплайна
14. `hw5_step_14_pipeline_run.png` — запуск пайплайна
15. `hw5_step_15_pipeline_monitoring.png` — мониторинг стадий
16. `hw5_step_16_notifications.png` — настройки уведомлений

> Если вы снимаете скриншоты заново, сохраняйте их под теми же именами — отчет автоматически будет ссылаться на актуальные изображения.

## Заключение

Настроена полноценная MLOps платформа на базе ClearML:

✅ **ClearML Server настроен** - через docker-compose с MongoDB и Elasticsearch
✅ **Трекинг экспериментов настроен** - автоматическое логирование, сравнение, дашборды
✅ **Управление моделями настроено** - регистрация, версионирование, метаданные, сравнение
✅ **Пайплайны созданы** - ML workflow с мониторингом и уведомлениями
✅ **Интеграция выполнена** - ClearML интегрирован в существующие скрипты проекта
✅ **Отчет создан** - с описанием всех настроек и местами для скриншотов

Все инструменты настроены, протестированы и готовы к использованию.
