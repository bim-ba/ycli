# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.


from pydantic import Field

from ycli.yandex.models import RequestBody


class GetLakehouseOperationArgs(RequestBody):
    operation_id: str = Field(
        ..., alias="operationId", description="ID of the operation to return."
    )
