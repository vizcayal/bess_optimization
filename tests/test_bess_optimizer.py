# tests
# chequear que el state of charge is correctly calculated
# chequear que la generacion no excede el SoC
# chequear que los costos esten bien calculado

import sys
import os

sys.path.append(os.path.abspath('../sr'))
#sys.path.append(os.path.abspath('../data'))
from src.bess_optimizer import Bess_Optimizer

def test_price_data():
    optimizer_test = Bess_Optimizer()
    optimizer_test.load_prices('data/energy_prices.csv')
    assert len(optimizer_test.energy_price)>0, 'no data for fuel prices'

def test_reg_up_data():
    optimizer_test = Bess_Optimizer()
    optimizer_test.load_regulation('data/regulation_prices.csv')
    assert len(optimizer_test.reg_prices)>0, 'no data for regulation prices'

def test_generation_lower_than_capacity():
    optimizer = Bess_Optimizer(case = 'case1', power_capacity = 100, energy_capacity = 200, efficiency = 0.9)
    optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
    optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
    optimizer.optimize_period(start_day = '1/1/2023', end_day = '2/1/2023', initial_charge = 0)
    optimizer.get_output_dataset()
    assert (optimizer.output_ds['gen_hour'] <= optimizer.power_capacity).all(), 'generation greater than capacity'
    
