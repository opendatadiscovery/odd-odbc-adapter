from datetime import datetime
from flask import Response
from typing import List, Tuple, Any, Dict

# import pytz
from odd_contract import ODDController
from odd_contract.encoder import JSONEncoder

from app.abstract_adapter import AbstractAdapter
from app.cache import Cache


class Controller(ODDController):
    __encoder = JSONEncoder()
    __empty_cache_response = Response(status=503, headers={"Retry-After": "30"})

    def __init__(self, adapter: AbstractAdapter, data_cache: Cache):
        self.__adapter = adapter
        self.__data_cache = data_cache

    def get_data_entities(self, changed_since: Dict[str, Any] = None):
        # try:
        #     changed_since = pytz.UTC.localize(datetime.strptime(changed_since["changed_since"], "%Y-%m-%dT%H:%M:%SZ")) \
        #         if changed_since["changed_since"] is not None and changed_since["changed_since"] != "" else None
        # except Exception:
        #     changed_since = None
        changed_since = None

        data_entities = self.__data_cache.retrieve_data_entities(changed_since)
        if data_entities is None:
            return self.__empty_cache_response
        return self.__build_response(data_entities)

    def __build_response(self, data: Tuple[List, datetime]):
        return Response(
            response=self.__encoder.encode({
                "data_source_oddrn": self.__adapter.get_data_source_oddrn(),
                "items": data[0]
            }),
            headers={"Last-Modified": data[1].strftime("%a, %d %b %Y %H:%M:%S GMT")},
            content_type="application/json",
            status=200
        )
