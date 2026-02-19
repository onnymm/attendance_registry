from typing import TypedDict, Literal

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
    Este tipo de dato de JSON contiene las condiciones de evento de acceso y se usa
    para las solicitudes de datos hacia la API de HikVision.
    """
    AcsEventCond: _AcsEventCondition

class RequestData(TypedDict):
    method: Literal['POST']
    url: str
    deviceSerial: str
    accessToken: str
    domain: Literal['https//iusopen.ezvizlife.com']
    body: str
    contentType: Literal['application/json']
    bizType: 0
    mainType: 5
    subType: 9
    deviceVersion: Literal['V1.2.7 build 240102']
    model: Literal['DS-K1A340WX']
    urlType: Literal['TEAM']
    siteId: str

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
