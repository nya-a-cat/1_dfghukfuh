import numpy as np
from numpy.typing import NDArray

def load_points_from_obj(filepath: str) -> NDArray[np.float64]:
    """
    Load vertex coordinates from a .obj file.

    This function reads a .obj file and extracts the vertex coordinates,
    ignoring all other information such as faces, normals, etc.

    Parameters
    ----------
    filepath : str
        The path to the .obj file.

    Returns
    -------
    NDArray[np.float64]
        An array of shape (N, 3) containing the (x, y, z) coordinates
        of the N vertices found in the file.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    ValueError
        If the file contains no vertex lines.
    """
    points = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                # parts[0] is 'v', coordinates are parts[1], parts[2], parts[3]
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    points.append([x, y, z])
                except (ValueError, IndexError):
                    # Skip malformed lines
                    continue
    
    if not points:
        raise ValueError(f"No vertices found in the file: {filepath}")

    return np.array(points, dtype=np.float64)