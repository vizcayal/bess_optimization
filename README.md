# Battery Energy Storage System (BESS) Schedule Optimization

## Schedule Optimizer that determines the hourly amount to charge and discharge
## for a BESS in an electricity Market for maximizing profits.


## Assumptions

1. Efficiency is 90% for charging and 90% for discharging.
2. Whenever the market accepts the regulation offer, 10% of the regulation is deployed in energy. 
The market pays for total energy deployed (schedule generation + regulation generated)
3. When the Bess is charging, it is can offer regulation services to the market depending on 
the energy stored in Bess
4. Bess can offer regulation up and down at one hour, and can be dispatched for both directions.
5. Central time zone assumed.


## Decision Variables

- charge[t]: hour energy charged by the Bess at hour t.
- gen[t]: hour energy generated to the system by the Bess (discharged) at hour t.
- acc_charge: state of charge, cumulative charge of the Bess at the beginning of hour t.
- reg_up: regulation up of the Bess at hour t.
- reg_down: regulation down of the Bess at hour t.


## Parameters

- energy price[t]: market price of energy for hour t (buy or sell price).
- reg_up_price[t]: market price of regulation up for hour t.
- reg_down_price[t]: market price of regulation.
- eff: efficiency of Bess.
- power_capacity: power capacity of the Bess.
- energy_capacity: energy capacity of Bess.


## Objective Function

Max[ Sum( energy_price[i] * (gen[i] - charge[i]) + reg_up_price(i) * reg_up[i] + reg_down_price[i] * reg_down[i] +
0.1 * energy_price[i] * (reg_down[i] + reg_up[i]) ) ]


## Constraints

1. Regulation, generation, charging are all greater or equal to zero
- reg_up[t] >= 0
- reg_down[t] >= 0
- gen[t] >= 0
- charge[t] >= 0
- acc_charge >= 0

2. Hour generation, charge, regulation up and down cannot exceed power capacity
- gen[t] + reg_up[t] <= power_capacity	
- reg_up[t] <= power_capacity	
- reg_down[t] <= power_capacity	
- charge[t] <= power_capacity	

3. Generation plus regulation up cannot surpass the power capacity
- gen[t] + reg_up[t] <= power_capacity	
	
4. Generation plus regulation up cannot surpass the charge of the Bess
- gen[t] + reg_up[t] <= 0.9 * energy_capacity

5. Charging rate plus regulation down cannot exceed the remaining capacity of charge
- charge[t] + reg_down[t] <= (1/0.9) * energy_capacity - acc_charge[t] 

6. Only one charging cycle by day.
- Sum(gen[t]) <= energy_capacity, for t from 0 to 23 hour for each day
- Sum(charge[t]) <= energy_capacity, for t from 0 to 23 hour for each day

7. State of charge of the Bess of the next hour is the State of charge of the current hour plus the energy charge from the system hour, minus the energy generated that hour plus the energy deployed by regulation, considering the effect of efficiency for every operation.
- acc_charge[t + 1] = acc_charge[t] + eff * charge[t] - (1/eff) * gen[t] + 0.1 * eff* reg_down[t] - 0.1 * (1/eff) * reg_up[t]  


## Approach
The optimization is set up as Linear Programming (LP) problem, solved by using Pulp library


## How to install bess optimizer

1. Unzip the bess_optimizer.zip file
2. In the root folder install the virtual env 'pip install -r requirements.txt'
3. Activate the virtual env by executing 'bess_env/scripts/activate'


## Structure of the project

root/
├── src/                                    # source folder
│   ├── __init__.py                         
│   ├── bess.py                             # bess class
│   ├── bess_optimizer.py                   # bess optimizer class
│   └── visualizer.py                       # visualizer class
├── tests/
│   ├── __init__.py     
│   ├── test_bess.py                        # tests for bess class
│   ├── test_bess_optimizer.py              # tests for bess_optimizer class
│   └── ...
├── data/
│   ├── energy_prices.csv                   # hourly energy prices file
│   └── regulation_prices.csv               # hourly regulation prices file
├── utils/
│   └── utils.py                            # utils functions
├── output/
│   └── results-case_0.csv                  # example results for the default case
├── optimizer.py                            # main file
├── requirements.txt                        # required libraries for the virtual environment
└── README.md           

## How to execute

1. Execute 'python optimizer.py' for default parameters optimization
2. The following optional parameters can be included:
    case: name of the case to be run
    power_capacity: power capacity of the bess to be optimized
    energy_capacity: energy capacity of charge of the bess
    start_date / end_date: start date for the optimization (MM/DD/YYYY)
    
    e.g 'python optimizer.py --case test1 --power_capacity 50 --energy_capacity 150 --start_date 03/01/2023 --end_date 04/01/2023'

## Output

1. Files in the output folder have the hourly optimization results for Bess Generation, Charge, regulation up/downs and state 
of charge.
3. After running the main script optimizer.py, the with information about the Total profit and total cycles will be printed
in the screen

e.g
SUMMARY SCHEDULE OPERATION:
Total Profit: 1271703.2
Total Cycles: 25.1

## How to test

1. For performing tests in the tests folder, execute the command: 'python -m pytest'

