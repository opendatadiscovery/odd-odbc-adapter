import logging
import pyodbc
from pyodbc import Connection, Cursor
from odd_contract.models import DataEntity
from adapter import _adapter_prefix
from adapter.table import _map_table
from app.abstract_adapter import AbstractAdapter
from config import get_env


def create_adapter() -> AbstractAdapter:
    return OdbcAdapter()


def sort_tables(row):
    return "[{}].[{}].[{}]".format(row[0], row[1], row[2])


def sort_columns(row):
    return "[{}].[{}].[{}].[{:>9}]".format(row[0], row[1], row[2], row[16])


class OdbcAdapter(AbstractAdapter):
    __cloud_prefix = ""
    __connection: Connection = None
    __cursor: Cursor = None

    # replace
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15
        # https://github.com/mkleehammer/pyodbc/wiki/Install
        # https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux
        # cat /etc/odbcinst.ini
        self.__driver: str = get_env("ODBCDRIVER", "ODBC Driver 17 for SQL Server")
        self.__host: str = get_env("ODBCHOST", "localhost")
        self.__database: str = get_env("ODBCDATABASE", "")
        self.__user: str = get_env("ODBCUSER", "")
        self.__password: str = get_env("ODBCPASSWORD", "")
        self.__data_source: str = f"DRIVER={self.__driver};SERVER={self.__host};DATABASE={self.__database};" \
                                  f"UID={self.__user};PWD={self.__password}"
        self.__data_source_oddrn: str = f"//{self.__cloud_prefix}{_adapter_prefix}{self.__host}"
        super().__init__()

    def get_data_source_oddrn(self) -> str:
        return self.__data_source_oddrn

    def get_datasets(self) -> list[DataEntity]:
        try:
            self.__connect()

            tables_cursor: Cursor = self.__cursor.tables()
            _table_metadata2: str = self.__get_metadata_from_cursor(tables_cursor)
            tables: list = tables_cursor.fetchall()

            columns_cursor: Cursor = self.__cursor.columns()
            _column_metadata2: str = self.__get_metadata_from_cursor(columns_cursor)
            columns: list = columns_cursor.fetchall()

            tables.sort(key=sort_tables)
            columns.sort(key=sort_columns)

            return _map_table(self.get_data_source_oddrn(), tables, columns)
        except Exception:
            logging.error("Failed to load metadata for tables")
            logging.exception(Exception)
        finally:
            self.__disconnect()
        return []

    def __get_metadata_from_cursor(self, tables_cursor: Cursor) -> str:
        names: list = []
        for table in tables_cursor.description:
            names.append(table[0])
        return ", ".join(names)

    def __query(self, columns: str, table: str, order_by: str) -> list[tuple]:
        return self.__execute(f"select {columns} from {table} order by {order_by}")

    def __execute(self, query: str) -> list[tuple]:
        self.__cursor.execute(query)
        records = self.__cursor.fetchall()
        return records

    # replace
    def __connect(self):
        try:

            self.__connection = pyodbc.connect(self.__data_source)
            self.__cursor = self.__connection.cursor()

        except Exception:
            logging.error(Exception)
            raise DBException("Database error")
        return

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
    def __init__(self, message: str) -> None:
        super().__init__(message)
