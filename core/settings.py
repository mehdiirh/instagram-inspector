import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


def env_literal(key, _default=None):
    value = os.environ.get(key, _default)
    if value != _default:
        return eval(str(value))
    return value


def env_default(key, default):
    value = os.environ.get(key, default)
    if value:
        return value
    return default


def env_error(key):
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"{key} environment variable not found")
    return value


def env_list(key):
    value = os.environ.get(key)
    if value:
        return value.split(",")
    return []


# Instagram Configurations
INSTAGRAM_PROXY_LINK = env_default("INSTAGRAM_PROXY_LINK", None)
INSTAGRAM_PROXY_USE = env_literal("INSTAGRAM_PROXY_USE", False)

# Telegram Configurations
TELEGRAM_BOT_USERNAME = env_error("TELEGRAM_BOT_USERNAME")
TELEGRAM_BOT_TOKEN = env_error("TELEGRAM_BOT_TOKEN")
TELEGRAM_LOG_CHANNEL = env_error("TELEGRAM_LOG_CHANNEL")
TELEGRAM_API_ID = env_error("TELEGRAM_API_ID")
TELEGRAM_API_HASH = env_error("TELEGRAM_API_HASH")
