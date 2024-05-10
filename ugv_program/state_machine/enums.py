from enum import IntEnum

class RobotState(IntEnum):
    INITIAL = 1
    IDLE = 2
    AUTONOMOUS = 3
    CONTROLLED = 4
    UPDATING = 5
    INACTIVE = 6


class RobotEvent(IntEnum):
    START_INIT = 1
    FINISH_INIT = 2
    START_MISN = 3
    HALT_MISN = 4  # pause or end
    CONT_MISN = 5
    AUTO = 6
    CONTROL = 7
    UPDATE = 8
    BACK = 9
    DELETE = 10
