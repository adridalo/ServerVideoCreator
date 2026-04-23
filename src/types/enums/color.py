from enum import Enum

class LabelColor(Enum):
    RED = "Red"
    GREEN = "Green"
    ORANGE = "Orange"
    BLACK = "Black"
    WHITE = "White"

    def __str__(self):
        return self.value