import time
import rtde_control
import rtde_receive
import rtde_io
import socket


class RobotInterface:
    """
    Manages connection to a UR robot via RTDE and Dashboard interfaces.

    Arguments:
        robot_ip (str): IP address of the robot.

    Attributes:
        ip (str): IP address of the robot.
        control (RTDEControlInterface): RTDE control interface.
        receive (RTDEReceiveInterface): RTDE receive interface.
        io (RTDEIOInterface): RTDE IO interface.

    Methods:
        connect(): Establishes connection to RTDE and Dashboard.
        reconnect(): Attempts to reconnect if connection is lost.
        is_ready(): Checks if robot is powered on and not in safety stop.
        disconnect(): Closes RTDE connections.
    """

    def __init__(self, robot_ip: str):
        """
        Initializes the RobotInterface with the given robot IP.
        Immediately attempts to connect upon initialization.

        Arguments:
            robot_ip (str): IP address of the robot.
        """
        self.ip = robot_ip

        self.control = None
        self.receive = None
        self.io = None

        # Connect immediately
        self.connect()

    def connect(self):
        """
        Attempts to establish connection to RTDE.
        """

        print(f"Connecting to Robot at {self.ip}...")

        try:
            self.control = rtde_control.RTDEControlInterface(self.ip)
            self.receive = rtde_receive.RTDEReceiveInterface(self.ip)
            self.io = rtde_io.RTDEIOInterface(self.ip)

            print("Robot RTDE Connected.")
        except Exception as e:
            print(f"Connection Failed: {e}")
            raise e

    def reconnect(self):
        """
        Closes existing connections and tries to reconnect loop.
        Called AFTER issues are fixed, detected by the pendant or other monitoring.
        """

        print("Re-initiating connection to robot.")

        # Disconnect existing connections
        try:
            if self.control:
                self.control.stopScript()
                self.control.disconnect()
            if self.receive:
                self.receive.disconnect()
            if self.io:
                self.io.disconnect()
        except:
            # Ignore errors during disconnect
            pass

        # Retry connection until successful
        while True:
            try:
                self.connect()

                if self.is_ready():
                    print("Reconnection successful.")
                    return

                else:
                    print("Connected but robot not ready yet.")
                    time.sleep(3)

            except Exception:
                print("   Retrying in 3 seconds.")
                time.sleep(3)

    def is_ready(self):
        """
        Checks if the robot is connected and ready for operation.
        Returns True if the robot is powered on and not in safety stop.
        """

        if self.control is None or self.receive is None:
            return False

        try:
            if not self.receive.isConnected():
                return False

            if self.receive.getSafetyStatusBits() > 1:
                return False

            return True
        except:
            return False

    def disconnect(self):
        try:
            if self.control:
                self.control.stopScript()
                self.control.disconnect()

            if self.receive:
                self.receive.disconnect()

            if self.io:
                self.io.disconnect()
        except:
            pass