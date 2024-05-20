from state_machine.state_machine import RobotStateMachine

robot = RobotStateMachine()
try:
    robot.start()
except KeyboardInterrupt:
    robot.mqtt_client.stop_client()
    robot.rtmp_client.stop_client()
    print("Robot Program is terminating...")
