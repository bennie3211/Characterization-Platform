import time
from routines.routine_base import BaseRoutine
from utils.math_tools import get_target_pose_along_tool_z
from utils.logger import ExperimentLogger
from utils.live_plot import LivePlotter


class ContinuousIndent(BaseRoutine):

    def run_logic(self, arduino_name: str, var_name: str, total_dist_mm: float = 10, acc: float = 0.1,
                  vel: float = 0.01):
        """
        Moves smoothly without stopping while measuring high-speed data.

        Arguments:
            arduino_name (str): Name of the Arduino node to read sensor data from.
            var_name (str): Name of the variable/sensor to monitor.
            total_dist_mm (float): Total distance to indent in mm. Default is 10mm.
            acc (float): Acceleration of movement in m/s^2. Default is 0.1
            vel (float): Speed of movement in m/s. Default is 0.01
        """

        arduino = self.arduinos.get(arduino_name)

        if not arduino:
            print(f"Error: Arduino '{arduino_name}' not found.")
            return

        print(f"Starting Continuous Scan: {total_dist_mm}mm @ {vel}m/s")

        logger = ExperimentLogger("Indent_Continuous")
        logger.init_csv(["Timestamp", "Time_Delta", "TCP_X", "TCP_Y", "TCP_Z", "Distance", var_name])

        plotter = LivePlotter(
            title=f"Continuous Scan ({vel}m/s)",
            x_label="Distance (mm)",
            y_label=var_name,
            legend_name="Sensor Data"
        )

        start_pose = self.robot.receive.getActualTCPPose()
        target_pose = get_target_pose_along_tool_z(start_pose, total_dist_mm)

        # 3. Async Move
        self.robot.control.moveL(target_pose, vel, 1.2, True)  # True = Async

        start_time = time.time()

        try:
            while self.robot.control.getAsyncOperationProgress() >= 0:
                now = time.time()
                elapsed = now - start_time

                # Get Data
                tcp = self.robot.receive.getActualTCPPose()

                val = arduino.get_latest_value(var_name)
                if val is None:
                    val = 0.0

                tcp = self.robot.receive.getActualTCPPose()

                distance = ((tcp[0] - start_pose[0]) ** 2 +
                            (tcp[1] - start_pose[1]) ** 2 +
                            (tcp[2] - start_pose[2]) ** 2) ** 0.5

                # Transform to mm
                distance *= 1000.0

                # Log
                logger.log_data([now, elapsed, tcp[0], tcp[1], tcp[2], distance, val])

                # Update Plot
                plotter.update(distance, val)

        except KeyboardInterrupt:
            print("Interrupted!")
            self.robot.control.stopL()

        print("Returning to start...")
        self.robot.control.moveL(start_pose, 0.5, 0.5)

        plotter.save(logger.get_plot_path())
        logger.close()