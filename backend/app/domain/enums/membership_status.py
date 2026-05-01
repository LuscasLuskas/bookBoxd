from enum import StrEnum


class MembershipStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    LEFT = "LEFT"
    KICKED = "KICKED"
