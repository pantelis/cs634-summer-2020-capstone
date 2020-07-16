import pandas as pd
import numpy as np

train_df = pd.read_csv('../training_data.csv', encoding="ISO-8859-1")
matrix = train_df.groupby(['pickup_grid_number','dropoff_grid_number']).size().unstack().fillna(0)

matrixByHours = train_df.groupby(['hour','pickup_grid_number','dropoff_grid_number']).size().unstack().fillna(0)

pickup_matrix = train_df.groupby(['hour', 'pickup_grid_number']).size().unstack().fillna(0)
dropoff_matrix = train_df.groupby(['hour', 'dropoff_grid_number']).size().unstack().fillna(0)
pickup_matrix.fillna(0, inplace=True)
dropoff_matrix.fillna(0, inplace=True)

change_obj = {}
for i in range(1, 2500):
    try:
        if i in dropoff_matrix[:].columns and i in pickup_matrix[:].columns:
            change_obj[str(i)] = dropoff_matrix[:][i] - pickup_matrix[:][i]
        elif i in dropoff_matrix[:].columns:
            change_obj[str(i)] = dropoff_matrix[:][i]
        elif i in pickup_matrix[:].columns:
            change_obj[str(i)] = -pickup_matrix[:][i]

    except KeyError:
        pass


#net_change_df is a 24x1010 (hour by zone) matrix containing the net change in a given zone
#a positive value implies more people entering the zone then leaving
#a negative value implies more people leaving the zone then entering
net_change_df = pd.DataFrame(change_obj)
