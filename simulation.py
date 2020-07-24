from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from epidemiology import fetch_grid_health_df
from mobility import fetch_total_population_df
from controller import ride_request
import pandas as pd

def compute_infection(model):
    agent_healths = [agent.health for agent in model.schedule.agents]
    infected_count = agent_healths.count(1)
    infected_count += agent_healths.count(2)
    return infected_count

class RiderAgent(Agent):
    
    def __init__(self, unique_id, model, health, hour, origin, destination):
        super().__init__(unique_id, model)
        self.destination = destination
        self.origin = origin
        self.hour = hour
        self.health = health
        self.rideApproved = -1

    def getRiderHealthState(self):
        #UPDATE HEALTH HERE USING EPIDEMIOLOGY MODEL
        return this.health

    def getGridHealthState(self):
        return grid_health_df[str(destination)][hour]

    def getRideApproval(self):
        return_code = ride_request(self.hour, self.health, self.origin, self.destination)
        if return_code > 0:
            self.hour = return_code
            return 0
        return return_code

    def step(self):
        self.healthState = self.getRiderHealthState()
        self.gridHealthState = self.getGridHealthState()
        self.rideApproved = self.getRideApproval()
        
        if self.rideApproved == 0:
            y = self.destination / 25 + 1
            x = self.destination % 25
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
            hour = simulation_df[simulation_df['user_id'] == i].hour
            origin = simulation_df[simulation_df['pickup_grid'] == i].pickup_grid
            destination = simulation_df[simulation_df['dropoff_grid'] == i].dropoff_grid
            health = simulation_df[simulation_df['state'] == i].state
            agent = RiderAgent(i, health, hour, origin, destination, self)
            self.schedule.add(agent)

            y = agent.origin / 25 + 1
            x = agent.origin % 25
            self.grid.place_agent(agent, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"Infection": compute_infection},
            agent_reporters={"Health": "health"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

simulation_df = pd.read_csv('simulation.csv', encoding="ISO-8859-1")
population_df = fetch_total_population_df()
grid_health_df = fetch_grid_health_df()
model = RiderModel(1000, 25, 100)
for i in range(100):
    model.step()
