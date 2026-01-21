import threading
import serial
import json
import time
from collections import deque


class ArduinoNode(threading.Thread):
    """
    Threaded class to handle Arduino data acquisition and transfer.

    Arguments:
        port (str): Physical USB port address.
        baudrate (int): Communication boud rate.
        queue_len (int): Size of parsed JSON queue sample points.
        timeout (float): Timeout between communication send/receive and ACK

    Methods:
        run(): Main threaded loop.
        get_latest_value(key: str): Retrieve the latest value for a given key.
    """

    def __init__(self, port: str, baudrate: int = 115200, queue_len: int = 50, timeout: float = 0.2):
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.data_queue = deque(maxlen=queue_len)
        self.timeout = timeout

        self.running = True
        self.ser = None

    def run(self):
        """
        Main loop: transfers data to and from Arduino.
        Note: Runs at separate thread!
        """

        try:
            print(f"Setting up Arduino connection on {self.port}...")

            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)

            print(f"Connected to Arduino on {self.port}")

            # Allow time for Arduino to reset
            time.sleep(2)

            # Read, parse and store in the queue
            while self.running:

                # If data is available
                if self.ser.in_waiting > 0:
                    try:
                        line = self.ser.readline().decode('utf-8').strip()

                        # Expecting JSON formatted data
                        if line.startswith('{') and line.endswith('}'):
                            # Parse data to JSON
                            data = json.loads(line)

                            # Add timestamp
                            data['timestamp'] = time.time()

                            # Append to queue
                            self.data_queue.append(data)

                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass  # Ignore malformed packets

        except Exception as e:
            print(f"Connection error on {self.port}: {e}")

    def get_latest_value(self, key: str) -> float | None:
        """
        Retrieve the latest value for a given key.

        Argument
            key (str): Key to retrieve value for.

        Returns
            float | None: Value for the given key, or None if not found.
        """

        if len(self.data_queue) > 0:
            return self.data_queue[-1].get(key, None)

        return None

    def get_mean_value_samples(self, key: str, n: int = 10) -> float | None:
        """
        Calculate the mean of the last n values for a given key.

        Argument
            key (str): Key to retrieve values for.
            n (int): Number of samples to average.

        Returns
            float | None: Mean value, or None if not enough samples are available.
        """

        values = [entry.get(key, 0) for entry in list(self.data_queue)[-n:]]

        if values:
            return sum(values) / len(values)

        return None

    def get_mean_value_time(self, key: str, t: float = 1.0) -> float | None:
        """
        Calculate the mean of values for a given key over the last t seconds.

        Argument
            key (str): Key to retrieve values for.
            t (float): Time window in seconds.

        Returns
            float | None: Mean value, or None if not enough samples are available.
        """

        current_time = time.time()
        values = [entry.get(key, 0) for entry in self.data_queue if (current_time - entry['timestamp']) <= t]

        if values:
            return sum(values) / len(values)

        return None

    def send_command(self, command: str):
        """
        Sends a raw string command to the Arduino.
        Automatically appends a newline ('\\n') which is standard for Arduino parsers.
        """
        if self.ser and self.ser.is_open:
            try:
                full_cmd = f"{command}\n"
                self.ser.write(full_cmd.encode('utf-8'))
                print(f"Sent to {self.port}: {command}")
            except Exception as e:
                print(f"Error writing to {self.port}: {e}")
        else:
            print(f"Cannot send command. Serial port {self.port} is not open.")

    def stop(self):
        """
        Stop the thread and close the connection.
        """

        print(f"Stopping Arduino thread on {self.port}...")

        self.running = False
        if self.ser:
            self.ser.close()