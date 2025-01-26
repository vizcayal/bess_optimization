# tests
# chequear que los costos esten bien calculado
# chequear que no haya duplicados en los datasets

import sys
import os

sys.path.append(os.path.abspath('../sr'))
from src.bess import Bess

def test_initialization():
    '''
    check the initial values are correctly set in a bess class
    '''
    
    bess = Bess()
    assert (bess.get_power_capacity()== 100), 'capacity is not equal to the default value 100'
    assert (bess.get_efficiency() == 0.9), 'efficiency is not the default vale 0.9'
    