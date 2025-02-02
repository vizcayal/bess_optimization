import pandas as pd
from datetime import datetime
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD
from src.bess import Bess
from utils.utils import date_to_timezone
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

class Bess_Optimizer:
        
    def __init__(self, case:str = 'test_0'):
        """
        Initialize the optimizer with a case name and properties for prices and total profit.

        Parameters:
        case: Identifier for the optimization case.
        self.energy_price = None
        self.total_profit = None
        """

        self.case = case                        # name for identify the optimization case
        self.reg_prices = None                  # hourly regulation price up and down
        self.energy_price = None                # hourly energy prices
        self.total_profit = None                # total profit of the Bess operation
    
    def load_prices(self, energy_price_file: str):
        '''
        load energy prices from energy_price_file
        ''' 
        self.energy_price = pd.read_csv(energy_price_file)
        self.energy_price['Operating Day'] = pd.to_datetime(self.energy_price['Operating Day'])
        self.energy_price['Date'] = self.energy_price['Operating Day'] + pd.to_timedelta(self.energy_price['Operating Hour'] - 1, unit='h')
        self.energy_price = date_to_timezone(self.energy_price, 'Date')
        self.energy_price['Date'] = self.energy_price['Date'].dt.strftime("%Y_%m_%d_%H")
        

    def load_regulation(self, regulation_price_file: str):
        '''
        load regulation prices from regulation_price_file
        '''
        self.reg_prices = pd.read_csv(regulation_price_file)
        self.reg_prices['Operating Day'] = pd.to_datetime(self.reg_prices['Operating Day'])
        self.reg_prices['Date'] = self.reg_prices['Operating Day'] + pd.to_timedelta(self.reg_prices['Operating Hour'] - 1, unit='h')
        self.reg_prices = date_to_timezone(self.reg_prices, 'Date')
        self.reg_prices['Date'] = self.reg_prices['Date'].dt.strftime("%Y_%m_%d_%H")

    def optimize_period(self, operated_bess: Bess, start_day: str, end_day:str, initial_charge: float = 0):
        '''
        determine the optimal schedule for Bess over the period from start_day to end_day
        includes the option to set an initial charge of the Bess 
        '''
        self.optimizer = LpProblem('Bess-Fluence', LpMaximize)
        bess_efficiency = operated_bess.get_efficiency()
        bess_power_capacity = operated_bess.get_power_capacity() 
        bess_energy_capacity = operated_bess.get_energy_capacity()                                        
        
        start_day = pd.to_datetime(start_day)
        end_day = pd.to_datetime(end_day)
        period = self.energy_price[(self.energy_price['Operating Day'] >= start_day) & (self.energy_price['Operating Day'] <= end_day)]['Date'].tolist()
        days_list = list(self.energy_price[(self.energy_price['Operating Day'] >= start_day) & (self.energy_price['Operating Day'] <= end_day)]['Operating Day'].unique())
        days_list = [day.strftime("%Y_%m_%d") for day in days_list]
        
        #Decision Variables
        
        # power generated by the Bess hourly
        self.gen_hour = LpVariable.dicts(                                                                 
                                    name = 'gen_hour', 
                                    indices= period,
                                    lowBound = 0, 
                                    upBound = bess_power_capacity
                                    )    

        # power charged by the Bess hourly
        self.charge_hour = LpVariable.dicts(                                                                 
                                    name = 'charge_hour', 
                                    indices= period,
                                    lowBound = 0, 
                                    upBound = bess_power_capacity
                                    )     
          
        
        # regulation up hourly
        self.reg_up = LpVariable.dicts(
                                        name = 'reg_up_hour',
                                        indices= period,
                                        lowBound = 0,
                                        upBound = bess_power_capacity
                                        )
        

        # regulation down hourly                        
        self.reg_down = LpVariable.dicts(
                                        name = 'reg_down_hour',
                                        indices= period,
                                        lowBound = 0,
                                        upBound = bess_power_capacity
                                        )

        # total charge hourly
        self.state_of_charge = LpVariable.dicts(
                                        name = 'state_of_charge',
                                        indices= period,
                                        lowBound = 0,
                                        upBound = bess_energy_capacity
                                        )

        # objective function
        self.optimizer += lpSum(
                                self.energy_price[self.energy_price['Date']==hour]['Price'].iloc[0] * self.gen_hour[hour] -
                                self.energy_price[self.energy_price['Date']==hour]['Price'].iloc[0] * self.charge_hour[hour] +
                                self.reg_prices[self.reg_prices['Date']==hour]['Regulation Up'].iloc[0] * self.reg_up[hour] +
                                self.energy_price[self.energy_price['Date']==hour]['Price'].iloc[0] * self.reg_up[hour] * 0.1 +
                                self.reg_prices[self.reg_prices['Date']==hour]['Regulation Down'].iloc[0] * self.reg_down[hour] +
                                self.energy_price[self.energy_price['Date']==hour]['Price'].iloc[0] * self.reg_down[hour] * 0.1 
                                for hour in period
                                )
        
        # initializing total charge 
        self.optimizer += self.state_of_charge[period[0]] == initial_charge

        
        for index in range(len(period)):
                hour = period[index]

                # generation plus regulation up should be less than capacity
                self.optimizer += (self.gen_hour[hour] + self.reg_up[hour]) <= bess_power_capacity
                
                # generation plus regulation up should be less than equal to battery charge
                self.optimizer += self.gen_hour[hour] + self.reg_up[hour] <= 0.9 * self.state_of_charge[hour] 
                
                # charging rate plus regulation down should be less than equal to remaining capacity of charge
                self.optimizer +=   (
                                    self.charge_hour[hour] + self.reg_down[hour] <= 
                                    (1 / bess_efficiency) * (bess_energy_capacity - self.state_of_charge[hour]) 
                                    )
        
        # iterate over the days in the period
        # only 1 cycle of charge/discharge per day
        for day in days_list:
            hour_day = [hour for hour in period if day in hour]
            
            self.optimizer += lpSum(
                                self.gen_hour[hour] 
                                for hour in hour_day
                                ) <= bess_efficiency * bess_energy_capacity 
        
            self.optimizer += lpSum(
                                    self.charge_hour[hour] 
                                    for hour in hour_day
                                    ) <= (1/bess_efficiency) * bess_energy_capacity 
                

        # temporary dependency on state of charge for all hours
        for index in range(len(period)):
            if index > 0:
                past_hour = period[index-1]
                hour = period[index]
                self.optimizer += (self.state_of_charge[hour] == + self.state_of_charge[past_hour]                   
                                                                 + self.charge_hour[past_hour]  * bess_efficiency    
                                                                 - self.gen_hour[past_hour] * (1/bess_efficiency)    
                                                                 + 0.1 * self.reg_down[past_hour]* bess_efficiency
                                                                 - 0.1 * self.reg_up[past_hour] * (1/bess_efficiency) 
                                    )

        self.optimizer.solve(PULP_CBC_CMD(msg=False))
        self.total_profit = round(self.optimizer.objective.value() , 1)
        self.process_optimal_schedule()
        

    def process_optimal_schedule(self) -> pd.DataFrame :
        '''
        process the hourly optimal schedule for the Bess
        into a pandas dataset
        '''
        vars = ['gen_hour', 'charge_hour', 'reg_up_hour', 'reg_down_hour', 'state_of_charge']
        schedule_dict = {}

        for var in vars:
            schedule_dict[var] = {}
            for v in self.optimizer.variables():
                if v.name.startswith(var):
                    day_hour = v.name.replace(var + '_', '')
                    day_hour = day_hour.replace('_', '-')
                    day_hour = datetime.strptime(day_hour, '%Y-%m-%d-%H')
                    schedule_dict[var][day_hour] = round(v.varValue,2)
        self.schedule_ds = pd.DataFrame.from_dict(schedule_dict)
    

    def get_optimal_schedule(self) -> pd.DataFrame:
        """
        return the hourly optimal schedule for the Bess 
        """
        return self.schedule_ds
    
    def save_hourly_report(self):
        '''
        save a csv hourly report into the output folder
        '''
        self.schedule_ds.to_csv(f'output/results-{self.case}.csv')

    def get_profit(self) -> float:
        """
        return the total profit for the optimal operation
        """
        return self.total_profit