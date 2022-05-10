from dataclasses import dataclass
import os


@dataclass
class Config:
    web_driver = os.environ.get("WEB_DRIVER")
    uprm_email = os.environ.get("UPRM_EMAIL")
    uprm_password = os.environ.get("UPRM_PASSWORD")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")

config = Config()
