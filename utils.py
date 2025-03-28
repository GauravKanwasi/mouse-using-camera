
import numpy as np

def calculate_distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def map_to_screen(x, y, frame_width, frame_height, screen_width, screen_height):
    """Map coordinates from frame to screen resolution."""
    screen_x = np.interp(x, [0, frame_width], [0, screen_width])
    screen_y = np.interp(y, [0, frame_height], [0, screen_height])
    return screen_x, screen_y
