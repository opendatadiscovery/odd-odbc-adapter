from odd_models.models import DataEntity, DataSet, MetadataExtension, DataEntityType
from oddrn_generator import OdbcGenerator

from . import _data_set_metadata_schema_url, MetadataNamedtuple, ColumnMetadataNamedtuple
from .columns import map_column
from .types import TABLE_TYPES_SQL_TO_ODD


def map_table(oddrn_generator: OdbcGenerator, tables: list[tuple], columns: list[tuple]) -> list[DataEntity]:
    data_entities: list[DataEntity] = []
    column_index: int = 0

    for table in tables:
        metadata: MetadataNamedtuple = MetadataNamedtuple(*table)

        table_schema: str = metadata.table_schem
        table_name: str = metadata.table_name

        oddrn_generator.set_oddrn_paths(schemas=table_schema, tables=table_name)

        schema_oddrn: str = oddrn_generator.get_oddrn_by_path("schemas")
        table_oddrn: str = oddrn_generator.get_oddrn_by_path("tables")

        data_entity: DataEntity = DataEntity(
            oddrn=table_oddrn,
            name=table_name,
            type=TABLE_TYPES_SQL_TO_ODD.get(metadata.table_type, DataEntityType.UNKNOWN),
            owner=schema_oddrn,
            metadata=[
                MetadataExtension(
                    schema_url=_data_set_metadata_schema_url,
                    metadata=metadata._asdict(),
                )
            ],
        )
        data_entities.append(data_entity)

        data_entity.dataset = DataSet(
            parent_oddrn=schema_oddrn,
            description=metadata.remarks,
            field_list=[]
        )

        while column_index < len(columns):
            column: tuple = columns[column_index]
            column_metadata: ColumnMetadataNamedtuple = ColumnMetadataNamedtuple(*column)

            if column_metadata.table_schem == table_schema and column_metadata.table_name == table_name:
                data_entity.dataset.field_list.append(map_column(column_metadata, oddrn_generator, data_entity.owner))
                column_index += 1
            else:
                break

    return data_entities
