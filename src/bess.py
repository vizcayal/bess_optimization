import pandas as pd
from datetime import datetime

class Bess:
    def __init__(self, power_capacity = 100, energy_capacity = 200, efficiency = 0.9):

        self.efficiency = efficiency
        self.energy_capacity = energy_capacity / self.efficiency
        self.power_capacity = power_capacity
        self.schedule = None

    def get_efficiency(self):
        return self.efficiency
    
    def get_energy_capacity(self):
        return self.energy_capacity
    
    def get_power_capacity(self):
        return self.power_capacity

    def set_schedule(self, schedule):
        self.schedule = schedule
    

    

    