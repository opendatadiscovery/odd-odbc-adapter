import logging
from datetime import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from .adapter import OdbcAdapter
from .cache import Cache


class Scheduler:
    def __init__(self, adapter: OdbcAdapter, cache: Cache) -> None:
        self.__adapter = adapter
        self.__cache = cache
        self.__scheduler = BackgroundScheduler(executors={"default": ThreadPoolExecutor(1)})

    def start_scheduler(self, interval_minutes: int):
        self.__scheduler.start()
        self.__scheduler.add_job(self.__retrieve_data_entities,
                                 trigger="interval",
                                 minutes=interval_minutes,
                                 next_run_time=datetime.now())

    def __retrieve_data_entities(self):
        datasets = self.__adapter.get_datasets()
        self.__cache.cache_data_entities(datasets, [], [])
        logging.info(f"Put {len(datasets)} DataEntities from database to cache")
