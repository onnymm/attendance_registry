from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict
from ._typing import EventStatus

@dataclass(slots= True)
class Device:
    model: str
    sn: str
    os_version: str

@dataclass(slots= True)
class Credentials:
    cookie: str
    token: str
    site_id: str

@dataclass(slots= True)
class ExecutionContext():
    device: Device
    credentials: Credentials
    start_date: datetime
    end_date: datetime
