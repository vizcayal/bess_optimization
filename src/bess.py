import pandas as pd
from datetime import datetime

class Bess:
    """
    Class that represents a Battery Energy Storage System (BESS).
    """
     
    def __init__(self, power_capacity: float = 100, energy_capacity: float = 200, efficiency: float = 0.9):
        """
        Parameters:
        
        power_capacity : maximum power output capacity to the system.
        energy_capacity : nominal energy storage capacity available to the system.
        efficiency : efficiency of the BESS (default: 0.9).
        """

        self.efficiency = efficiency                                # efficiency
        self.energy_capacity = energy_capacity / self.efficiency    # energy capacity adjusted by efficiency
        self.power_capacity = power_capacity                        # power capacity
        self.schedule_ds = None                                     # hourly schedule
        self.total_profit = None                                    # total profit of the optimal operation
        self.total_cycles = None                                    # total cycles of the optimal operation

    def get_efficiency(self) -> float:
        """
        Returns the efficiency of the BESS.
        """
        return self.efficiency
    
    def get_energy_capacity(self) ->float:
        """
        Returns the energy capacity of the BESS.
        """
        return self.energy_capacity
    
    def get_power_capacity(self) -> float:
        """
        Returns the power capacity of the BESS.
        """
        return self.power_capacity

    def set_schedule(self, schedule: pd.DataFrame):
        """
        Sets the optimal hourly schedule for the BESS.

        Parameters:
        schedule : Optimal Schedule to assign to the BESS.
        """
        self.schedule_ds = schedule
    
    def set_profit(self, profit):
        """
        set the total profit of the operation in Bess 
        """
        self.total_profit = profit

    def calc_total_cycles(self) -> float:
        """
        calculate the total cycles of the optimal schedule
        """
        total_charge = self.schedule_ds['charge_hour'].sum()
        self.cycles = round(total_charge / self.energy_capacity,1)
        return self.cycles
    
    def print_report(self):
        """
        print in the screen the total profit and cycles of the optimal schedule
        """
        self.calc_total_cycles()
        print('SUMMARY SCHEDULE OPERATION:')
        print(f'Total Profit: {self.total_profit}')
        print(f'Total Cycles: {self.cycles}')
    

    

    