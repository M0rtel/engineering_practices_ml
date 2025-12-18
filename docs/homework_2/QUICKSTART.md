## Быстрый старт: ДЗ 2 — DVC и версионирование данных/моделей

Этот `QUICKSTART.md` описывает только шаги, которые нужны для **воспроизведения ДЗ 2**.

Убедитесь, что файл `data/raw/WineQT.csv` присутствует в репозитории (или скачайте его из указанных в задании источников).

### 1. Инициализация и проверка DVC

Если DVC ещё не инициализирован:

```bash
dvc init --no-scm
```
![img.png](img.png)

Проверьте конфигурацию:

```bash
dvc version
dvc remote list
cat .dvc/config || echo "Конфиг DVC будет создан автоматически при настройке remote"
```

![img_1.png](img_1.png)

Подробности см. в `docs/homework_2/REPORT.md`, раздел «Настройка DVC».

### 2. Настройка локального remote (local storage)

```bash
mkdir -p storage/local
dvc remote add -d local storage/local
dvc remote list
```

![img_2.png](img_2.png)

### 3. Настройка MinIO (через docker-compose)

Запустите инфраструктуру (MinIO и остальные сервисы, если нужно):

```bash
docker compose up -d minio
```

![img_3.png](img_3.png)

Проверьте, что MinIO доступен по адресу `http://localhost:9000`:

- Логин: `minioadmin`
- Пароль: `minioadmin`

Затем добавьте MinIO как remote:

```bash
dvc remote add minio s3://engineering-practices-ml/dvc
dvc remote modify minio endpointurl http://localhost:9000
```

> При необходимости креденшелы для MinIO можно настроить через переменные окружения или `.dvc/config.local`.

### 4. Добавление данных в DVC

Добавьте датасет в DVC:

```bash
dvc add data/raw/WineQT.csv
git add data/raw/WineQT.csv.dvc
git commit -m "data: add WineQT dataset"
```

![img_4.png](img_4.png)

### 5. Запуск DVC pipeline

В репозитории уже настроен `dvc.yaml` с этапами:
- `prepare_data`
- `validate_data`
- `train_model`
- `evaluate_model`
- `monitor_pipeline`

Запуск всех стадий:

```bash
dvc repro
```

![img_5.png](img_5.png)

Проверка графа зависимостей:

```bash
dvc dag
```

![img_6.png](img_6.png)

### 6. Версионирование артефактов в remote

Отправьте данные и артефакты в настроенный remote:

```bash
dvc push
```

![img_7.png](img_7.png)

Для разных remote (local / minio / s3) можно использовать:

```bash
dvc push -r local
dvc push -r minio
```

### 7. Где смотреть результаты по ДЗ 2

- Описание настройки DVC и remote storage: `docs/homework_2/REPORT.md`
- Скриншоты: `docs/homework_2/screenshots/`
