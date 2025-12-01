from enum import Enum

class LabelColor(Enum):
    RED = "Red"
    GREEN = "Green"
    ORANGE = "Orange"
    BLACK = "Black"

    def __str__(self):
        return self.value