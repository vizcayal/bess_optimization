import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD
from datetime import datetime

class Bess_Optimizer:

    def __init__(self, case = '', power_capacity = 100, energy_capacity = 200, efficiency = 0.9):
        self.case = case
        self.efficiency = efficiency
        self.energy_capacity = energy_capacity / self.efficiency
        self.energy_prices = None
        self.power_capacity = power_capacity
        self.reg_up_prices = None
        self.reg_down_prices = None
        self.total_profit = None


    def load_prices(self, energy_price_file):
        '''
        load energy prices from energy_price_file
        ''' 
        self.energy_prices = pd.read_csv(energy_price_file)
        self.energy_prices['Operating Day'] = pd.to_datetime(self.energy_prices['Operating Day'])
        self.energy_prices['Date'] = self.energy_prices['Operating Day'] + pd.to_timedelta(self.energy_prices['Operating Hour'] - 1, unit='h')
        self.energy_prices['Date'] = pd.to_datetime(self.energy_prices['Date'])
        self.energy_prices['Date'] = self.energy_prices['Date'].dt.strftime("%Y_%m_%d_%H")
        

    def load_regulation(self, regulation_price_file):
        '''
        load regulation prices from regulation_price_file
        '''
        self.reg_prices = pd.read_csv(regulation_price_file)
        self.reg_prices['Operating Day'] = pd.to_datetime(self.reg_prices['Operating Day'])
        self.reg_prices['Date'] = self.reg_prices['Operating Day'] + pd.to_timedelta(self.reg_prices['Operating Hour'] - 1, unit='h')
        self.reg_prices['Date'] = pd.to_datetime(self.reg_prices['Date'])
        self.reg_prices['Date'] = self.reg_prices['Date'].dt.strftime("%Y_%m_%d_%H")


    def optimize_period(self, start_day = None, end_day = None, initial_charge = 0):
        '''
        determine the optimal schedule for battery over the period from start_day to end_day (not included)
        includes the option to set the initial charge of the battery
        '''
        self.optimizer = LpProblem('Bess-Fluence', LpMaximize)                                            
        
        start_day = pd.to_datetime(start_day)
        end_day = pd.to_datetime(end_day)
        period = self.energy_prices[(self.energy_prices['Operating Day'] >= start_day) & (self.energy_prices['Operating Day'] <= end_day)]['Date'].tolist()
        days_list = list(self.energy_prices[(self.energy_prices['Operating Day'] >= start_day) & (self.energy_prices['Operating Day'] <= end_day)]['Operating Day'].unique())
        days_list = [day.strftime("%Y_%m_%d") for day in days_list]
        
        #Decision Variables
        
        # power generated by the battery hourly
        self.gen_hour = LpVariable.dicts(                                                                 
                                    name = 'gen_hour', 
                                    indices= period,
                                    lowBound = 0, 
                                    upBound = self.power_capacity
                                    )    

        # power charged by the battery hourly
        self.charge_hour = LpVariable.dicts(                                                                 
                                    name = 'charge_hour', 
                                    indices= period,
                                    lowBound = 0, 
                                    upBound = self.power_capacity
                                    )     
        
        # switch for activating charge
        # self.sw_charge = LpVariable.dicts(                                                                 
        #                             name = 'sw_charge', 
        #                             indices= period,
        #                             lowBound = 0, 
        #                             upBound = 1,
        #                             cat = "Binary"
        #                             )     
        
        # regulation up hourly
        self.reg_up = LpVariable.dicts(
                                        name = 'reg_up_hour',
                                        indices= period,
                                        lowBound = 0,
                                        upBound = self.power_capacity
                                        )
        
        # switch for regulation up
        # self.sw_reg_up = LpVariable.dicts(                                                                 
        #                             name = 'sw_reg_up', 
        #                             indices= period,
        #                             lowBound = 0, 
        #                             upBound = 1,
        #                             cat = "Binary"
        #                             )  

        # regulation down hourly                        
        self.reg_down = LpVariable.dicts(
                                        name = 'reg_down_hour',
                                        indices= period,
                                        lowBound = 0,
                                        upBound = self.power_capacity
                                        )

        # total charge hourly
        self.state_of_charge = LpVariable.dicts(
                                        name = 'state_of_charge',
                                        indices= period,
                                        lowBound = 0,
                                        upBound = self.energy_capacity
                                        )

        # objective function
        self.optimizer += lpSum(
                                self.energy_prices[self.energy_prices['Date']==hour]['Price'].iloc[0] * self.gen_hour[hour] -
                                self.energy_prices[self.energy_prices['Date']==hour]['Price'].iloc[0] * self.charge_hour[hour] +
                                self.reg_prices[self.reg_prices['Date']==hour]['Regulation Up'].iloc[0] * self.reg_up[hour] +
                                self.energy_prices[self.energy_prices['Date']==hour]['Price'].iloc[0] * self.reg_up[hour] * 0.1 +
                                self.reg_prices[self.reg_prices['Date']==hour]['Regulation Down'].iloc[0] * self.reg_down[hour] +
                                self.energy_prices[self.energy_prices['Date']==hour]['Price'].iloc[0] * self.reg_down[hour] * 0.1 
                                for hour in period
                                )
        
        # initializing total charge 
        self.optimizer += self.state_of_charge[period[0]] == initial_charge

        
        for index in range(len(period)):
                hour = period[index]

                # generation plus regulation up should be less than capacity
                self.optimizer += (self.gen_hour[hour] + self.reg_up[hour]) <= self.power_capacity
                
                # generation plus regulation up should be less than equal to battery charge
                self.optimizer += self.gen_hour[hour] + self.reg_up[hour] <= 0.9 * self.state_of_charge[hour] 
                
                # charging rate plus regulation down should be less than equal to remaining capacity of charge
                self.optimizer +=   (
                                    self.charge_hour[hour] + self.reg_down[hour] <= 
                                    (1 / self.efficiency) * (self.energy_capacity - self.state_of_charge[hour]) 
                                    )
        
        # iterate over the days in the period
        # only 1 cycle of charge/discharge per day
        for day in days_list:
            hour_day = [hour for hour in period if day in hour]
            
            self.optimizer += lpSum(
                                self.gen_hour[hour] 
                                for hour in hour_day
                                ) <= self.efficiency * self.energy_capacity 
        
            self.optimizer += lpSum(
                                    self.charge_hour[hour] 
                                    for hour in hour_day
                                    ) <= (1/self.efficiency) * self.energy_capacity 
                

        # temporary dependency on state of charge for all hours
        for index in range(len(period)):
            if index > 0:
                past_hour = period[index-1]
                hour = period[index]
                self.optimizer += (self.state_of_charge[hour] == + self.state_of_charge[past_hour]                   
                                                                 + self.charge_hour[past_hour]  * self.efficiency    
                                                                 - self.gen_hour[past_hour] * (1/self.efficiency)    
                                                                 + 0.1 * self.reg_down[past_hour]
                                                                 + 0.1 * self.reg_up[past_hour]  
                                    )
                
        self.optimizer.solve(PULP_CBC_CMD(msg=False))
        self.total_profit = self.optimizer.objective.value()


    def get_output_dataset(self):
        '''
        print the results of the optimization and the values of total profit
        '''
        vars = ['gen_hour', 'charge_hour', 'reg_up_hour', 'reg_down_hour', 'state_of_charge']
        results_dict = {}

        for var in vars:
            results_dict[var] = {}
            for v in self.optimizer.variables():
                if v.name.startswith(var):
                    day_hour = v.name.replace(var + '_', '')
                    day_hour = day_hour.replace('_', '-')
                    day_hour = datetime.strptime(day_hour, '%Y-%m-%d-%H')
                    results_dict[var][day_hour] = round(v.varValue,2)
        self.output_ds = pd.DataFrame.from_dict(results_dict)
        self.output_ds.to_csv(f'results-{self.case}.csv')
    