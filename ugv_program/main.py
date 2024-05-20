from state_machine.state_machine import RobotStateMachine
robot = None
try:
    robot = RobotStateMachine()
except KeyboardInterrupt:
    robot.mqtt_client.stop_client()
    robot.rtmp_client.stop_client()
    print("Robot Program is terminating...")
