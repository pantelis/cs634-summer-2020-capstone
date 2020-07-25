from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from epidemiology import fetch_grid_health_df, fetch_risk_df
from mobility import fetch_total_population_df
from controller import ride_request
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

SAFETY_THRESHOLD = 0.95

def compute_infection(model):
    agent_healths = [agent.health for agent in model.schedule.agents]
    infected_count = agent_healths.count(1) + agent_healths.count(2)
    print('infected_count:', infected_count)
    return infected_count

class RiderAgent(Agent):
    
    def __init__(self, model, unique_id, health, hour, origin, destination):
        super().__init__(unique_id, model)
        self.destination = destination
        self.origin = origin
        self.hour = hour
        self.health = health
        self.rideApproved = -1

    def getRiderHealthState(self):
        return self.health

    def getGridHealthState(self):
        return grid_health_df[str(self.destination)][self.hour]

    def getRideApproval(self):
        return_code = ride_request(self.hour, self.health, self.origin, self.destination)
        if return_code > 0:
            self.hour = return_code
            return 0
        if return_code == 0:
            self.healthStatusUpdate()
        return return_code

    def healthStatusUpdate(self):
        covid_probability = risk_df[str(self.destination)][self.hour]
        for i in range(random.randint(2, 6)):
            simulation = random.random()
            if simulation < covid_probability:
                self.health = 1

    def step(self):
        self.healthState = self.getRiderHealthState()
        self.gridHealthState = self.getGridHealthState()
        self.rideApproved = self.getRideApproval()
        
        if self.rideApproved == 0:
            x = self.destination % 25
            y = self.destination // 25 + 1
            newPos = x,y
            self.model.grid.move_agent(self, newPos)
        self.health = self.getRiderHealthState()

class RiderModel(Model):
    """A model with some number of agents."""
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            rider_id = random.randint(0, 4000000)
            hour = simulation_df[simulation_df['user_id'] == rider_id].hour.values[0].astype('int')
            origin = simulation_df[simulation_df['user_id'] == rider_id].pickup_grid_number.values[0].astype('int')
            destination = simulation_df[simulation_df['user_id'] == rider_id].dropoff_grid_number.values[0].astype('int')
            health = simulation_df[simulation_df['user_id'] == rider_id].state.values[0].astype('int')
            agent = RiderAgent(self, rider_id, health, hour, origin, destination)
            self.schedule.add(agent)

            x = agent.origin % 25
            y = agent.origin // 25 + 1
            self.grid.place_agent(agent, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"Infection": compute_infection},
            agent_reporters={"Health": "health"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.datacollector.collect(self)

simulation_df = pd.read_csv('simulation.csv', encoding="ISO-8859-1")
population_df = fetch_total_population_df()
grid_health_df = fetch_grid_health_df(SAFETY_THRESHOLD)
risk_df = fetch_risk_df()
model = RiderModel(1000, 25, 100)
model.step()

agent_counts = np.zeros((model.grid.width, model.grid.height))
for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    agent_count = len(cell_content)
    agent_counts[x][y] = agent_count
plt.imshow(agent_counts, interpolation='nearest')
plt.colorbar()
plt.show()

agent_health = model.datacollector.get_agent_vars_dataframe()
agent_health.head()

infection = model.datacollector.get_model_vars_dataframe()
infection.plot()
