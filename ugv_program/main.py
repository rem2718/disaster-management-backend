from state_machine.state_machine import RobotStateMachine

try:
    robot = RobotStateMachine()
except KeyboardInterrupt:
    print("Robot Program is terminating...")
