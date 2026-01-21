class BaseRoutine:

    def __init__(self, robot, arduinos):
        """
        Parameters:
            robot (RobotInterface): The robot interface for controlling the robot.
            arduinos (dict): A dictionary of ArduinoNode instances for sensor data.

        Attributes:
            robot: The robot interface for controlling the robot.
            arduinos: A dictionary of ArduinoNode instances for sensor data.
        """
        self.robot = robot
        self.arduinos = arduinos

    def execute(self, *args):
        if not self.ready():
            # Robot is not ready, skip execution
            return

        try:
            self.run_logic(*args)
        except Exception as e:
            print(f"Error during routine execution: {e}")
            self.robot.reconnect()

    def ready(self):
        while not self.robot.is_ready():
            print("\nROBOT STATUS NOT READY")
            print("   1. Check the Teach Pendant.")
            print("   2. Clear any Protective/Emergency Stops manually.")
            print("   3. Enable the robot and release brakes.")
            print("   4. Once the light is GREEN on the pendant, press [ENTER] here.")

            user_choice = input("   (Press [ENTER] to retry, or type 'x' to cancel command): ")

            if user_choice.lower() == 'x':
                return False

            # Try to reconnect/check status
            self.robot.reconnect()

        return True

    def run_logic(self, *args):
        raise NotImplementedError("Run logic method must be implemented")