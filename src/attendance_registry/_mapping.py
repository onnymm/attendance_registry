from pandas._typing import AstypeArg
from ._constants import (
    API_FIELD,
    COLUMN,
)

REASSIGNATION_NAMES = {
    API_FIELD.USER_ID: COLUMN.USER_ID,
    API_FIELD.NAME: COLUMN.NAME,
    API_FIELD.TIME: COLUMN.REGISTRY_TIME,
    API_FIELD.REGISTRY_TYPE: COLUMN.REGISTRY_TYPE,
    API_FIELD.DEVICE: COLUMN.DEVICE,
}

SELECTED_COLUMNS = [
    COLUMN.USER_ID,
    COLUMN.NAME,
    COLUMN.REGISTRY_TIME,
    COLUMN.REGISTRY_TYPE,
    COLUMN.DEVICE,
]

ASSIGNED_DTYPES: dict[str, AstypeArg] = {
    COLUMN.USER_ID: 'uint16',
    COLUMN.NAME: 'string[python]',
    COLUMN.REGISTRY_TIME: 'datetime64[s]',
    COLUMN.REGISTRY_TYPE: 'category',
    COLUMN.DEVICE: 'category',
}

CHARACTER_FORMATTING = {
    '帽': 'ñ',
    '铆': 'í',
    '煤': 'ú',
}
'Mapeo de corrección de caracteres'
