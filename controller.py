import math

import pandas as pd
import numpy as np

#This is the 24x2500x2500 matrix computed by the mobility model and epidemiological team
mobility_grid = {}

#This is the state of the user making the current request, it is passed in by agent based model simulation team
#It is passed in by the user making the request
state = 'healthy'

#This is the location the user is being picked up
#It is passed in by the user making the request
pickup_grid = 180

#This is the location the user is being dropped off
#It is passed in by the user making the request
dropoff_grid = 230

#This is the current time
#It is passed in by the user making the request
current_time = 12

#check if the user is currently sick
if state == 'sick':
    print('NOT allowed')


#Compute distance between coordinates, if less than about 1 mile (I am rounding for simplicity)
#then automatically allow
x_pickup = pickup_grid % 25
y_pickup = (pickup_grid / 25) + 1

x_dropoff = dropoff_grid % 25
y_dropoff = (dropoff_grid / 25) + 1

x_change = x_dropoff - x_pickup
y_change = y_dropoff - y_pickup

distance = math.sqrt(x_change^2 + y_change^2)
if distance < 15:
    print('ALLOWED')


#If both pickup and dropoff zones are safe then allow
if mobility_grid[current_time][dropoff_grid] == 'safe' and mobility_grid[current_time][pickup_grid] == 'safe':
    print('ALLOWED')

#If either pickup and dropoff zones are not safe, then cycle through the rest of the day to find
#an alternative time slot
for i in range(current_time, 24):
    if mobility_grid[current_time][dropoff_grid] == 'safe' and mobility_grid[current_time][pickup_grid] == 'safe':
        print('allowed at time :', i)

#If no safe time slots are allowed, refuse the trip
print('not allowed')

