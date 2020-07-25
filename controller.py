import math

import pandas as pd
import numpy as np
from simulation import SAFETY_THRESHOLD
from epidemiology import fetch_grid_health_df

grid_health_df = fetch_grid_health_df(0.95)

def ride_request(hour, health, origin, destination):
    if health == 2:
        return -1

    x_origin = origin % 25
    y_origin = (origin / 25) + 1

    x_destination = destination % 25
    y_destination = (destination // 25) + 1

    x_change = x_destination - x_origin
    y_change = y_destination - y_origin

    distance = math.sqrt(x_change**2 + y_change**2)
    if distance < 15:
        return 0

    if grid_health_df[str(destination)][hour] == 'safe' and grid_health_df[str(origin)][hour] == 'safe':
        return 0

    for i in range(hour, 24):
        if grid_health_df[str(destination)][i] == 'safe' and grid_health_df[str(origin)][i] == 'safe':
            return i

    return -1

