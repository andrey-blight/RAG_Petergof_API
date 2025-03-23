import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM")


settings = Settings()
