from routines.routine_base import BaseRoutine


class OrientRoutine(BaseRoutine):

    def run_logic(self, rx: float, ry: float, rz: float, acc: float = 0.1, vel: float = 0.05):
        """
        Rotates the TCP to the defined orientation while keeping position (x, y, z) constant.

        Args:
            rx (float): Rotation around X axis in radians.
            ry (float): Rotation around Y axis in radians.
            rz (float): Rotation around Z axis in radians.
            acc (float): Acceleration in rad/s^2. Default is 0.1.
            vel (float): Speed in rad/s. Default is 0.05.
        """
        print(f"Rotating TCP to: [{rx:.2f}, {ry:.2f}, {rz:.2f}]")

        # Get current pose [x, y, z, rx, ry, rz]
        current_pose = self.robot.receive.getActualTCPPose()

        # Construct new pose
        target_pose = current_pose[:3] + [rx, ry, rz]

        try:
            # Move
            self.robot.control.moveL(target_pose, acc, vel)
            print("Orientation complete.")

        except Exception as e:
            print("Target pose orientation may be unreachable.")
            print(f"Error during orientation: {e}")