import os
import csv
from datetime import datetime


class ExperimentLogger:

    def __init__(self, routine_name: str):
        """
        Initializes the ExperimentLogger with a routine name.

        Args:
            routine_name (str): Name of the experiment routine.
        """
        # Set up naming convention
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_name = f"{timestamp}_{routine_name}"

        # Create base directory for logs
        self.base_dir = os.path.join("logs", folder_name)

        # Ensure directory exists
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        # Set file paths
        self.csv_path = os.path.join(self.base_dir, "data.csv")
        self.plot_path = os.path.join(self.base_dir, "plot.png")
        self.file_handle = None
        self.writer = None

    def init_csv(self, headers: list):
        """
        Initializes the CSV file with the given headers.

        Args:
            headers (list): List of column headers for the CSV file.
        """
        self.file_handle = open(self.csv_path, 'w', newline='')
        self.writer = csv.writer(self.file_handle)
        self.writer.writerow(headers)
        return self.csv_path

    def log_data(self, row_data: list):
        """
        Logs a row of data to the CSV file.

        Args:
            row_data (list): List of data values corresponding to the CSV columns.
        """
        if self.writer:
            self.writer.writerow(row_data)

    def close(self):
        """
        Closes the CSV file handle.
        """
        if self.file_handle:
            self.file_handle.close()
            print(f"CSV saved to: {self.csv_path}")

    def get_plot_path(self):
        """
        Returns the file path for saving plots.
        """
        return self.plot_path