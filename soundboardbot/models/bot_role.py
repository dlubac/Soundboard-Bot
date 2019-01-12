from enum import Enum


class BotRole(Enum):
    OWNER = 'BotOwner'
    ADMIN = 'BotAdmin'
    USER = 'BotUser'
    BANNED = 'BotBanned'
