from src.bess_optimizer import Bess_Optimizer

optimizer = Bess_Optimizer(case = 'case1', power_capacity = 100, energy_capacity = 200, efficiency = 0.9)
optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
optimizer.optimize_period(start_day = '1/1/2023', end_day = '2/1/2023', initial_charge = 0)
optimizer.get_output_dataset()