from state_machine.state_machine import RobotStateMachine

robot = RobotStateMachine()
try:
    robot.start()
except KeyboardInterrupt:
    robot.stop()
    print("Robot Program is terminating...")
