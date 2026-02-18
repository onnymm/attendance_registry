import pandas as pd
from typing import (
    Generic,
    Optional,
)
from ._types import (
    _T,
    _DateOrDateRange,
)

class _Base_Assistance(Generic[_T]):

    _URL = 'https://ius-team.hikcentralconnect.com/hcc/ccbdevicebiz/v1/custom/request'
    """
    URL del endpoint para obtención de registros de asistencia
    """
    _devices_data: dict[_T, str]
    """
    Datos de los dispositivos
    """
    _DATA_TITLES: dict
    """
    Títulos de datos finales
    """

    _DATA_TYPES: dict
    """
    Tipos de datos.
    """

    _DATA_ORDER: list[str]
    """
    Orden de columnas de DataFrames.
    """

    _CHARACTER_FORMATTING: dict[str, str]
    """
    Mapeo de formato de caracteres.
    """

    def get_today_attendance(
        self,
        device: Optional[_T] = None
    ) -> pd.DataFrame:
        """
        #### Obtención de los registros de asistencia del hoy
        Este método obtiene los registros de asistencia del día de hoy, ya sea de un dispositivo
        especificado o de todos los dispositivos.

        Uso:
        >>> # Obtención de los registros del día de hoy
        >>> data = instance.get_today_attendance()
        >>> 
        >>> # Obtención de los registros del día de hoy por dispositivo específico
        >>> data = instance.get_today_attendance('my_device_name')
        """
        ...

    def get_daily_attendance(
        self,
        date_or_range: _DateOrDateRange,
        device: _T | None = None
    ) -> pd.DataFrame:
        """
        #### Obtención de registros diarios de asistencia
        Este método obtiene todos los registros de asistencia de un día especificado o
        un rango de fecha especificado con granularidad de día y opcionalmente
        especificando un dispositivo.

        Uso:
        >>> # Obtención de los registros de un día especificado
        >>> data = instance.get_daily_attendance('2025-08-21')
        >>> 
        >>> # Obtención de los registros de un rango de fecha
        >>> data = instance.get_daily_attendance(('2025-08-01', '2025-08-31'))
        >>> 
        >>> # Obtención de los registros de un día por dispositivo específico
        >>> data = instance.get_today_attendance('2025-08-21', 'my_device_name')
        """
        ...
