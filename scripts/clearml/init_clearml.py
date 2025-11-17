"""Скрипт для инициализации ClearML."""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def init_clearml(
    api_host: str | None = None,
    web_host: str | None = None,
    access_key: str | None = None,
    secret_key: str | None = None,
) -> None:
    """
    Инициализировать ClearML с указанными параметрами.

    Args:
        api_host: URL API сервера ClearML
        web_host: URL веб-интерфейса ClearML
        access_key: Access key для аутентификации
        secret_key: Secret key для аутентификации
    """
    # Используем переменные окружения или значения по умолчанию
    api_host = api_host or os.getenv("CLEARML_API_HOST", "http://localhost:8008")
    web_host = web_host or os.getenv("CLEARML_WEB_HOST", "http://localhost:8080")
    access_key = access_key or os.getenv("CLEARML_API_ACCESS_KEY")
    secret_key = secret_key or os.getenv("CLEARML_API_SECRET_KEY")

    print("🔧 Инициализация ClearML...")
    print(f"  API Host: {api_host}")
    print(f"  Web Host: {web_host}")

    if not access_key or not secret_key:
        print("\n⚠️  Access key и Secret key не указаны.")
        print("Для получения credentials:")
        print(
            "  1. Запустите ClearML Server: docker compose up -d clearml-server clearml-webserver"
        )
        print("  2. Откройте веб-интерфейс: http://localhost:8080")
        print(
            "  3. Создайте НОВЫЙ пользовательский аккаунт (не используйте системный __allegroai__):"
        )
        print("     - Нажмите 'Sign Up' или 'Create Account'")
        print("     - Заполните форму регистрации")
        print("  4. Войдите в созданный аккаунт")
        print("  5. Перейдите в Settings > Workspace > Create new credentials")
        print("  6. Скопируйте Access Key и Secret Key")
        print("\n⚠️  Если возникает ошибка 'Invalid user id (protected identity)':")
        print(
            "   - Убедитесь, что вы вошли в обычный пользовательский аккаунт (не системный)"
        )
        print("   - Credentials можно создавать только для обычных пользователей")
        print("\nЗатем установите переменные окружения:")
        print("  export CLEARML_API_HOST=http://localhost:8008")
        print("  export CLEARML_WEB_HOST=http://localhost:8080")
        print("  export CLEARML_API_ACCESS_KEY=<your-access-key>")
        print("  export CLEARML_API_SECRET_KEY=<your-secret-key>")
        print("\nИли используйте команду:")
        print("  poetry run clearml-init")
        return

    # Создаем конфигурационный файл ClearML
    config_dir = Path.home() / ".clearml"
    config_dir.mkdir(exist_ok=True)
    config_file = config_dir / "clearml.conf"

    config_content = f"""api {{
    # ClearML Server API
    api_server {{
        host = "{api_host}"
    }}

    # ClearML Web Server
    web_server {{
        host = "{web_host}"
    }}

    # Authentication
    credentials {{
        "access_key" = "{access_key}"
        "secret_key" = "{secret_key}"
    }}
}}
"""

    with open(config_file, "w") as f:
        f.write(config_content)

    print(f"✅ Конфигурация ClearML сохранена в {config_file}")
    print("\nТеперь можно использовать ClearML для трекинга экспериментов!")


def main() -> None:
    """Главная функция."""
    import argparse

    parser = argparse.ArgumentParser(description="Инициализация ClearML")
    parser.add_argument(
        "--api-host",
        type=str,
        help="URL API сервера ClearML (по умолчанию из CLEARML_API_HOST)",
    )
    parser.add_argument(
        "--web-host",
        type=str,
        help="URL веб-интерфейса ClearML (по умолчанию из CLEARML_WEB_HOST)",
    )
    parser.add_argument(
        "--access-key",
        type=str,
        help="Access key для аутентификации (по умолчанию из CLEARML_API_ACCESS_KEY)",
    )
    parser.add_argument(
        "--secret-key",
        type=str,
        help="Secret key для аутентификации (по умолчанию из CLEARML_API_SECRET_KEY)",
    )
    args = parser.parse_args()

    init_clearml(
        api_host=args.api_host,
        web_host=args.web_host,
        access_key=args.access_key,
        secret_key=args.secret_key,
    )


if __name__ == "__main__":
    main()
