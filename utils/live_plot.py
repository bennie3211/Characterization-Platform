import matplotlib.pyplot as plt


class LivePlotter:

    def __init__(self, title: str, x_label: str, y_label: str, legend_name: str, marker: str = 'r-'):
        """
        Initializes a live plotter for real-time data visualization.

        Args:
            title (str): Title of the plot.
            x_label (str): Label for the x-axis.
            y_label (str): Label for the y-axis.
            legend_name (str): Name for the data series in the legend.
            marker (str): Matplotlib marker style for the plot line. Default is 'r-' (red line).
        """
        self.x_data = []
        self.y_data = []
        self.title = title

        plt.ion()  # Interactive mode on
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], marker, label=legend_name)

        self.ax.set_title(title)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.legend()
        self.ax.grid(True)

    def update(self, x: float, y: float):
        """
        Updates the plot with new x and y data points.

        Args:
            x (float): New x data point.
            y (float): New y data point.
        """
        self.x_data.append(x)
        self.y_data.append(y)

        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)

        self.ax.relim()
        self.ax.autoscale_view()

        # Short pause for UI update
        plt.pause(0.001)

    def save(self, filepath: str):
        """
        Saves the current plot to the specified file path and closes the plot.

        Args:
            filepath (str): The path where the plot image will be saved.
        """
        # Disable interaction
        plt.ioff()

        plt.savefig(filepath)
        print(f"Plot saved to: {filepath}")

    def close(self):
        """
        Closes the plot window.
        """
        plt.close(self.fig)
        print("Plot closed.")