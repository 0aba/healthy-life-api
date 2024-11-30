from enum import StrEnum, unique


@unique
class Role(StrEnum):
    MODERATOR = 'moderator'
    PHARMACIST = 'pharmacist'

