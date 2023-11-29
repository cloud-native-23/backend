import enum
from aenum import MultiValueEnum

class LevelRequirement(MultiValueEnum):
    EASY = "初級", 1
    EASY_MEDIUM = "中級_初級", 2 
    MEDIUM = "中級", 3
    EASY_MEDIUM_HARD = "初級_中級_高級", 4
    MEDIUM_HARD = "中級_高級", 5 
    HARD = "高級", 6

class RentStatus(enum.Enum):
    Approved = 1
    Cancelled = 0