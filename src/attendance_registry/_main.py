import json
import pandas as pd
import requests
from datetime import date
from ._types import (
    _T,
    ACC_EVT_API_FIELD,
    ACC_EVT_DATA_FIELD,
    AccessEvent,
    AccessEventInfo,
    AccessEventsData,
    AcsEventSearchJSON,
    RequestData,
    _DateOrDateRange,
)
from json import JSONDecodeError
from typing import Optional
from uuid import uuid4
from ._execution_context import _ExecutionContext
from ._interface import _Base_Assistance
from ._resources import _DeviceInfo
from ._settings import CONFIG

class Assistance(_Base_Assistance[_T]):

    _DATA_TITLES = {
        ACC_EVT_API_FIELD.USER_ID: ACC_EVT_DATA_FIELD.USER_ID,
        ACC_EVT_API_FIELD.NAME: ACC_EVT_DATA_FIELD.NAME,
        ACC_EVT_API_FIELD.TIME: ACC_EVT_DATA_FIELD.TIME,
        ACC_EVT_API_FIELD.REGISTRY_TYPE: ACC_EVT_DATA_FIELD.REGISTRY_TYPE,
        ACC_EVT_API_FIELD.DEVICE: ACC_EVT_DATA_FIELD.DEVICE,
    }
    """
    Títulos de datos finales
    """

    _DATA_TYPES = {
        ACC_EVT_DATA_FIELD.USER_ID: 'O',
        ACC_EVT_DATA_FIELD.NAME: 'O',
        ACC_EVT_DATA_FIELD.TIME: '<M8[ns]',
        ACC_EVT_DATA_FIELD.REGISTRY_TYPE: 'O',
        ACC_EVT_DATA_FIELD.DEVICE: 'O',
    }
    """
    Tipos de datos.
    """

    _DATA_ORDER = [
        ACC_EVT_DATA_FIELD.USER_ID,
        ACC_EVT_DATA_FIELD.NAME,
        ACC_EVT_DATA_FIELD.TIME,
        ACC_EVT_DATA_FIELD.REGISTRY_TYPE,
        ACC_EVT_DATA_FIELD.DEVICE,
    ]
    """
    Orden de columnas de DataFrames.
    """

    _CHARACTER_FORMATTING = {
        '帽': 'ñ',
        '铆': 'í',
        '煤': 'ú',
    }
    """
    Mapeo de formato de caracteres.
    """

    def __init__(
        self,
        devices: dict[_T, str],
    ) -> None:

        # Se guardan los datos de los dispositivos
        self._devices_data = devices

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

        # Obtención de la fecha del día de hoy en formato de texto
        date_day = date.today().__str__()
        # Obtención de los registros de asistencia del día
        data = self.get_daily_attendance(date_day, device)

        return data

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
            # Se ordenan los datos por fecha y hora
            .sort_values( [
                # ACC_EVT_API_FIELD.DATE,
                ACC_EVT_API_FIELD.TIME,
            ] )
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
            # Obtención de columnas de fecha y hora
            .assign(
                **{
                    # Formateo de fecha
                    ACC_EVT_API_FIELD.TIME: lambda df: (
                        pd.to_datetime(
                            df[ACC_EVT_API_FIELD.TIME]
                            .apply(
                                lambda value: (
                                    value
                                    .replace('T', ' ')
                                    [:19]
                                )
                            )
                        )
                    ),
                }
            )
            # Se descartan todos los registros que no sean registro de asistencia
            .pipe(lambda df: df[ (df[ACC_EVT_API_FIELD.NET_USER] != 'admin') & (df[ACC_EVT_API_FIELD.NAME] != '') ])
            # Se asigna la columna de dispositivo
            .assign(**{ACC_EVT_API_FIELD.DEVICE: device.label})
            # Formateo de caracteres
            .assign(
                **{
                    ACC_EVT_API_FIELD.NAME: lambda df: (
                        df[ACC_EVT_API_FIELD.NAME]
                        .apply(self._character_format)
                    )
                }
            )
            # Se reasignan los nombres de columna
            .rename(columns= self._DATA_TITLES)
            # Orden de columnas
            [self._DATA_ORDER]
        )

        return data

    def _build_empty_data(
        self,
    ) -> pd.DataFrame:

        # Inicialización del DataFrame vacío
        records = (
            pd.DataFrame(
                # Selección de columnas
                columns= self._DATA_ORDER
            )
            # Tipado de columnas
            .astype(self._DATA_TYPES)
        )

        return records

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

        # Obtención de la primera respuesta desde la API para obtener el número total de registros existentes
        first_response = self._get_access_event_data_page(ctx, sn)
        # Obtención del número total de registros existentes
        total_matches = first_response['totalMatches']
        # Cálculo de páginas totales para consultar
        pages = total_matches // CONFIG.MAX_RESULTS_QTY + int(total_matches % CONFIG.MAX_RESULTS_QTY > 0)

        # Inicialización de lista de eventos de acceso
        access_event_records: list[AccessEventInfo] = []

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
        access_event_json = self._build_access_event_search_json(ctx, sn, page)
        access_event_headers = self._build_access_event_headers()

        # Solicitud de datos al endpoint
        response = requests.post(
            self._URL,
            json= access_event_json,
            headers= access_event_headers,
        )

        try:
            # Obtención del diccionario de datos
            content: AccessEventsData = (
                # Se carga el cuerpo de respuesta de...
                json.loads(
                    # Se carga la respuesta desde un JSON
                    json.loads(response.content)
                    # Acceso al cuerpo de respuesta
                    ['data']['responseBody']
                )
            )
        except JSONDecodeError:
            raise AssertionError('Actualiza los datos de autenticación')
        # Obtención de los datos de eventos de acceso
        data = content['AcsEvent']

        return data

    def _build_access_event_headers(
        self,
    ) -> dict:
        """
        #### Construcción de los encabezados de eventos de acceso
        Este método construye los encabezados usados para solicitud de datos de eventos de acceso, en base al dispositivo especificado.
        """

        # Construcción de los encabezados
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-419,es;q=0.9',
            'Content-Type': 'application/json',
            'Cookie': f'JSESSIONID={CONFIG.COOKIE}',
            'Origin': 'https://www.hik-connect.com',
            'Priority': 'u=1, i',
            'Referer': 'https://www.hik-connect.com/',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cors-site',
            'Sec-Fetch-Storage-Access': 'active',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        }

        return headers

    def _build_access_event_search_json(
        self,
        ctx: _ExecutionContext,
        sn: str,
        page: int = 0,
    ) -> AcsEventSearchJSON:
        """
        #### Construcción de JSON de eventos de acceso
        Este método construye el JSON que contiene los criterios de búsqueda
        para filtrar los eventos de acceso. Este JSON se usa para realizar las
        solicitudes de datos a la API de HikVision.

        Ejemplo de retorno:
        >>> {
        >>>     "AcsEventCond": {
        >>>         "searchID": "24afd955-d334-4480-b74e-3f84e6933c05",
        >>>         "searchResultPosition": 0,
        >>>         "maxResults": 24,
        >>>         "major": 0,
        >>>         "minor": 0,
        >>>         "startTime": f"2025-08-01T00:00:00+00:00",
        >>>         "endTime": f"2025-08-01T23:59:59+00:00",
        >>>     },
        >>> }
        """

        # Obtención del número de serie del dispositivo
        # sn = self._get_device_sn(device)

        # Construcción de los parámetros
        params: AcsEventSearchJSON = {
            "AcsEventCond": {
                "searchID": f"{uuid4()}",
                "searchResultPosition": page,
                "maxResults": CONFIG.MAX_RESULTS_QTY,
                "major": 0,
                "minor": 0,
                "startTime": ctx.start_date,
                "endTime": ctx.end_date,
            },
        }

        # Construcción de los datos de la solicitud
        data: RequestData = {
            'method': 'POST',
            'url': '/ISAPI/AccessControl/AcsEvent?format=json',
            'deviceSerial': sn,
            'accessToken': CONFIG.TOKEN,
            'domain': 'https://iusopen.ezvizlife.com',
            'body': json.dumps(params),
            'contentType': 'application/json',
            'bizType': 0,
            'mainType': 5,
            'subType': 9,
            'deviceVersion': 'V1.2.7 build 240102',
            'model': CONFIG.DEVICE_MODEL,
            'urlType': 'TEAM',
            'siteId': CONFIG.SITE_ID,
        }

        return data

    # def _get_device_sn(
    #     self,
    #     device: _T,
    # ) -> str:

    #     # Obtención del número de serie del dispositivo
    #     sn = self._devices_data[device]

    #     return sn

    def _character_format(
        self,
        value: str,
    ) -> str:

        # Iteración por cada caracter a reemplazar
        for ( i, o ) in self._CHARACTER_FORMATTING.items():
            # Reemplazo de caracteres
            value = value.replace(i, o)

        return value
