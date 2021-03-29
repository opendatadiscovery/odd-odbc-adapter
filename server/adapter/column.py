from odd_contract.models import DataSetField, DataSetFieldType, MetadataExtension, DataSetFieldStat
from adapter import _data_set_field_metadata_schema_url, ColumnMetadataNamedtuple
from adapter.type import TYPES_SQL_TO_ODD


def _map_column(column_metadata: ColumnMetadataNamedtuple,
                schema_oddrn: str, table_oddrn: str, parent_oddrn: str = None,
                is_key: bool = None, is_value: bool = None
                ) -> list[DataSetField]:
    result: list[DataSetField] = []

    name: str = column_metadata.column_name
    resource_name: str = "keys" if is_key else "values" if is_value else "subcolumns"

    dsf: DataSetField = DataSetField()

    dsf.oddrn = f"{table_oddrn}/columns/{name}" if parent_oddrn is None else f"{parent_oddrn}/{resource_name}/{name}"
    dsf.name = name
    dsf.owner = schema_oddrn

    dsf.metadata = [MetadataExtension()]  # List[MetadataExtension]
    dsf.metadata[0].schema_url = _data_set_field_metadata_schema_url
    dsf.metadata[0].metadata = __convert_bytes_to_str_in_dict(column_metadata._asdict())  # dict[str, object]

    dsf.parent_field_oddrn = parent_oddrn

    dsf.type = DataSetFieldType()
    data_type: str = __convert_bytes_to_str(column_metadata.type_name)
    dsf.type.type = TYPES_SQL_TO_ODD[data_type] if data_type in TYPES_SQL_TO_ODD else "TYPE_STRING"  # TYPE_UNKNOWN
    dsf.type.logical_type = __convert_bytes_to_str(column_metadata.type_name)
    dsf.type.is_nullable = True if column_metadata.is_nullable == "YES" else False

    dsf.is_key = bool(is_key)
    dsf.is_value = bool(is_value)
    dsf.default_value = __convert_bytes_to_str(column_metadata.column_def)
    dsf.description = __convert_bytes_to_str(column_metadata.remarks)

    dsf.stats = DataSetFieldStat()
    # DataSetFieldStat

    result.append(dsf)
    return result


def __convert_bytes_to_str(value: bytes or None) -> str or None:
    return value if type(value) is not bytes else value.decode("utf-8")


def __convert_bytes_to_str_in_dict(values: dict[str, object]) -> dict[str, object]:
    for key, value in values.items():
        if type(value) is bytes:
            values[key] = value.decode("utf-8")
    return values
