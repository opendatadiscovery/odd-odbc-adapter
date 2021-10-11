import logging

import pyodbc
from odd_contract.models import DataEntity
from oddrn_generator import OdbcGenerator
from pyodbc import Connection, Cursor

from .mappers.tables import map_table


class OdbcAdapter:
    __connection: Connection = None
    __cursor: Cursor = None

    # replace
    def __init__(self, config) -> None:
        # https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
        # https://github.com/mkleehammer/pyodbc/wiki/Install
        # https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux
        # cat /etc/odbcinst.ini
        self.__driver: str = config['ODD_DRIVER']
        self.__host: str = config['ODD_HOST']
        self.__port: str = config['ODD_PORT']
        self.__database: str = config['ODD_DATABASE']
        self.__user: str = config['ODD_USER']
        self.__password: str = config['ODD_PASSWORD']
        self.__data_source: str = f"DRIVER={self.__driver};SERVER={self.__host};DATABASE={self.__database};" \
                                  f"UID={self.__user};PWD={self.__password}"
        self.__oddrn_generator = OdbcGenerator(host_settings=f"{self.__host}:{self.__port}", databases=self.__database)

    def get_data_source_oddrn(self) -> str:
        return self.__oddrn_generator.get_data_source_oddrn()

    def get_datasets(self) -> list[DataEntity]:
        try:
            self.__connect()

            tables_cursor: Cursor = self.__cursor.tables(catalog=self.__database)

            # excluding system tables
            tables = list(filter(lambda t: t.table_schem not in ['INFORMATION_SCHEMA', 'sys', ], tables_cursor))

            columns: list = []
            for table in tables:
                columns_cursor: Cursor = self.__cursor.columns(catalog=self.__database, table=table[2])
                columns.extend(columns_cursor.fetchall())

            tables.sort(key=lambda row: "[{}].[{}].[{}]".format(row[0], row[1], row[2]))
            columns.sort(key=lambda row: "[{}].[{}].[{}].[{:>9}]".format(row[0], row[1], row[2], row[16]))

            return map_table(self.__oddrn_generator, tables, columns)
        except Exception as e:
            logging.error("Failed to load metadata for tables")
            logging.exception(e)
        finally:
            self.__disconnect()
        return []

    # replace
    def __connect(self):
        try:
            self.__connection = pyodbc.connect(self.__data_source)
            self.__cursor = self.__connection.cursor()
        except Exception as e:
            logging.error(e)
            raise DBException("Database error")

    # replace
    def __disconnect(self):
        try:
            if self.__cursor:
                self.__cursor.close()
        except Exception:
            pass
        try:
            if self.__connection:
                self.__connection.close()
        except Exception:
            pass
        return


class DBException(Exception):
    pass
