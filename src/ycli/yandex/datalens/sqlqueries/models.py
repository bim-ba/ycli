"""DataLens saved SQL query models: the public names of the generated classes it uses."""

from ycli.yandex.datalens.schemas.sql_queries import (
    CreateSqlQueryArgsParamsItemVariant1,
    CreateSqlQueryArgsParamsItemVariant2,
    CreateSqlQueryArgsParamsItemVariant3,
    SqlQuery,
    UpdateSqlQueryArgsParamsItemVariant1,
    UpdateSqlQueryArgsParamsItemVariant2,
    UpdateSqlQueryArgsParamsItemVariant3,
)
from ycli.yandex.datalens.schemas.sql_queries import CreateSqlQueryResult as SqlQueryCreated
from ycli.yandex.datalens.schemas.sql_queries import GetSqlQueryResult as SqlQueryDetails
from ycli.yandex.datalens.schemas.sql_queries import (
    RunSqlQueryArgsParamsValueVariant5 as SqlQueryInterval,
)
from ycli.yandex.datalens.schemas.sql_queries import RunSqlQueryResult as SqlQueryRun
from ycli.yandex.datalens.schemas.sql_queries import UpdateSqlQueryResult as SqlQuerySaved

#: A parameter of a new query: an interval of dates, one date, or a string, number or boolean.
SqlQueryNewParam = (
    CreateSqlQueryArgsParamsItemVariant1
    | CreateSqlQueryArgsParamsItemVariant2
    | CreateSqlQueryArgsParamsItemVariant3
)
#: A parameter of a query saved anew; the document describes it apart from a new one's.
SqlQuerySavedParam = (
    UpdateSqlQueryArgsParamsItemVariant1
    | UpdateSqlQueryArgsParamsItemVariant2
    | UpdateSqlQueryArgsParamsItemVariant3
)
#: The value a run gives a parameter: one value, several, or an interval.
SqlQueryValue = str | int | float | bool | list[str | int | float | bool] | SqlQueryInterval

__all__ = [
    "SqlQuery",
    "SqlQueryCreated",
    "SqlQueryDetails",
    "SqlQueryInterval",
    "SqlQueryNewParam",
    "SqlQueryRun",
    "SqlQuerySaved",
    "SqlQuerySavedParam",
    "SqlQueryValue",
]
