# https://docs.microsoft.com/en-us/sql/t-sql/data-types/data-types-transact-sql?view=sql-server-ver15
# Exact numerics:
# tinyint, smallint, int, bigint, numeric, decimal, smallmoney, money, bit
# Approximate numerics:
# float, real
# Date and time:
# smalldatetime, datetime, datetime2, datetimeoffset, date, time
# Character strings:
# char, varchar, text
# Unicode character strings:
# nchar, nvarchar, ntext
# Binary strings:
# binary, varbinary, image
# Other data types:
# uniqueidentifier, sql_variant, xml, rowversion, hierarchyid, cursor, table,
# Spatial Geometry Types, Spatial Geography Types

TYPES_SQL_TO_ODD = {

    "tinyint": "TYPE_INTEGER",
    "smallint": "TYPE_INTEGER",
    "int": "TYPE_INTEGER",
    "bigint": "TYPE_INTEGER",
    "numeric": "TYPE_NUMBER",
    "decimal": "TYPE_NUMBER",
    "smallmoney": "TYPE_NUMBER",
    "money": "TYPE_NUMBER",
    "bit": "TYPE_BINARY",

    "float": "TYPE_NUMBER",
    "real": "TYPE_NUMBER",

    "smalldatetime": "TYPE_DATETIME",
    "datetime": "TYPE_DATETIME",
    "datetime2": "TYPE_DATETIME",
    "datetimeoffset": "TYPE_DATETIME",
    "date": "TYPE_DATETIME",
    "time": "TYPE_DATETIME",

    "char": "TYPE_CHAR",
    "varchar": "TYPE_STRING",
    "text": "TYPE_STRING",

    "nchar": "TYPE_CHAR",
    "nvarchar": "TYPE_STRING",
    "ntext": "TYPE_STRING",

    "binary": "TYPE_BINARY",
    "varbinary": "TYPE_BINARY",
    "image": "TYPE_BINARY",

    "uniqueidentifier": "TYPE_STRING",
    "xml": "TYPE_STRING"
    # Other data types
}
