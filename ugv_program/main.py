from state_machine.state_machine import RobotStateMachine

robot = RobotStateMachine()
try:
    robot.start()
except KeyboardInterrupt:
    print("Robot Program is terminating...")
    robot.stop()
