import logging
import os
from typing import Any


class MissingEnvironmentVariable(Exception):
    pass


def get_env(env: str, default_value: Any = None) -> str:
    try:
        return os.environ[env]
    except KeyError:
        if default_value is not None:
            return default_value
        raise MissingEnvironmentVariable(f"{env} does not exist")


class BaseConfig:
    ODD_DRIVER = get_env('ODBC_DRIVER', 'ODBC Driver 17 for SQL Server')
    ODD_HOST = get_env('ODBC_HOST', 'localhost')
    ODD_PORT = get_env('ODBC_PORT', '1433')
    ODD_DATABASE = get_env('ODBC_DATABASE', '')
    ODD_USER = get_env('ODBC_USER', '')
    ODD_PASSWORD = get_env('ODBC_PASSWORD', '')

    SCHEDULER_INTERVAL_MINUTES = get_env('SCHEDULER_INTERVAL_MINUTES', 60)


class DevelopmentConfig(BaseConfig):
    FLASK_DEBUG = True


class ProductionConfig(BaseConfig):
    FLASK_DEBUG = False


def log_env_vars(config: dict):
    logging.info('Environment variables:')
    logging.info(f'ODD_DRIVER={config["ODD_DRIVER"]}')
    logging.info(f'ODBC_HOST={config["ODD_HOST"]}')
    logging.info(f'ODBC_PORT={config["ODD_PORT"]}')
    logging.info(f'ODBC_DATABASE={config["ODD_DATABASE"]}')
    logging.info(f'ODBC_USER={config["ODD_USER"]}')
    if config["ODD_PASSWORD"] != '':
        logging.info('ODBC_PASSWORD=***')
    logging.info(f'SCHEDULER_INTERVAL_MINUTES={config["SCHEDULER_INTERVAL_MINUTES"]}')
