import pandas as pd
from datetime import date
from typing import Optional
from ._constants import COLUMN
from ._execution_context import _ExecutionContext
from ._interface import _Base_Assistance
from ._resources import _DeviceInfo
from ._settings import CONFIG
from ._mapping import (
    SELECTED_COLUMNS,
    ASSIGNED_DTYPES,
)
from ._modules import (
    _API,
    _Params,
    _Processing,
)
from ._typing import (
    _D,
    AccessEvent,
    AccessEventInfo,
    DateOrDateRange,
)

class Assistance(_Base_Assistance[_D]):

    def __init__(
        self,
        devices: dict[_D, str],
    ) -> None:

        # Se guardan los datos de los dispositivos
        self._devices_data = devices

        # Inicialización de módulos
        self._api = _API(self)
        self._params = _Params(self)
        self._processing = _Processing(self)

    def get_today_attendance(
        self,
        device: Optional[_D] = None,
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

        # Obtención de la fecha del día de hoy
        date_day = date.today()
        # Obtención de los registros de asistencia del día
        data = self.get_daily_attendance(date_day, device)

        return data

    def get_daily_attendance(
        self,
        date_or_range: DateOrDateRange,
        device: Optional[_D] = None,
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

        # Inicialización de contexto de ejecución
        ctx = _ExecutionContext(self, date_or_range, device)

        # Inicialización de lista de DataFrames a concatenar para el resultado final
        attendance: list[pd.DataFrame] = []

        # Iteración por cada dispositivo
        for device_i in ctx.devices:
            # Obtención de los registros de asistencia del dispositivo i
            attendance_i = self._get_device_attendance_per_date_range(ctx, device_i)
            # Se añade el DataFrame obtenido a la lista de DataFrames por concatenar
            attendance.append(attendance_i)

        # Obtención de todos los registros de asistencia
        total_attendance = (
            # Concatenación de todos los DataFrames creados
            pd.concat(attendance)
            # Procesamiento de datos
            .pipe(self._processing.process_data)
            # Se ordenan los datos por fecha y hora de registro
            .sort_values(COLUMN.REGISTRY_TIME)
        )

        return total_attendance

    def _get_device_attendance_per_date_range(
        self,
        ctx: _ExecutionContext,
        device: _DeviceInfo,
    ) -> pd.DataFrame:
        """
        #### Obtención de registros de asistencia desde un dispositivo
        Este método obtiene todos los registros de asistencia de un dispositivo que se
        encuentren entre el rango de fecha especificado.
        """

        # Obtención de los datos desde la API
        records = self._get_device_access_event_records_per_date_range(ctx, device.sn)

        # Si no existen registros en el día...
        if not records:
            # Se genera un DataFrame vacío
            data = self._build_empty_data()

            return data

        # Procesamiento de los datos
        data = (
            # Conversión de la información a DataFrame
            pd.DataFrame(records)
            # Se asigna la columna de dispositivo
            .assign(**{COLUMN.DEVICE: device.label})
        )

        return data

    def _get_device_access_event_records_per_date_range(
        self,
        ctx: _ExecutionContext,
        sn: str,
    ) -> list[AccessEventInfo]:
        """
        #### Obtención de registros de acceso de dispositivo
        Este método obtiene los registros de acceso de un dispositivo
        desde la API en base a un rango de fecha especificado.
        """

        # Inicialización de lista de eventos de acceso
        access_event_records: list[AccessEventInfo] = []

        # Obtención de la primera respuesta desde la API y el total de registros encontrados
        ( first_response, pages ) = self._get_first_response_and_total_matches(ctx, sn)

        # Si no existen registros encontrados...
        if first_response['responseStatusStrg'] == 'NO MATCH':
            # Se retorna la lista vacía
            return access_event_records

        # Se añade la primera página de resultados a la lista de eventos de acceso
        access_event_records += first_response['InfoList']
        # Iteración por la cantidad de páginas para consultar desde la segunda página (Si es que hay más de una)
        for i in range(1, pages):
            # Cálculo de página
            page = i * CONFIG.MAX_RESULTS_QTY
            # Obtención de los datos desde la API
            response = self._get_access_event_data_page(ctx, sn, page)
            # Se añaden los resultados a la lista de eventos de acceso
            access_event_records += response['InfoList']

        return access_event_records

    def _get_first_response_and_total_matches(
        self,
        ctx: _ExecutionContext,
        sn: str,
    ) -> tuple[AccessEvent, int]:

        # Obtención de la primera respuesta desde la API para obtener el número total de registros existentes
        first_response = self._get_access_event_data_page(ctx, sn)
        # Obtención del número total de registros existentes
        total_matches = first_response['totalMatches']
        # Cálculo de páginas totales para consultar
        pages = total_matches // CONFIG.MAX_RESULTS_QTY + int(total_matches % CONFIG.MAX_RESULTS_QTY > 0)

        return (first_response, pages)

    def _build_empty_data(
        self,
    ) -> pd.DataFrame:

        # Inicialización del DataFrame vacío
        records = (
            pd.DataFrame(
                # Selección de columnas
                columns= SELECTED_COLUMNS
            )
            # Tipado de columnas
            .astype(ASSIGNED_DTYPES)
        )

        return records

    def _get_access_event_data_page(
        self,
        ctx: _ExecutionContext,
        sn: str,
        page: int = 0,
    ) -> AccessEvent:
        """
        #### Obtención de los eventos de acceso desde la API
        Este endpoint obtiene los datos de una página de eventos de acceso
        desde la API, de un dispositivo específico.
        """

        # Obtención del JSON y encabezados de eventos de acceso
        access_event_json = self._params.build_access_event_search_json(ctx, sn, page)
        access_event_headers = self._params.build_access_event_headers()
        # Obtención de los datos de eventos de acceso
        data = self._api.request(access_event_json, access_event_headers)

        return data
