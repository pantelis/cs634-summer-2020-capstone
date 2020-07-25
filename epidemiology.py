from mobility import fetch_total_population_df
import pandas as pd
import numpy as np

t = np.linspace(0, 24, 24)

population_df = fetch_total_population_df()

def fetch_grid_health_df(safety_threshold):
    quantiles = population_df.quantile(safety_threshold,axis=1)
    grid_health_df = population_df.copy()

    for i in range(24):
        grid_health_df.loc[i] = grid_health_df.loc[i].apply(lambda x: 'safe' if x < quantiles[i] else 'unsafe')

    return grid_health_df

def calculate_risk(N, i):
    upper_bound = population_df.quantile(0.95,axis=1)
    I0 = 0.2*N
    R0 = 0.1*N
    S0 = N - I0 - R0
    gamma = 1/336
    beta = min(N / upper_bound[i], 0.75)
    try:
        return beta * S0 * I0 / N - gamma * I0
    except ZeroDivisionError:
        return 0

def fetch_risk_df():
    risk_df = population_df.copy()
    for i in range(24):
        risk_df.loc[i] = risk_df.loc[i].apply(lambda x: calculate_risk(max(x, 0), i))
    risk_df.fillna(0, inplace=True)
    return risk_df / population_df