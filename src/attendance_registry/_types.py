from typing import (
    Literal,
    TypedDict,
)
from pydantic import BaseModel

class AccessEventInfo(TypedDict):
    major: int
    minor: int
    time: str
    netUser: str
    remoteHostAddr: str
    cardNo: str
    cardType: int
    name: str
    reportChannel: int
    cardReaderKind: int
    cardReaderNo: int
    doorNo: int
    verifyNo: int
    alarmInNo: int
    alarmOutNo: int
    caseSensorNo: int
    RS485No: int
    multiCardGroupNo: int
    deviceNo: int
    employeeNoString: str
    InternetAccess: int
    type: int
    MACAddr: str
    swipeCardType: int
    serialNo: int
    userType: str
    currentVerifyMode: str
    attendanceStatus: str
    statusValue: int

class AccessEvent(TypedDict):
    searchID: str
    responseStatusStrg: Literal['More', 'OK', 'NO MATCH']
    numOfMatches: int
    totalMatches: int
    InfoList: list[AccessEventInfo]

class AccessEventsData(TypedDict):
    AcsEvent: AccessEvent

class DeviceAttsDict(TypedDict):
    id: str
    """
    ID del dispositivo
    """
    sn: str
    """
    Número de serie del dispositivo
    """

class DeviceAtts(BaseModel):
    id: str
    """
    ID del dispositivo
    """
    sn: str
    """
    Número de serie del dispositivo
    """

class ACC_EVT_API_FIELD:
    NET_USER = 'netUser'
    DATE = 'date'
    TIME = 'time'
    NAME = 'name'
    USER_ID = 'employeeNoString'
    REGISTRY_TYPE = 'attendanceStatus'
    DEVICE = 'device'

class ACC_EVT_DATA_FIELD:
    DATE = 'date'
    TIME = 'time'
    NAME = 'name'
    USER_ID = 'user_id'
    REGISTRY_TYPE = 'status'
    DEVICE = 'device'

class _AcsEventCondition(TypedDict):
    """
    #### Condiciones de evento de acceso
    Este tipo de dato especifica los criterios de búsqueda de eventos de acceso.
    """
    searchID: str
    searchResultPosition: int
    maxResults: int
    major: int
    minor: int
    startTime: str
    endTime: str

class AcsEventSearchJSON(TypedDict):
    """
    #### JSON de condiciones de evento de acceso
    Este JSON contiene las condiciones de evento de acceso y se usa para las
    solicitudes de datos hacia la API de HikVision
    """
    AcsEventCond: _AcsEventCondition

DeviceName = Literal['csl', 'sjc']
