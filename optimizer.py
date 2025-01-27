from src.bess import Bess
from src.bess_optimizer import Bess_Optimizer
from src.visualizer import Visualizer
import argparse

def main():
    """
    main function for the Bess optimizer
    """

    parser = argparse.ArgumentParser()

    # Define Arguments
    parser.add_argument("--case", type=str, required=False, help="name of the case", default= "case_0")
    parser.add_argument("--power_capacity", type = float, required = False, help="Bess power capacity", default= 100)
    parser.add_argument("--energy_capacity", type = float, required = False, help="Bess power capacity", default= 200)
    parser.add_argument("--start_date", type = str, required = False, help="optimization start date", default ='03-01-2023')
    parser.add_argument("--end_date", type = str, required = False, help="Optimization end date", default ='04-01-2023')
    args = parser.parse_args()

    # create a Bess instance
    bess_texas = Bess(power_capacity = args.power_capacity, energy_capacity = args.energy_capacity)
    # create a Bess Optimizer instance
    optimizer = Bess_Optimizer(case = args.case)
    # load energy prices
    optimizer.load_prices(energy_price_file ='data/energy_prices.csv')
    # load regulation prices
    optimizer.load_regulation(regulation_price_file = 'data/regulation_prices.csv')
    # optimize the period
    optimizer.optimize_period(bess_texas, start_day = args.start_date, end_day = args.end_date, initial_charge = 0)
    # write hourly report
    optimizer.save_hourly_report()
    # set the optimal schedule on bess
    bess_texas.set_schedule(optimizer.get_optimal_schedule())
    # set the profit to the bess
    bess_texas.set_profit(optimizer.get_profit())
    # print the total profit and number of cycles
    bess_texas.print_report()

    visualizer = Visualizer(args.case)
    visualizer.plot()


if __name__ == "__main__":
    main()