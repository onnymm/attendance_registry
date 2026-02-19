from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)
import re
from typing import (
    Generic,
    Optional,
    TypeGuard,
)
from ._constants import (
    ERRORS,
    REGEX,
)
from ._interface import _Base_Assistance
from ._resources import _DeviceInfo
from ._settings import CONFIG
from ._typing import (
    _D,
    DateOrDateRange,
    DatetimeOrString,
)

class _ExecutionContext(Generic[_D]):
    start_date: str
    end_date: str
    devices: list[_DeviceInfo]

    def __init__(
        self,
        main: _Base_Assistance[_D],
        date_or_range: DateOrDateRange,
        device: Optional[_D] = None,
    ) -> None:

        # Asignación de instancia principal
        self._main = main
        # Se asigna el valor proporcionado de fecha o rango de fecha
        self._date_or_range = date_or_range
        # Se asigna el dispositivo
        self._specified_device = device

        # Inicialización de módulos
        self._device = self._Device(self)
        self._date = self._Date(self)

    class _Device:

        def __init__(
            self,
            main_ctx: '_ExecutionContext',
        ) -> None:

            # Asignación de instancia principal
            self._main_ctx = main_ctx
            # Resolución de valores de dispositivo
            self._resolve_devices()

        def _resolve_devices(
            self,
        ) -> None:

            # Si no se especificó un dispositivo...
            if self._main_ctx._specified_device is None:
                # Se obtiene la lista de todos los dispositivos
                self._main_ctx.devices = [ _DeviceInfo(label, sn) for ( label, sn ) in self._main_ctx._main._devices_data.items() ]
            # Si es especificó un dispositivo
            else:
                # Uso del nombre del dispositivo especificado
                device_label = self._main_ctx._specified_device
                # Obtención del número de serie de éste
                device_sn = self._main_ctx._main._devices_data[device_label]
                # Inicialización de un objeto de información de dispositivo
                device_info = _DeviceInfo(device_label, device_sn)
                # Se usa éste dentro de una lista
                self._main_ctx.devices = [device_info]

    class _Date:

        def __init__(
            self,
            main_ctx: '_ExecutionContext',
        ) -> None:

            # Asignación de instancia principal
            self._main_ctx = main_ctx
            # Se define el huso horario
            self._define_timezone()
            # Se definen los valores de fecha a usar
            self._define_date_range(self._main_ctx._date_or_range)

        def _define_timezone(
            self,
        ) -> None:

            # Se asigna el huso horario
            self._tz = (
                timezone( timedelta(hours= CONFIG.TIME_OFFSET) )
            )

        def _define_date_range(
            self,
            date_or_range: DateOrDateRange,
        ) -> tuple[str, str]:

            # Si el valor de fecha es una tupla...
            if isinstance(date_or_range, tuple):
                # Se resuelve éste
                self._resolve_date_range(date_or_range)

            # Si el valor fue provisto como escalar...
            elif isinstance(date_or_range, str) or isinstance(date_or_range, date):
                # Se resuelve éste
                self._resolve_scalar_date(date_or_range)

            # Si el tipo de dato de valor no es válido...
            else:
                # Se arroja error
                raise TypeError(ERRORS.ONLY_DATETIMELIKE)

        def _resolve_date_range(
            self,
            value: tuple[DatetimeOrString, DatetimeOrString],
        ) -> None:

            # Si la tupla no contiene exactamente dos elementos...
            if len(value) != 2:
                raise SyntaxError(ERRORS.TUPLE_INVALID_SIZE)

            # Obtención de los valores provistos
            ( start_date, end_date ) = value

            # Si ambos valores son fecha y hora...
            if self._is_datetime(start_date) and self._is_datetime(end_date):
                # Se usan éstos procesados con huso horario
                self._main_ctx.start_date = self._resolve_date(start_date)
                self._main_ctx.end_date = self._resolve_date(end_date)

                # Se valida que la fecha inicial sea menor a la final
                if not datetime.fromisoformat(self._main_ctx.start_date) < datetime.fromisoformat(self._main_ctx.end_date):
                    raise ValueError(ERRORS.TUPLE_INVALID_SIZE)

            # Si ambos valores son fecha...
            elif self._is_date(start_date) and self._is_date(end_date):
                self._main_ctx.start_date = self._use_date_as_start(start_date)
                self._main_ctx.end_date = self._use_date_as_end(end_date)

            # Si no hay consistencia en tipos...
            else:
                raise SyntaxError(ERRORS.TUPLE_MUST_BE_SAME_TYPE)

        def _resolve_date(
            self,
            string_or_datetime_value: datetime | str,
        ) -> str:

            # Conversión del tipo de dato a objeto [datetime]
            datetime_value = self._datetime_from_object_or_string(string_or_datetime_value)

            resolved_value = (
                # Uso del valor de fecha y hora
                datetime_value
                # Se añade el huso horario
                .astimezone(self._tz)
                # Se formatea a texto
                .isoformat(timespec= 'seconds')
            )

            return resolved_value

        def _resolve_scalar_date(
            self,
            string_or_date_value: date | str,
        ) -> None:

            # Se valida que el valor sea válido
            if self._is_date(string_or_date_value):
                # Se usa fecha como rango del día
                self.use_unique_date_as_whole_day(string_or_date_value)

            # Si el valor es fecha y hora...
            else:
                # No se puede usar éste como rango
                raise SyntaxError(ERRORS.SCALAR_VALUE_MUST_BE_DATE_LIKE)

        def use_unique_date_as_whole_day(
            self,
            string_date_value: str,
        ) -> None:

            # Se usa el rango del día como inicio y final
            self._main_ctx.start_date = self._use_date_as_start(string_date_value)
            self._main_ctx.end_date = self._use_date_as_end(string_date_value)

        def _use_date_as_start(
            self,
            string_or_date_value: date | str,
        ) -> str:

            # Conversión del tipo de dato a objeto [date]
            date_value = self._date_from_object_or_string(string_or_date_value)

            # Construcción de valor de fecha y hora
            resolved_value = (
                datetime(
                    *(
                        # Se usa el valor de fecha
                        date_value
                        # Se obtiene una tupla de valores
                        .timetuple()
                        # Se usan solo los primeros tres valores de año, mes y día
                        [:3]
                    ),
                    # Se usa el huso horario
                    tzinfo= self._tz,
                )
                # Se formatea a texto
                .isoformat(timespec= 'seconds')
            )

            return resolved_value

        def _use_date_as_end(
            self,
            string_or_date_value: date | str,
        ) -> str:

            # Conversión del tipo de dato a objeto [date]
            date_value = self._date_from_object_or_string(string_or_date_value)

            # Conversión de valor de fecha y hora
            resolved_value = (
                (
                    datetime(
                        *(
                            # Se usa el valor de fecha
                            date_value
                            # Se obtiene una tupla de valores
                            .timetuple()
                            # Se usan solo los primeros tres valores de año, mes y día
                            [:3]
                        ),
                        # Se usa el huso horario
                        tzinfo= self._tz,
                    )
                    # Se suma el tiempo hasta el último segundo del día
                    + timedelta(hours= 23, minutes= 59, seconds= 59)
                )
                # Se formatea a texto
                .isoformat(timespec= 'seconds')
            )

            return resolved_value

        def _datetime_from_object_or_string(
            self,
            obj: datetime | str
        ) -> datetime:

            # Si la instancia es un texto...
            if isinstance(obj, str):
                # Se convierte ésta a un objeto de tiempo
                value = datetime.fromisoformat(obj)
            # Si la instancia es de tipo [date]...
            else:
                # Se usa ésta como valor de retorno
                value = obj

            return value

        def _date_from_object_or_string(
            self,
            obj: date | str
        ) -> date:

            # Si la instancia es un texto...
            if isinstance(obj, str):
                # Se convierte ésta a un objeto de tiempo
                value = date.fromisoformat(obj)
            # Si la instancia es de tipo [date]...
            else:
                # Se usa ésta como valor de retorno
                value = obj

            return value

        def _is_date(
            self,
            value: str,
        ) -> TypeGuard[str | date]:

            # Validación de estructura
            if isinstance(value, str):
                # Validación de si la estructura del texto es de tipo fecha
                is_date_structure = re.match(REGEX.DATE_STRUCTURE, value) is not None

                return is_date_structure

            # Validación del tipo de objeto
            is_date_object = isinstance(value, date)

            return is_date_object

        def _is_datetime(
            self,
            value: str,
        ) -> TypeGuard[str | datetime]:

            # Validación de estructura
            if isinstance(value, str):
                # Validación de si la estructura del texto es de tipo fecha y hora
                is_datetime_structure = re.match(REGEX.DATETIME_STRUCTURE, value) is not None

                return is_datetime_structure

            # Validación del tipo de objeto
            is_datetime_object = isinstance(value, datetime)

            return is_datetime_object
