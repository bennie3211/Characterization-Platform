from routines.routine_base import BaseRoutine
from utils.math_tools import get_target_pose_along_tool_z


class ZeroRoutine(BaseRoutine):

    def run_logic(self, arduino_name: str, var_name: str, threshold: float, step_size_mm: float = 1,
                  max_size_mm: float = 10.0, acc: float = 0.1, vel: float = 0.05):
        """
        Moves Tool Z+ in steps until sensor value > threshold.
        Then moves back one step to unload the applied force.

        Arguments:
            arduino_name (str): Name of the Arduino node to read sensor data from.
            var_name (str): Name of the variable/sensor to monitor.
            threshold (float): Threshold value to trigger stopping.
            step_size_mm (float): Step size in mm for each movement. Default is 1.
            max_size_mm (float): Maximum distance in mm to move before stopping. Default is 10.
            acc (float): Acceleration for movements in m/s^2. Default is 0.1.
            vel (float): Speed for movements in m/s. Default is 0.05.
        """
        # Validate Hardware
        arduino = self.arduinos.get(arduino_name)

        if not arduino:
            print(f"Error: Arduino '{arduino_name}' not found.")
            return

        print(f"Zeroing: {var_name} > {threshold} (Step: {step_size_mm}mm / Max: {max_size_mm}mm)")

        total_steps_moved = 0.0

        try:
            while True:
                # Check Sensor
                val = arduino.get_latest_value(var_name)

                # Handle initial None values if the sensor is warming up
                if val is None:
                    val = 0.0

                print(f"\rSensor: {val:.2f} / {threshold:.2f}", end="", flush=True)

                if val >= threshold:
                    print(f"\nThreshold hit. Backing off {step_size_mm} mm.")

                    # Back off logic
                    current_pose = self.robot.receive.getActualTCPPose()
                    target = get_target_pose_along_tool_z(current_pose, -step_size_mm)

                    # Move back one step
                    self.robot.control.moveL(target, acc, vel)
                    break

                # Update and check max distance
                total_steps_moved += step_size_mm

                if total_steps_moved > max_size_mm:
                    print("\nMax distance reached without hitting threshold.")
                    break

                # Move Forward logic
                current_pose = self.robot.receive.getActualTCPPose()
                target = get_target_pose_along_tool_z(current_pose, step_size_mm)

                # Move one step forward
                self.robot.control.moveL(target, acc, vel)

        except KeyboardInterrupt:
            print("Zeroing interrupted manually.")
            self.robot.control.stopL()

        print("Zero Action Complete.")