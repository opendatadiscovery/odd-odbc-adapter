from odd_contract.models import DataEntity, DataSet, MetadataExtension
from adapter import _data_set_metadata_schema_url, MetadataNamedtuple, ColumnMetadataNamedtuple
from adapter.column import _map_column
from app.oddrn import generate_table_oddrn, generate_schema_oddrn


def _map_table(data_source_oddrn: str, tables: list[tuple], columns: list[tuple]) -> list[DataEntity]:
    data_entities: list[DataEntity] = []
    column_index: int = 0

    for table in tables:
        metadata: MetadataNamedtuple = MetadataNamedtuple(*table)

        table_catalog: str = metadata.table_cat
        table_schema: str = metadata.table_schem
        table_name: str = metadata.table_name

        schema_oddrn: str = generate_schema_oddrn(data_source_oddrn, table_catalog, table_schema)
        table_oddrn: str = generate_table_oddrn(data_source_oddrn, table_catalog, table_schema, table_name)

        data_entity: DataEntity = DataEntity()
        data_entities.append(data_entity)

        data_entity.oddrn = table_oddrn
        data_entity.name = table_name
        data_entity.owner = schema_oddrn

        data_entity.metadata = [MetadataExtension()]  # List[MetadataExtension]
        data_entity.metadata[0].schema_url = _data_set_metadata_schema_url
        data_entity.metadata[0].metadata = metadata._asdict()  # dict[str, object]

        # data_entity.created_at = metadata.create_time
        # data_entity.updated_at = metadata.update_time

        data_entity.dataset = DataSet()
        data_entity.dataset.parent_oddrn = schema_oddrn
        data_entity.dataset.description = metadata.remarks
        # data_entity.dataset.rows_number = metadata.table_rows
        data_entity.dataset.subtype = "DATASET_TABLE"
        data_entity.dataset.field_list = []

        while column_index < len(columns):
            column: tuple = columns[column_index]
            column_metadata: ColumnMetadataNamedtuple = ColumnMetadataNamedtuple(*column)

            if column_metadata.table_cat == table_catalog and \
                    column_metadata.table_schem == table_schema and \
                    column_metadata.table_name == table_name:
                data_entity.dataset.field_list.extend(_map_column(column_metadata, schema_oddrn, table_oddrn))
                column_index += 1
            else:
                break

    return data_entities
