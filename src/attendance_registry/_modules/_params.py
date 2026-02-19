import json
from uuid import uuid4
from .._execution_context import _ExecutionContext
from .._settings import CONFIG
from .._typing import (
    AcsEventSearchJSON,
    RequestData,
)
from .._interface import _Base_Assistance

class _Params:

    def __init__(
        self,
        main: _Base_Assistance,
    ) -> None:

        # Asignación de instancia principal
        self._main = main

    def build_access_event_headers(
        self,
    ) -> dict[str, str]:
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

    def build_access_event_search_json(
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
        >>>     'AcsEventCond': {
        >>>         'searchID': '24afd955-d334-4480-b74e-3f84e6933c05',
        >>>         'searchResultPosition': 0,
        >>>         'maxResults': 24,
        >>>         'major': 0,
        >>>         'minor': 0,
        >>>         'startTime': f'2025-08-01T00:00:00+00:00',
        >>>         'endTime': f'2025-08-01T23:59:59+00:00',
        >>>     },
        >>> }
        """

        # Construcción de los parámetros de búsqueda de eventos
        event_search_params = self._build_event_search_params(ctx, page)

        # Construcción de los datos de la solicitud
        data: RequestData = {
            'method': 'POST',
            'url': '/ISAPI/AccessControl/AcsEvent?format=json',
            'deviceSerial': sn,
            'accessToken': CONFIG.TOKEN,
            'domain': 'https://iusopen.ezvizlife.com',
            'body': event_search_params,
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

    def _build_event_search_params(
        self,
        ctx: _ExecutionContext,
        page: int,
    ) -> str:

        # Construcción de los parámetros en diccionario
        dict_params: AcsEventSearchJSON = {
            'AcsEventCond': {
                'searchID': f'{uuid4()}',
                'searchResultPosition': page,
                'maxResults': CONFIG.MAX_RESULTS_QTY,
                'major': 0,
                'minor': 0,
                'startTime': ctx.start_date,
                'endTime': ctx.end_date,
            },
        }

        # Conversión de los parámetros a JSON
        json_params = json.dumps(dict_params)

        return json_params
