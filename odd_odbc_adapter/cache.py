import logging
from datetime import datetime
from typing import List, Union, Iterable, Tuple

import pytz
from odd_models.models import DataEntity

CacheEntry = Tuple[List[DataEntity], datetime]


class Cache:
    __DATA_ENTITIES: CacheEntry = None

    def cache_data_entities(self,
                            data_entities: Iterable[DataEntity],
                            updated_at: datetime = datetime.now(tz=pytz.UTC)):
        self.__DATA_ENTITIES = list(data_entities), updated_at

    def retrieve_data_entities(self, changed_since: datetime = None) -> Union[CacheEntry, None]:
        if self.__DATA_ENTITIES is None:
            logging.warning("DataEntities cache has never been enriched")
            return None

        data_entities_filtered = [
            de
            for de in self.__DATA_ENTITIES[0]
            if de.updated_at is None or de.updated_at >= changed_since
        ] if changed_since else self.__DATA_ENTITIES[0]

        if data_entities_filtered is not None:
            logging.info(f"Get {len(data_entities_filtered)} DataEntities from cache")
        else:
            logging.info(f"Get empty DataEntities list from cache")

        return data_entities_filtered, self.__DATA_ENTITIES[1]
