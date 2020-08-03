from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from constants import SIMULATION_COUNT
from constants import AGENT_COUNT
from epidemiology import Epidemiology
from controller import Controller
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

simulation_df = pd.read_csv('simulation.csv', encoding="ISO-8859-1")

class Simulation:

    def __init__(self):
        headers = {'iteration': [], 'threshold': [], 'before_count': [], 'after_count': [], 'difference': []}
        self.results_file = 'results.csv'
        self.generate_csv_results_file(headers, self.results_file)
        for threshold in np.linspace(0.5, 1, 10):
            self.epidemiology = Epidemiology(threshold)
            self.controller = Controller(self.epidemiology.grid_health_df)
            self.simulation_df = simulation_df
            self.completed = False
            self.before_count = 0
            self.after_count = 0
            for i in range(SIMULATION_COUNT):
                self.model = RiderModel(AGENT_COUNT, 25, 100, self, self.epidemiology, self.controller)
                self.model.step()
                self.record_results(i, threshold)

    def record_results(self, iteration, threshold):
        data = {
            'iteration': [iteration],
            'threshold': [threshold],
            'before_count': [self.before_count],
            'after_count': [self.after_count],
            'difference': [self.after_count - self.before_count]
        }
        self.append_to_results_file(data, self.results_file)

    def append_to_results_file(self, data, filename):
        df = pd.DataFrame(data=data)
        df.to_csv(filename, mode='a', header=False, index=False)

    def generate_csv_results_file(self, data, filename):
        df = pd.DataFrame(data=data)
        df.to_csv(filename, index=False)

    def compute_infection(self, model):
        agent_healths = [agent.health for agent in self.model.schedule.agents]
        infected_count = agent_healths.count(1) + agent_healths.count(2)
        if self.completed == True:
            self.after_count = infected_count
        else:
            self.before_count = infected_count
        return infected_count

class RiderAgent(Agent, Simulation):
        
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
        try:
            return self.model.epidemiology.grid_health_df[str(self.destination)][self.hour]
        except KeyError:
            return 'safe'

    def getRideApproval(self):
        return_code = self.model.controller.ride_request(self.hour, self.health, self.origin, self.destination)
        if return_code > 0:
            self.hour = return_code
            return 0
        if return_code == 0:
            self.healthStatusUpdate()
        return return_code

    def healthStatusUpdate(self):
        covid_probability = self.model.epidemiology.risk_df[str(self.destination)][self.hour]
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

class RiderModel(Model, Simulation):
    """A model with some number of agents."""
    def __init__(self, N, width, height, simulation, epidemiology, controller):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.simulation = simulation
        self.controller = controller
        self.epidemiology = epidemiology
        # Create agents
        for i in range(self.num_agents):
            rider_id = random.randint(0, 4000000)
            hour = self.simulation.simulation_df[self.simulation.simulation_df['user_id'] == rider_id].hour.values[0].astype('int')
            origin = self.simulation.simulation_df[self.simulation.simulation_df['user_id'] == rider_id].pickup_grid_number.values[0].astype('int')
            destination = self.simulation.simulation_df[self.simulation.simulation_df['user_id'] == rider_id].dropoff_grid_number.values[0].astype('int')
            health = self.simulation.simulation_df[self.simulation.simulation_df['user_id'] == rider_id].state.values[0].astype('int')
            agent = RiderAgent(self, rider_id, health, hour, origin, destination)
            self.schedule.add(agent)

            x = agent.origin % 25
            y = agent.origin // 25 + 1
            self.grid.place_agent(agent, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"Infection": self.simulation.compute_infection},
            agent_reporters={"Health": "health"}
        )

    def step(self):
        self.simulation.completed = False
        self.datacollector.collect(self)
        self.schedule.step()
        self.simulation.completed = True
        self.datacollector.collect(self) 

simulation = Simulation()

# agent_counts = np.zeros((model.grid.width, model.grid.height))
# for cell in model.grid.coord_iter():
#     cell_content, x, y = cell
#     agent_count = len(cell_content)
#     agent_counts[x][y] = agent_count
# plt.imshow(agent_counts, interpolation='nearest')
# plt.colorbar()
# plt.show()

# agent_health = model.datacollector.get_agent_vars_dataframe()
# agent_health.head()

# infection = model.datacollector.get_model_vars_dataframe()
# infection.plot()
