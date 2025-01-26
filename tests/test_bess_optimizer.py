import sys
import os

sys.path.append(os.path.abspath('../sr'))
from src.bess_optimizer import Bess_Optimizer
from src.bess import Bess


def test_price_data():
    '''
    check energy prices have data
    '''
    optimizer_test = Bess_Optimizer()
    optimizer_test.load_prices('data/energy_prices.csv')
    assert len(optimizer_test.energy_price)>0, 'no data for fuel prices'


def test_reg_data():
    '''
    check regulation has data
    '''
    optimizer_test = Bess_Optimizer()
    optimizer_test.load_regulation('data/regulation_prices.csv')
    assert len(optimizer_test.reg_prices)>0, 'no data for regulation prices'


def test_generation_not_exceed_capacity():
    '''
    check that hourly generation not exceed the bess power capacity
    '''
    bess_1 = Bess()
    optimizer = Bess_Optimizer(case = 'case1')
    optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
    optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
    optimizer.optimize_period(bess_1, start_day = '1/1/2023', end_day = '2/1/2023', initial_charge = 0)
    optimizer.get_optimal_schedule()
    assert (optimizer.schedule_ds['gen_hour'] <= bess_1.power_capacity).all(), 'generation is greater than capacity'


def test_generation_not_exceed_charge():
    '''
    check that hourly generation the bess charge available
    '''
    bess_1 = Bess()
    optimizer = Bess_Optimizer(case = 'case1')
    optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
    optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
    optimizer.optimize_period(bess_1, start_day = '1/1/2023', end_day = '2/1/2023', initial_charge = 0)
    optimizer.get_optimal_schedule()
    assert (optimizer.schedule_ds['gen_hour'] <= optimizer.schedule_ds['state_of_charge']).all(), 'generation is greater than capacity'


def test_reg_up_not_exceed_capacity():
    '''
    check that hourly generation not exceed the bess power capacity
    '''
    bess_1 = Bess()
    optimizer = Bess_Optimizer(case = 'case1')
    optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
    optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
    optimizer.optimize_period(bess_1, start_day = '1/1/2023', end_day = '2/1/2023', initial_charge = 0)
    optimizer.get_optimal_schedule()
    assert (optimizer.schedule_ds['reg_up_hour'] <= bess_1.power_capacity).all(), 'generation is greater than capacity'

def test_reg_down_not_exceed_capacity():
    '''
    check that hourly generation not exceed the bess power capacity
    '''
    bess_1 = Bess()
    optimizer = Bess_Optimizer(case = 'case1')
    optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
    optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
    optimizer.optimize_period(bess_1, start_day = '1/1/2023', end_day = '2/1/2023', initial_charge = 0)
    optimizer.get_optimal_schedule()
    assert (optimizer.schedule_ds['reg_up_hour'] <= bess_1.power_capacity).all(), 'generation is greater than capacity'