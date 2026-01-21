# Robot Control and Data Acquisition Project

This project provides a framework for controlling a Universal Robot (UR) and acquiring data from Arduino-based sensors. It includes a variety of routines for robot movement, orientation, and indentation tasks, as well as a command-line interface for manual control and calibration.

## Features

- **Robot Control**: Interface for Universal Robots using the RTDE (Real-Time Data Exchange) protocol.
- **Sensor Integration**: Threaded Arduino nodes for real-time data acquisition via serial communication (JSON format).
- **Routines**:
    - `move`: Manual teaching/movement.
    - `orient`: Adjust robot orientation.
    - `indd`: Discrete indentation routine.
    - `indc`: Continuous indentation routine.
    - `zero`: Routine to find or define a zero point based on sensor thresholds.
- **Utilities**: Includes live plotting, network management (experimental), and math tools.

## Requirements

Before setting up the project, ensure you have Python installed. The project depends on several libraries, which are listed in `requirements.txt`.

Key dependencies include:
- `ur-rtde`: For communication with Universal Robots.
- `pyserial`: For serial communication with Arduino nodes.
- `numpy`: For mathematical operations.
- `matplotlib`: For data visualization and live plotting.

## Setup and Installation

1.  **Clone the Repository**:
    Download or clone this project to your local machine.

2.  **Install Dependencies**:
    Navigate to the project root directory and install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
    
3.  **Network setup (Temporary)**:

    To allow communication between the PC and the UR robot, configure the Ethernet
    interface so both devices are on the same subnet.

    **UR Robot**
    - IP Address: `192.169.100.1`
    - Subnet Mask: `255.255.255.0` (`/24`)

    **PC (Example)**
    - IP Address: `192.169.100.5`
    - Subnet Mask: `255.255.255.0`

    > ⚠️ These settings are temporary and will be lost after reboot.

    ### Linux

    Identify the Ethernet interface:
    ```bash
    ip a
    ```

    Assign IP address (replace `eth0` with your interface name):
    ```bash
    sudo ip addr flush dev eth0
    sudo ip addr add 192.169.100.5/24 dev eth0
    sudo ip link set eth0 up
    ```

    Verify connection:
    ```bash
    ping 192.169.100.1
    ```

    ### Windows

    Open **Command Prompt as Administrator**.

    List network interfaces:
    ```cmd
    netsh interface ipv4 show interfaces
    ```

    Assign IP address (replace `"Ethernet"` if needed):
    ```cmd
    netsh interface ipv4 set address name="Ethernet" static 192.169.100.5 255.255.255.0
    ```

    Verify connection:
    ```cmd
    ping 192.169.100.1
    ```

    Revert to DHCP (optional):
    ```cmd
    netsh interface ipv4 set address name="Ethernet" dhcp
    ```

4.  **Hardware Configuration**:
    - **Robot**: Ensure your UR robot is powered on and reachable on the network. The default IP in `main.py` is `192.168.100.1`.
    - **Arduino**: Connect your Arduino(s) via USB. The default configuration in `main.py` expects an Arduino named `force` on port `/dev/ttyACM0` (Linux) or a corresponding COM port (Windows).
    - **Force Module Design**: The mechanical design of the force module (also implemented in the main controller under `force`)
     is provided in the `design/` directory. This directory contains all corresponding CAD files in
     `.step` format.

## How it Works

The project is centered around a main control loop in `main.py`.

1.  **Initialization**: The script initializes `ArduinoNode` instances for sensors and a `RobotInterface` for the UR robot.
2.  **Command Interface**: A command-line interface allows you to send instructions to the system. Available commands include:
    - `tare <arduino> <samples>`: Tare a specific Arduino sensor.
    - `cal <arduino> <weight>`: Calibrate an Arduino sensor with a known weight.
    - `debug <arduino> <variable>`: Stream live values from a sensor to the console.
    - `move`: Start the teaching routine.
    - `orient`, `zero`, `indd`, `indc`: Execute specific robotic routines with parameters.
3.  **Routines**: Each routine (found in the `routines/` directory) inherits from `BaseRoutine` and implements specific logic for interacting with the robot and sensors.

## Usage

To start the project, run:
```bash
python main.py
```
Follow the on-screen prompts to issue commands and execute routines. Ensure the robot is in a safe state and the Teach Pendant is accessible for safety confirmations.
