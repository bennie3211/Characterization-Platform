import time
from routines.routine_base import BaseRoutine
from utils.math_tools import get_target_pose_along_tool_z
from utils.logger import ExperimentLogger
from utils.live_plot import LivePlotter


class DiscreteIndent(BaseRoutine):

    def run_logic(self, arduino_name: str, var_name: str, step_size_mm: float, total_dist_mm: float,
                  settling_time: float):
        """
        Moves in steps, pauses, records data, and plots results.

        Arguments:
            arduino_name (str): Name of the Arduino node to read sensor data from.
            var_name (str): Name of the variable/sensor to monitor.
            step_size_mm (float): Step size in mm for each movement.
            total_dist_mm (float): Total distance to indent in mm.
            settling_time (float): Time in seconds to wait after each movement before recording data.
        """

        arduino = self.arduinos.get(arduino_name)

        if not arduino:
            print(f"Error: Arduino '{arduino_name}' not found.")
            return

        steps = int(total_dist_mm / step_size_mm)
        print(f"Starting Discrete Indent: {steps} steps of {step_size_mm}mm")

        logger = ExperimentLogger("Indent_Discrete")
        logger.init_csv(["Step", "Timestamp", "TCP_X", "TCP_Y", "TCP_Z", "Distance", var_name])

        plotter = LivePlotter(
            title=f"Discrete Indent ({total_dist_mm}mm)",
            x_label="Distance (mm)",
            y_label=var_name,
            legend_name="Measured Value"
        )

        start_pose = self.robot.receive.getActualTCPPose()

        try:
            for i in range(steps):
                current_pose = self.robot.receive.getActualTCPPose()
                target = get_target_pose_along_tool_z(current_pose, step_size_mm)
                self.robot.control.moveL(target, 0.1, 0.5)

                time.sleep(settling_time)

                val = 0.0

                for _ in range(10):  # Average over 10 samples
                    received = arduino.get_latest_value(var_name)

                    if received is not None:
                        val += received

                    time.sleep(0.0001)

                    # Average
                val /= 10.0

                # Get current TCP pose
                tcp = self.robot.receive.getActualTCPPose()

                # Calculate distance moved from start
                distance = ((tcp[0] - start_pose[0]) ** 2 +
                            (tcp[1] - start_pose[1]) ** 2 +
                            (tcp[2] - start_pose[2]) ** 2) ** 0.5

                # Transform to mm
                distance *= 1000.0

                logger.log_data([i, time.time(), tcp[0], tcp[1], tcp[2], distance, val])
                plotter.update(distance, val)  # Plot distance vs value

                print(f"   Step {i + 1}/{steps}: {val}")

        except KeyboardInterrupt:
            self.robot.stop()
            print("Interrupted!")

        print("Discrete indentation complete. Returning...")
        self.robot.control.moveL(start_pose, 0.5, 0.5)

        plotter.save(logger.get_plot_path())
        logger.close()