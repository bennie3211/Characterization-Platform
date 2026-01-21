from routines.routine_base import BaseRoutine

class TeachRoutine(BaseRoutine):

    def run_logic(self):
        """
        Puts the robot into 'Freedrive' (Teach) mode.
        The script waits for the user to press Enter to lock the robot again.
        """

        print("Enabling Teach Mode (Freedrive)...")
        print("You can now manually move the robot arm.")

        try:
            # Unlock the robot
            self.robot.control.teachMode()

            # Block code execution until user is done
            input("Press [ENTER] to lock the robot and finish...")

        except Exception as e:
            print(f"Error in teach mode: {e}")

        finally:
            self.robot.control.endTeachMode()
            print("Teach Mode Disabled. Robot locked.")