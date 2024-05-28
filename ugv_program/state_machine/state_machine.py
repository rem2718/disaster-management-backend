import time
import sys

from interfaces.hw_interface.motors_control import move_motor, move_camera, move_arm
from interfaces.hw_interface.sensors import read_sensor_data, get_gps
from interfaces.mqtt_interface.robot_client import RobotMQTTClient
from interfaces.config_interface import config_interface
from state_machine.enums import RobotState, RobotEvent
from interfaces.rtmp_interface import RobotRTMPClient
from interfaces.hw_interface.auto import auto_motion
from interfaces.mqtt_interface.admin_client import *
from state_machine.stack import Stack
from config import config


motion_queue = []
admin_queue = []
WAIT_TIME = 0.0001


class RobotStateMachine:

    def __init__(self):
        self.states = Stack(3)

    def start(self):
        self.transition(RobotEvent.START_INIT)

    def stop(self):
        self.transition(RobotEvent.DELETE, {"deactivate": False})

    def state_setter(self, value):
        self.states.push(value)
        cur = self.states.cur().name if self.states.cur() else None
        prev = self.states.prev().name if self.states.prev() else None
        print(f"<prev: {prev}, cur: {cur}>")

    def transition(self, event, data=None):
        print(f"Event {RobotEvent(event).name} has occurred")

        if event == RobotEvent.START_INIT:
            self.state_setter(RobotState.INITIAL)
            self.init_robot()
            self.transition(RobotEvent.FINISH_INIT)
        elif event == RobotEvent.FINISH_INIT:
            self.state_setter(RobotState.IDLE)
            self.idle_mode()
        elif event == RobotEvent.START_MISN:
            self.state_setter(RobotState.AUTONOMOUS)
            self.auto_mode()
        elif event == RobotEvent.HALT_MISN:
            self.state_setter(RobotState.IDLE)
            self.idle_mode()
        elif event == RobotEvent.AUTO:
            self.state_setter(RobotState.AUTONOMOUS)
            self.auto_mode()
        elif event == RobotEvent.CONTROL:
            self.state_setter(RobotState.CONTROLLED)
            self.control_mode()
        elif event == RobotEvent.UPDATE:
            self.state_setter(RobotState.UPDATING)
            self.update_robot(data)
            self.transition(RobotEvent.BACK)
        elif event == RobotEvent.DELETE:
            self.state_setter(RobotState.INACTIVE)
            self.delete_robot(data)
        elif event == RobotEvent.BACK:
            prev = self.states.back()
            if prev == RobotState.IDLE:
                self.transition(RobotEvent.HALT_MISN)
            elif prev == RobotState.AUTONOMOUS:
                self.transition(RobotEvent.AUTO)
            elif prev == RobotState.CONTROLLED:
                self.transition(RobotEvent.CONTROL)
            else:
                print("Invalid state")

    def init_robot(self):
        skipped, data = config_interface()
        self.broker_addr = data["BROKER_ADDR"]
        print(f"a MQTT broker has detected with IP address {self.broker_addr}")
        config.update(data)
        if not skipped:
            create_mqtt_user(self.broker_addr, data["NAME"], data["PASSWORD"])
        if config.get("NAME") == "" or config.get("PASSWORD") == "":
            print("No robot has been configured before. please try again...")
            sys.exit()
        self.name = config.get("NAME")
        self.password = config.get("PASSWORD")
        self.broker_name = config.get("BROKER_NAME")
        self.mqtt_client = RobotMQTTClient(
            self.name,
            self.password,
            self.broker_name,
            self.broker_addr,
            motion_queue,
            admin_queue,
        )
        self.rtmp_client = RobotRTMPClient(
            self.name, self.password, config.get("RTMP_URL"), 0
        )

    def update_robot(self, data):
        config.update(data)
        self.name = data["NAME"]
        self.password = data["PASSWORD"]
        self.mqtt_client.stop_client()
        self.mqtt_client = RobotMQTTClient(
            self.name,
            self.password,
            self.broker_name,
            self.broker_addr,
            motion_queue,
            admin_queue,
        )
        self.rtmp_client.stop_client()
        self.rtmp_client = RobotRTMPClient(
            self.name, self.password, config.get("RTMP_URL"), 0
        )

    def delete_robot(self, data):
        if data["deactivate"]:
            config.update(
                {"NAME": "", "PASSWORD": "", "BROKER_ADDR": "", "BROKER_NAME": ""}
            )
            print("Robot is deactivating...")
        self.rtmp_client.stop_client()
        self.mqtt_client.stop_client()
        sys.exit()

    def idle_mode(self):
        global motion_queue
        self.rtmp_client.stop_client()
        while True:
            self.check_admin_queue()
            if motion_queue:
                motion_queue = []
            time.sleep(WAIT_TIME)

    def auto_mode(self):
        self.rtmp_client.start_client()
        while True:
            self.check_admin_queue()
            data = read_sensor_data()
            gps = get_gps()
            if data:
                topic = f"cloud/reg/{self.broker_name}/{self.name}/sensor-data"
                self.mqtt_client.publish(topic, data)
            if gps:
                topic = f"cloud/reg/{self.broker_name}/{self.name}/gps"
                self.mqtt_client.publish(topic, data)
            auto_motion()
            time.sleep(WAIT_TIME)

    def control_mode(self):
        self.rtmp_client.start_client()
        while True:
            self.check_admin_queue()
            self.check_motion_queue()
            data = read_sensor_data()
            gps = get_gps()
            if data:
                topic = f"cloud/reg/{self.broker_name}/{self.name}/sensor-data"
                self.mqtt_client.publish(topic, data)
            if gps:
                topic = f"cloud/reg/{self.broker_name}/{self.name}/gps"
                self.mqtt_client.publish(topic, data)
            time.sleep(WAIT_TIME)

    def check_admin_queue(self):
        elem = admin_queue.pop(0) if admin_queue else None
        if elem == None:
            return
        _, data = elem
        command = data["command"]
        if command == "start":
            self.transition(RobotEvent.START_MISN)
        elif command == "pause":
            self.transition(RobotEvent.HALT_MISN)
        elif command == "continue":
            self.transition(RobotEvent.BACK)
        elif command == "end":
            self.transition(RobotEvent.HALT_MISN)
        elif command == "update":
            new_data = {"NAME": data["name"], "PASSWORD": data["password"]}
            self.transition(RobotEvent.UPDATE, new_data)
        elif command == "delete":
            new_data = {"deactivate": True}
            self.transition(RobotEvent.DELETE, new_data)
        elif command == "switch":
            if data["state"] == "auto" and self.states.cur() == RobotState.CONTROLLED:
                self.transition(RobotEvent.AUTO)
            elif (
                data["state"] == "control"
                and self.states.cur() == RobotState.AUTONOMOUS
            ):
                self.transition(RobotEvent.CONTROL)
        else:
            print("Invalid admin command")

    def check_motion_queue(self):
        elem = motion_queue.pop(0) if motion_queue else None
        if elem == None:
            return
        _, data = elem
        dev = data["device"]
        if dev == "motor":
            move_motor(data["value"])
        elif dev == "camera":
            move_camera(data["value"])
        elif dev == "arm":
            move_arm(data["command"])
        else:
            print("Invalid motion command")
