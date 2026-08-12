from enum import IntEnum, auto


class States(IntEnum):
    REG_USERNAME = auto()
    REG_EMAIL = auto()
    REG_PASSWORD = auto()

    LOGIN_USERNAME = auto()
    LOGIN_PASSWORD = auto()

    TX_TYPE = auto()
    TX_AMOUNT = auto()
    TX_CATEGORY = auto()
    TX_DESCRIPTION = auto()

    DEP_NAME = auto()
    DEP_CATEGORY = auto()
    DEP_LIMIT = auto()
    DEP_START = auto()
    DEP_END = auto()

    REPORT_MENU = auto()
    REPORT_FROM = auto()
    REPORT_TO = auto()
