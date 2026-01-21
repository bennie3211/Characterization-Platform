import time
from hardware.arduino import ArduinoNode
from hardware.robot import RobotInterface
from routines.teach import TeachRoutine
from routines.orient import OrientRoutine
from routines.indent_continuous import ContinuousIndent
from routines.zero import ZeroRoutine
from routines.indent_discrete import DiscreteIndent


def main():
    arduinos = {
        "force": ArduinoNode(port="/dev/ttyACM0", baudrate=115200, queue_len=10, timeout=0.2)
    }

    # Start Arduino Threads
    for node in arduinos.values():
        node.start()

    # Setup Robot
    # Check the network controller mask -> Should be equal to the one on the UR controller!
    # Check utils/network_manager.py
    robot = RobotInterface("192.168.100.1")

    # Instantiate routines with hardware references
    routines = {
        'move': TeachRoutine(robot, arduinos),
        'orient': OrientRoutine(robot, arduinos),
        'indd': DiscreteIndent(robot, arduinos),
        'indc': ContinuousIndent(robot, arduinos),
        'zero': ZeroRoutine(robot, arduinos)
    }

    # Main logic loop
    try:
        while True:

            print("Commands:")
            print("     tare <ard> <samples>")
            print("     cal  <ard> <known_weight>")
            print("     loop <ard> <var>")
            print(" ")
            print("     exit")
            print("     move")
            print("     orient <Rx> <Ry> <Rz> [acc] [vel]")
            print("     zero <ard> <var> <thres> <step> <dist> [acc] [vel]")
            print("     indd <ard> <var> <step> <dist> <settle>")
            print("     indc <ard> <var> <dist> [acc] [vel]")

            user_input = input("\nCommand > ").strip().split()

            # Check for empty input
            if not user_input:
                continue

            # Parse command
            cmd = user_input[0].lower()

            # Quick tare implementation
            if cmd == 'tare':
                try:
                    ard_name = user_input[1]
                    samples = int(user_input[2])

                    if ard_name in arduinos:
                        arduinos[ard_name].send_command(f"tare:{int(samples)}")
                        print(f"Taring '{ard_name}' for {samples} samples.")
                    else:
                        print(f"Arduino '{ard_name}' not found.")
                except (IndexError, ValueError):
                    print("Usage: tare <arduino_name> <samples>")

            # Quick calibration implementation
            elif cmd == 'cal':
                try:
                    ard_name = user_input[1]
                    weight = float(user_input[2])

                    if ard_name in arduinos:
                        arduinos[ard_name].send_command(f"cal:{weight}")
                        print(f"Calibrating '{ard_name}' for units {weight}.")
                    else:
                        print(f"Arduino '{ard_name}' not found.")
                except (IndexError, ValueError):
                    print("Usage: cal <arduino_name> <known_weight>")


            # Debug streaming implementation
            elif cmd == 'debug':
                try:
                    ard_name = user_input[1]
                    var_name = user_input[2]

                    print(f"Streaming '{var_name}' from Arduino '{ard_name}'.")
                    print("Press Ctrl+C to stop.")

                    try:
                        while True:
                            value = arduinos[ard_name].get_latest_value(var_name)
                            print(f"\r{var_name}: {value}" + " " * 20, end="", flush=True)

                    except KeyboardInterrupt:
                        print("\nLooping stopped by user.")

                except (IndexError, ValueError):
                    print("Usage: debug <arduino_name> <var_name>")


            # Execute a routine if registered
            elif cmd in routines:
                try:
                    # Collection of arguments for the routine
                    args = []

                    # Convert rest of input to floats/strings as needed by a specific routine.
                    # Assuming all args are float for simplicity,
                    # but possible to add specific casting in the routine itself.
                    for arg in user_input[1:]:
                        try:
                            args.append(float(arg)) # Cast to float
                        except ValueError:
                            args.append(arg)  # Fallback to string

                    # Execute the routine
                    routines[cmd].execute(*args)

                except Exception as e:
                    print(f"Execution Error: {e}")
            else:
                print("Unknown routine or command.")

    # Handle global interrupt
    except KeyboardInterrupt:
        print("\nClosing program.")

    finally:
        # Stop Arduino Threads
        for node in arduinos.values():
            node.stop()
            node.join()

        # Disconnect Robot
        robot.disconnect()

        print("Program closed.")

if __name__ == "__main__":
    main()