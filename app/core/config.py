import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    WB_PARSE_URL = os.environ.get("WB_PARSE_URL")
    WB_SUBSCRIBE_URL = os.environ.get("WB_SUBSCRIBE_URL")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    PARSER_URL = os.environ.get("PARSER_URL")
    API_PASSWORD = os.environ.get("API_PASSWORD")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM")
    API_USERNAME = os.environ.get("API_USERNAME")
    WEB_SOCKET = os.environ.get("WEB_SOCKET")


settings = Settings()
