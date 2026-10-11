from enum import Enum, auto


class AppointmentStatus(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    COMPLETED = auto()
    CANCELLED = auto()