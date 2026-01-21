import math
import numpy as np


def _axis_angle_to_matrix(rx, ry, rz):
    """
    Converts axis-angle representation to a rotation matrix SO(3).
    Implementation of the Rodrigues' rotation formula.

    Attributes:
        rx (float): Axis-angle representation component.
        ry (float): Axis-angle representation component.
        rz (float): Axis-angle representation component.

    Returns:
        np.ndarray: 3x3 rotation matrix.
    """
    # Compute the angle of rotation
    theta = math.sqrt(rx * rx + ry * ry + rz * rz)

    # Handle the case when the angle is very small
    if theta < 1e-6:
        return np.eye(3)

    # Normalize axis
    ux, uy, uz = rx / theta, ry / theta, rz / theta

    # Compute rotation matrix using Rodrigues' rotation formula
    c = math.cos(theta)
    s = math.sin(theta)
    C = 1 - c

    # Rotation matrix
    return np.array([
        [c + ux * ux * C, ux * uy * C - uz * s, ux * uz * C + uy * s],
        [uy * ux * C + uz * s, c + uy * uy * C, uy * uz * C - ux * s],
        [uz * ux * C - uy * s, uz * uy * C + ux * s, c + uz * uz * C]
    ])


def get_target_pose_along_tool_z(current_pose, z_step_mm):
    """
    Calculates a new pose in Base Frame by moving along the Tool Z axis.

    Attributes:
        current_pose (list): Current pose as [Px, Py, Pz, Rx, Ry, Rz].
        z_step_mm (float): Distance to move along the Tool Z axis in millimeters.

    Returns:
        list: New pose as [Px, Py, Pz, Rx, Ry, Rz].
    """
    # Convert mm to meters
    z_step_m = z_step_mm / 1000.0

    # Extract position and rotation
    P_base = np.array(current_pose[:3])
    R_base = _axis_angle_to_matrix(*current_pose[3:])

    # Translation vector in Tool Frame (0, 0, z)
    trans_tool = np.array([0, 0, z_step_m])

    # Calculate new position
    P_new = P_base + R_base.dot(trans_tool)

    # Return new pose
    return list(P_new) + list(current_pose[3:])