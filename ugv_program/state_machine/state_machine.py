import time

from state_machine.enums import RobotState, RobotEvent
from mqtt_clients.robot_client import RobotMQTTClient
from utils.config_interface import config_interface
from mqtt_clients.admin_client import *
from utils.cache import *

# run_rtmp(f"{Config.RTMP_URL}/{name}")


class RobotStateMachine:
    def __init__(self):
        self.prev = None
        self.state = None
        self.transition(RobotEvent.START_INIT)

    def transition(self, event):
        match event:
            case RobotEvent.START_INIT:
                self.prev = self.state
                self.state = RobotState.INITIAL
                self.init_robot()
                self.transition(RobotEvent.FINISH_INIT)
            case RobotEvent.FINISH_INIT:
                self.prev = self.state
                self.state = RobotState.IDLE
                self.idle_mode()
            case RobotEvent.START_MISN:
                self.prev = self.state
                self.state = RobotState.AUTONOMOUS
                self.auto_mode()
            case RobotEvent.HALT_MISN:
                self.prev = self.state
                self.state = RobotState.IDLE
                self.idle_mode()
            case RobotEvent.CONT_MISN:
                match self.prev:
                    case RobotState.AUTONOMOUS:
                        self.transition(RobotEvent.AUTO)
                    case RobotState.CONTROLLED:
                        self.transition(RobotEvent.CONTROL)
            case RobotEvent.AUTO:
                self.prev = self.state
                self.state = RobotState.AUTONOMOUS
                self.auto_mode()
            case RobotEvent.CONTROL:
                self.prev = self.state
                self.state = RobotState.CONTROLLED
                self.control_mode()
            case RobotEvent.UPDATE:
                self.prev = self.state
                self.state = RobotState.UPDATING
                self.update_robot()
                self.transition(RobotEvent.BACK)
            case RobotEvent.BACK:
                match self.prev:
                    case RobotState.IDLE:
                        self.transition(RobotEvent.HALT_MISN)
                    case RobotState.AUTONOMOUS:
                        self.transition(RobotEvent.AUTO)
                    case RobotState.CONTROLLED:
                        self.transition(RobotEvent.CONTROL)
            case RobotEvent.DELETE:
                self.prev = self.state
                self.state = RobotState.INACTIVE
                self.delete_robot()

    def init_robot(self):
        skipped, data = config_interface()
        broker = data["broker_addr"]
        if skipped:
            data = read_cache()
        else:
            update_cache(data)
            create_mqtt_user(broker, data["name"], data["password"])

        self.name = data["name"]
        self.password = data["password"]
        self.mqtt_client = RobotMQTTClient(self.name, self.password, broker)

    def update_robot(self):
        # TO-DO: cache
        # TO-DO: restart all connections
        pass

    def delete_robot(self):
        # TO-DO: stop everything
        pass

    def idle_mode(self):
        while True:
            time.sleep(1)
        # TO-DO: stop mqtt, rtmp
        # To-DO: sub broker
        pass

    def auto_mode(self):
        # TO-DO: pub sensor data
        # TO-DO: rtmp
        # TO-DO: sub broker
        # TO-DO: auto motions
        pass

    def control_mode(self):
        # TO-DO: pub sensor data
        # TO-DO: rtmp
        # TO-DO: sub broker
        # TO-DO: sub commands
        pass
