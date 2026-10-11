import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN: str = "8726295366:AAGbrr3OJCsbaDXp4xHIbAv775OCj5f86Zc"
    DB_URL: str = "sqlite+aiosqlite:///data/shifts.db"

config = Settings()