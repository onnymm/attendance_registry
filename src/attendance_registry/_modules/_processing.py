import pandas as pd
from .._constants import (
    API_FIELD,
    COLUMN,
)
from .._interface import _Base_Assistance
from .._mapping import (
    ASSIGNED_DTYPES,
    CHARACTER_FORMATTING,
    REASSIGNATION_NAMES,
    SELECTED_COLUMNS,
)
from .._typing import ColumnAssignation

class _Processing:

    def __init__(
        self,
        main: _Base_Assistance,
    ) -> None:

        # Asignación de instancia principal
        self._main = main

    def process_data(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:

        # Función de reasignación de tipo de dato a la columna de fecha y hora de registro
        _to_datetime64_s: ColumnAssignation = {
            COLUMN.REGISTRY_TIME: (
                lambda df: (
                    pd.to_datetime(df[COLUMN.REGISTRY_TIME])
                    # Se eliminan los datos del huso horario
                    .dt.tz_localize(None)
                    # Conversión a tipo de dato de fecha y hora
                    .astype('datetime64[s]')
                )
            )
        }

        return (
            data
            # Se descartan todos los registros que no sean registro de asistencia
            .pipe(lambda df: df[ (df[API_FIELD.NET_USER] != 'admin') & (df[API_FIELD.NAME] != '') ])
            # Se reasignan los nombres de columna
            .rename(columns= REASSIGNATION_NAMES)
            # Formateo de columna de fecha y hora
            .assign(**_to_datetime64_s)
            # Se corrigen símbolos
            .pipe(self._fix_symbols)
            # Selección de columnas
            [SELECTED_COLUMNS]
            # Asignación de tipos de dato
            .astype(ASSIGNED_DTYPES)
        )

    def _fix_symbols(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:

        # Función para reemplazo de caracteres
        def character_replace(
            value: str,
        ) -> str:

            # Iteración por cada caracter a reemplazar
            for ( i, o ) in CHARACTER_FORMATTING.items():
                # Reemplazo de caracteres
                value = value.replace(i, o)

            return value

        # Reasignación de columna con reemplazo de caracteres
        fix_values: ColumnAssignation = {
            COLUMN.NAME: (
                lambda df: (
                    df[COLUMN.NAME].apply(character_replace)
                )
            )
        }

        return (
            data
            .assign(**fix_values)
        )
