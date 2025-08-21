import json
import pandas as pd
import requests
from datetime import date
from ._types import (
    ACC_EVT_API_FIELD,
    ACC_EVT_DATA_FIELD,
    AccessEvent,
    AccessEventInfo,
    AccessEventsData,
    AcsEventSearchJSON,
    DeviceAttsDict,
    DeviceAtts,
)
from typing import Generic, TypeVar
from json import JSONDecodeError

_T = TypeVar('_T')

class Assistance(Generic[_T]):

    _URL = 'http://127.0.0.1:18090/api/hikvision/ISAPI/AccessControl/AcsEvent?format=json'
    """
    URL del endpoint para obtención de registros de asistencia
    """
    _devices_data: dict[_T, DeviceAttsDict]
    """
    Datos de los dispositivos
    """
    _MAX_RESULTS_QTY = 24
    """
    Constante de cantidad máxima de resultados
    """
    _devices: dict[_T, DeviceAtts]
    """
    Diccionario de datos de los dispositivos disponibles
    """
    _data_titles = {
        ACC_EVT_API_FIELD.DATE: ACC_EVT_DATA_FIELD.DATE,
        ACC_EVT_API_FIELD.TIME: ACC_EVT_DATA_FIELD.TIME,
        ACC_EVT_API_FIELD.REGISTRY_TYPE: ACC_EVT_DATA_FIELD.REGISTRY_TYPE,
        ACC_EVT_API_FIELD.USER_ID: ACC_EVT_DATA_FIELD.USER_ID,
        ACC_EVT_API_FIELD.DEVICE: ACC_EVT_DATA_FIELD.DEVICE,
    }
    """
    Títulos de datos finales
    """

    def __init__(
        self,
        devices: dict[_T, DeviceAttsDict]
    ) -> None:

        # Se guardan los datos de los dispositos
        self._devices_data = devices

        # Se crean los BaseModel de los datos
        self._devices = {
            device_name: DeviceAtts(**device_atts)
            for ( device_name, device_atts )
            in self._devices_data.items()
        }

    def get_today_attendance(
        self,
        device: _T | None = None
    ) -> pd.DataFrame:
        """
        #### Obtención de los registros de asistencia del hoy
        Este método obtiene los registros de asistencia del día de hoy, ya sea de un dispositivo
        especificado o de todos los dispositivos.
        """

        # Obtención de la fecha del día de hoy en formato de texto
        date_day = date.today().__str__()
        # Obtención de los registros de asistencia del día
        data = self.get_daily_attendance(date_day, device)

        return data

    def get_daily_attendance(
        self,
        date_day: str, # YYYY-MM-DD
        device: _T | None = None
    ) -> pd.DataFrame:
        """
        #### Obtención de registros diarios de asistencia
        Este endpoint obtiene todos los registros de asistencia de un día especificado.
        """

        # Si no se especificó un dispositivo...
        if device is None:
            # Se obtiene la lista de todos los dispositivos
            devices: list[_T] = [ dev_key for dev_key in self._devices_data.keys() ]
        # Si se especificó un dispositivo
        else:
            # Se convierte éste a una lista de un elemento
            devices: list[_T] = [device]

        # Inicialización de lista de DataFrames a concatenar para el resultado final
        attendance: list[pd.DataFrame] = []

        # Iteración por cada dispositivo
        for dev_i in devices:
            # Obtención de los registros de asistencia del dispositivo i
            attendance_i = self._get_device_attendance_per_date_range(date_day, date_day, dev_i)
            # Se añade el DataFrame obtenido a la lista de DataFrames por concatenar
            attendance.append(attendance_i)

        # Obtención de todos los registros de asistencia
        total_attendance = (
            # Concatenación de todos los DataFrames creados
            pd.concat(attendance)
            # Se ordenan los datos por fecha y hora
            .sort_values( [ACC_EVT_API_FIELD.DATE, ACC_EVT_API_FIELD.TIME] )
        )

        return total_attendance

    def _get_device_attendance_per_date_range(
        self,
        start_date: str, # YYYY-MM-DD
        end_date: str, # YYYY-MM-DD
        device: _T,
    ) -> pd.DataFrame:
        """
        #### Obtención de registros de asistencia desde un dispositivo
        Este método obtiene todos los registros de asistencia de un dispositivo que se
        encuentren entre el rango de fecha especificado.
        """

        # Obtención de los datos desde la API
        records = self._get_device_access_event_records_per_date_range(start_date, end_date, device)
        # Procesamiento de los datos
        data = (
            # Conversión de la información a DataFrame
            pd.DataFrame(records)
            # Obtención de columnas de fecha y hora
            .assign(
                **{
                    # Obtención de fecha
                    ACC_EVT_API_FIELD.DATE: lambda df: df[ACC_EVT_API_FIELD.TIME].apply(lambda value: value.split('T')[0]),
                    # Obtención de hora
                    ACC_EVT_API_FIELD.TIME: lambda df: df[ACC_EVT_API_FIELD.TIME].apply(lambda value: value.split('T')[1].split('-')[0]),
                }
            )
            # Se descartan todos los registros que no sean registro de asistencia
            .pipe(lambda df: df[ (df[ACC_EVT_API_FIELD.NET_USER] != 'admin') & (df[ACC_EVT_API_FIELD.NAME] != '') ])
            # Selección de columnas
            [[
                ACC_EVT_API_FIELD.USER_ID,
                ACC_EVT_API_FIELD.NAME,
                ACC_EVT_API_FIELD.DATE,
                ACC_EVT_API_FIELD.TIME,
                ACC_EVT_API_FIELD.REGISTRY_TYPE,
            ]]
            # Se asigna la columna de dispositivo
            .assign(**{ACC_EVT_API_FIELD.DEVICE: device})
            # Se reasignan los nombres de columna
            .rename(columns= self._data_titles)
        )

        return data

    def _get_device_access_event_records_per_date_range(
        self,
        start_date: str, # YYYY-MM-DD
        end_date: str, # YYYY-MM-DD
        device: _T,
    ) -> list[AccessEventInfo]:
        """
        #### Obtención de registros de acceso de dispositivo
        Este método obtiene los registros de acceso de un dispositivo
        desde la API en base a un rango de fecha especificado.
        """

        # Obtención de la primera respuesta desde la API para obtener el número total de registros existentes
        first_response = self._get_access_event_data_page(start_date, end_date, device)
        # Obtención del número total de registros existentes
        total_matches = first_response['totalMatches']
        # Cálculo de páginas totales para consultar
        pages = total_matches // self._MAX_RESULTS_QTY + int(total_matches % self._MAX_RESULTS_QTY > 0)

        # Inicialización de lista de eventos de acceso
        access_event_records: list[AccessEventInfo] = []
        # Se añade la primera página de resultados a la lista de eventos de acceso
        access_event_records += first_response['InfoList']

        # Iteración por la cantidad de páginas para consultar desde la segunda página (Si es que hay más de una)
        for i in range(1, pages):
            # Cálculo de página
            page = i * self._MAX_RESULTS_QTY
            # Obtención de los datos desde la API
            response = self._get_access_event_data_page(start_date, end_date, device, page)
            # Se añaden los resultados a la lista de eventos de acceso
            access_event_records += response['InfoList']

        return access_event_records

    def _get_access_event_data_page(
        self,
        start_date: str, # YYYY-MM-DD
        end_date: str, # YYYY-MM-DD
        device: _T,
        offset: int = 0,
    ) -> AccessEvent:
        """
        #### Obtención de los eventos de acceso desde la API
        Este endpoint obtiene los datos de una página de eventos de acceso
        desde la API, de un dispositivo específico.
        """

        # Obtención del JSON y encabezados de eventos de acceso
        access_event_json = self._build_access_event_search_json(offset, start_date, end_date)
        access_event_headers = self._build_access_event_headers(device)

        # Solicitud de datos al endpoint
        response = requests.post(
            self._URL,
            json= access_event_json,
            headers= access_event_headers,
        )

        try:
            # Obtención del diccionario de datos
            content: AccessEventsData = json.loads(response.content)
        except JSONDecodeError:
            raise AssertionError('Actualiza las IDs de la API')
        # Obtención de los datos de eventos de acceso
        data = content['AcsEvent']

        return data

    def _build_access_event_headers(
        self,
        device: _T,
    ) -> dict:
        """
        #### Construcción de los encabezados de eventos de acceso
        Este método construye los encabezados usados para solicitud de datos de eventos de acceso, en base al dispositivo especificado.
        """

        # Obtención de URL de referencia
        referer = self._get_referer_url(device)
        # Construcción de los encabezados
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-419,es;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '118',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'If-Modified-Since': '0',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Storage-Access': 'active',
            'Referer': referer,
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Host': '127.0.0.1:18090',
            'Origin': 'http://127.0.0.1:18090',
        }

        return headers

    def _get_referer_url(
        self,
        device: _T,
    ) -> str:
        """
        #### Dispositivo de referencia
        Este método crea un atributo en URL que contiene los datos de ID y número de serie del dispositivo del que se desean obtener los datos.

        Ejemplo de retorno:
        >>> f'http://127.0.0.1:18090/deviceCfgNew/{ID DEL DISPOSITIVO}/0/{NÚMERO DE SERIE}/accessControl/WebConfigCtrl/Packages/R0401/webs_4.0_isapi/index.asp'
        """

        # Obtención de los atributos del dispositivo especificado
        device_atts = self._devices[device]
        # Construcción de la URL de referencia
        data = f'http://127.0.0.1:18090/deviceCfgNew/{device_atts.id}/0/{device_atts.sn}/accessControl/WebConfigCtrl/Packages/R0401/webs_4.0_isapi/index.asp'

        return data

    def _build_access_event_search_json(
        self,
        offset: int,
        start_date: str, # YYYY-MM-DD
        end_date: str, # YYYY-MM-DD
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

        # Construcción de los datos
        data = {
            "AcsEventCond": {
                "searchID": "24afd955-d334-4480-b74e-3f84e6933c05",
                "searchResultPosition": offset,
                "maxResults": self._MAX_RESULTS_QTY,
                "major": 0,
                "minor": 0,
                "startTime": f"{start_date}T00:00:00+00:00",
                "endTime": f"{end_date}T23:59:59+00:00",
            },
        }

        return data
