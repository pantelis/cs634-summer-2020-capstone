import math

import pandas as pd
import numpy as np

class Controller():
    def __init__(self, grid_health_df):
        self.grid_health_df = grid_health_df

    def ride_request(self, hour, health, origin, destination):
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

        if self.grid_health_df[str(destination)][hour] == 'safe' and self.grid_health_df[str(origin)][hour] == 'safe':
            return 0

        for i in range(hour, 24):
            if self.grid_health_df[str(destination)][i] == 'safe' and self.grid_health_df[str(origin)][i] == 'safe':
                return i

        return -1

