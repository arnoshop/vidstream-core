import os
from dotenv import load_dotenv

load_dotenv()


def get_env_value(key_name, default_value):
    raw_val = os.getenv(key_name)
    if raw_val is None:
        return default_value

    cleaned = raw_val.strip()
    if cleaned == "":
        return default_value

    return cleaned


class AppConfig:
    def __init__(self):
        self.app_name = get_env_value("APP_NAME", "VidStreamCore")
        self.app_env = get_env_value("APP_ENV", "development")
        self.secret_key = get_env_value("SECRET_KEY", "")
        self.database_url = get_env_value("DATABASE_URL", "sqlite:///./vidstream.db")
        self.vast_preroll_url = get_env_value("VAST_PREROLL_URL", "")

    def is_dev(self):
        if self.app_env.lower() == "development":
            return True
        return False


settings = AppConfig()