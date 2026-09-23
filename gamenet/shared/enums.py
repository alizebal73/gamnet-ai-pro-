from enum import StrEnum


class CustomerStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class PCStatus(StrEnum):
    OFFLINE = "OFFLINE"
    ONLINE = "ONLINE"
    READY = "READY"
    BUSY = "BUSY"
    PAUSED = "PAUSED"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"
    LOCKED = "LOCKED"
    RETIRED = "RETIRED"
