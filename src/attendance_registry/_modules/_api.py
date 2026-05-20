import json
import requests
from json import JSONDecodeError
from .._constants import URL
from .._interface import _Base_Assistance
from .._typing import (
    AccessEvent,
    AccessEventsData,
    AcsEventSearchJSON,
)
class _API:

    def __init__(
        self,
        main: _Base_Assistance,
    ) -> None:

        # Asignación de instancia principal
        self._main = main

    def request(
        self,
        access_event_search: AcsEventSearchJSON,
        headers: dict[str, str],
    ) -> AccessEvent:

        # Solicitud de datos al endpoint
        response = requests.post(
            URL,
            json= access_event_search,
            headers= headers,
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
