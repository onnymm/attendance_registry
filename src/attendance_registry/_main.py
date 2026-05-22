from datetime import datetime
import json
from uuid import uuid4
import requests
from ._constants import API_NOT_AVAIABLE_SHAPE
from ._constants import EXPIRED_CREDENTIALS_SHAPE
from ._constants import ERROR_LABEL
from ._constants import URL
from ._errors import APINotAvailableError
from ._errors import ExpiredCredentialsError
from ._resources import Credentials
from ._resources import Device
from ._resources import ExecutionContext
from ._typing import _AccessEvent
from ._typing import _AccessEventInfo
from ._typing import _AcsEventSearchJSON
from ._typing import _RequestData
from ._typing import AccessEventsData
from ._typing import AssistanceEvent

class Attendance():

    def get_events(
        self,
        device_model: str,
        device_sn: str,
        device_os_version: str,
        cookie: str,
        token: str,
        site_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[AssistanceEvent]:

        # Inicialización de objeto de dispositivo
        device = Device(
            device_model,
            device_sn,
            device_os_version,
        )
        # Inicialización de objeto de credenciales
        credentials = Credentials(
            cookie,
            token,
            site_id,
        )
        # Inicialización de contexto de ejecución
        ctx = ExecutionContext(
            device,
            credentials,
            start_date,
            end_date,
        )

        # Inicialización de lista de eventos de acceso
        access_event_records: list[_AccessEvent] = []

        # Obtención de primera respuesta desde la API de HikVision
        first_response = self._get_access_event(ctx)

        # Si no existen registros nuevos...
        if first_response['responseStatusStrg'] == 'NO MATCH':
            # Se retorna una lista vacía
            return []

        # Se añade la primera página de resultados a la lista de eventos de acceso
        access_event_records += first_response['InfoList']

        # Obtención del número total de registros existentes
        total_matches = first_response['totalMatches']
        # Cálculo de páginas totales para consultar
        pages = total_matches // 24 + int(total_matches % 24 > 0)
        # Iteración por la cantidad de páginas para consultar desde la segunda página (Si es que hay más de una)
        for i in range(1, pages):
            # Cálculo de página
            page = i * 24
            # Obtención de los datos desde la API
            response = self._get_access_event(ctx, page)
            # Se añaden los resultados a la lista de eventos de acceso
            access_event_records += response['InfoList']

        # Procesamiento de los registros
        assistance_events = self._process(access_event_records)

        return assistance_events

    def _process(
        self,
        access_event_records: list[_AccessEventInfo],
    ) -> list[AssistanceEvent]:

        # Inicialización de lista de salida
        assistance_events: list[AssistanceEvent] = []

        # Iteración por cada registro de evento de acceso
        for acc_evt_rcd in access_event_records:
            # Si el valor en netUser es [admin]...
            if acc_evt_rcd['netUser'] == 'admin':
                # Se continúa al siguiente registro
                continue
            # Si no existe nombre de usuario...
            if acc_evt_rcd['name'] == '':
                # Se continúa al siguiente registro
                continue

            # Inicialización de diccionario de evento de asistencia
            event: AssistanceEvent = {}
            # Adición de valores
            event['user_id'] = acc_evt_rcd['employeeNoString']
            event['registry_time'] = acc_evt_rcd['time']
            event['status'] = acc_evt_rcd['attendanceStatus']

            # Se añade el diccionario a la lista de registros procesados
            assistance_events.append(event)

        return assistance_events

    def _get_access_event(
        self,
        ctx: ExecutionContext,
        page: int = 0,
    ) -> _AccessEvent:

        # Construcción del JSON y encabezados de eventos de acceso
        access_event_json = self._build_access_event_search_json(ctx, page)
        access_event_headers = self._build_access_event_headers(ctx)

        # Solicitud de datos a la API y obtención de la respuesta de ésta
        response = self._request(access_event_json, access_event_headers)

        return response

    def _request(
        self,
        access_event_search: _AcsEventSearchJSON,
        headers: dict[str, str],
    ) -> _AccessEvent:

        # Solicitud de datos al endpoint
        response = requests.post(
            URL,
            json= access_event_search,
            headers= headers,
        )

        # Decodificación del contenido en formato JSON
        content = json.loads(response.content)

        if content == API_NOT_AVAIABLE_SHAPE:
            # Se arroja error de API no disponible
            raise APINotAvailableError(ERROR_LABEL.API_NOT_AVAILABLE)

        if content == EXPIRED_CREDENTIALS_SHAPE:
            # Se arroja error de credenciales expiradas
            raise ExpiredCredentialsError(ERROR_LABEL.EXPIRED_CREDENTIALS)

        # Obtención del cuerpo de los datos mediante otra decodificación en JSON
        response_body: AccessEventsData = json.loads(content['data']['responseBody'])
        # Obtención de los eventos de acceso
        access_events = response_body['AcsEvent']

        return access_events

    def _build_access_event_search_json(
        self,
        ctx: ExecutionContext,
        page: int,
    ):

        # Construcción de los parámetros de búsqueda de eventos
        access_event_search = self._build_event_search_params(ctx, page)

        # Construcción de los datos de la solicitud
        data: _RequestData = {
            'method': 'POST',
            'url': '/ISAPI/AccessControl/AcsEvent?format=json',
            'deviceSerial': ctx.device.sn,
            'accessToken': ctx.credentials.token,
            'domain': 'https://iusopen.ezvizlife.com',
            'body': access_event_search,
            'contentType': 'application/json',
            'bizType': 0,
            'mainType': 5,
            'subType': 9,
            'deviceVersion': ctx.device.os_version,
            'model': ctx.device.model,
            'urlType': 'TEAM',
            'siteId': ctx.credentials.site_id,
        }

        return data

    def _build_access_event_headers(
        self,
        ctx: ExecutionContext,
    ) -> dict[str, str]:

        # Construcción de los encabezados
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-419,es;q=0.9',
            'Content-Type': 'application/json',
            'Cookie': f'JSESSIONID={ctx.credentials.cookie}',
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

    def _build_event_search_params(
        self,
        ctx: ExecutionContext,
        page: int,
    ) -> str:

        # Construcción de los parámetros en diccionario
        access_event_search: _AcsEventSearchJSON = {
            'AcsEventCond': {
                'searchID': uuid4().__str__(),
                'searchResultPosition': page,
                'maxResults': 24,
                'major': 0,
                'minor': 0,
                'startTime': ctx.start_date.isoformat(timespec= 'seconds'),
                'endTime': ctx.end_date.isoformat(timespec= 'seconds'),
            }
        }

        # Conversión de los parámetros a JSON
        json_params = json.dumps(access_event_search)

        return json_params
