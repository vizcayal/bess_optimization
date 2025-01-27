import matplotlib.pyplot as plt
import pandas as pd

class Visualizer:
    def __init__(self, case):
        """
        Initialize the Visualizer with the dataset.
        
        :param case: identifier used to locate the the CSV file containing the dataset, and naming the output.
        """
        self.case = case
        self.data = pd.read_csv(f'output/results-{self.case}.csv')
        self.data.rename(columns={'Unnamed: 0': 'timestamp'}, inplace=True)
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])

    def plot(self):
        """
        Generate separate reports for gen_hour, charge_hour, and state_of_charge over time in pdf.
        """
        # Plot gen_hour
        plt.figure(figsize=(10, 4))
        plt.plot(self.data['timestamp'], self.data['gen_hour'], label='Generation Hour', linestyle='-', marker='o', alpha=0.5)
        plt.title('Generation Hour Over Time', fontsize=14)
        plt.xlabel('Timestamp', fontsize=12)
        plt.ylabel('Generation Hour', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'output/hourly_gen-{self.case}.pdf')
        plt.show()

        # Plot charge_hour
        plt.figure(figsize=(10, 4))
        plt.plot(self.data['timestamp'], self.data['charge_hour'], label='Charge Hour', linestyle='--', marker='x', alpha=0.5)
        plt.title('Charge Hour Over Time', fontsize=14)
        plt.xlabel('Timestamp', fontsize=12)
        plt.ylabel('Charge Hour', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'output/hourly_charge-{self.case}.pdf')
        plt.show()

        # Plot state_of_charge
        plt.figure(figsize=(10, 4))
        plt.plot(self.data['timestamp'], self.data['state_of_charge'], label='State of Charge', linestyle='-.', marker='s', alpha=0.5)
        plt.title('State of Charge Over Time', fontsize=14)
        plt.xlabel('Timestamp', fontsize=12)
        plt.ylabel('State of Charge', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'output/state_of_charge-{self.case}.pdf')
        plt.show()