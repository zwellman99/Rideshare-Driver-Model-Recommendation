import sys

# Add path of the base environment to sys.path
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages')


import xgboost as xgb
import pandas as pd
from datetime import datetime, timedelta
from xgboost import XGBRegressor


def predict_fare_amount(passenger_count, hour, day_of_week, month, distance):
    # Load the trained model from disk
    fare_model = xgb.Booster()
    fare_model.load_model('fare_model.bin')

    # Prepare the input data as a Pandas DataFrame
    data = {'passenger_count': [passenger_count],
            'hour': [hour],
            'day_of_week': [day_of_week],
            'month': [month],
            'distance': [distance]}
    df = pd.DataFrame(data)

    # Use the trained model to make a prediction
    prediction = fare_model.predict(xgb.DMatrix(df))[0]

    # Return the predicted fare amount
    return prediction


def predict_ride_count(hour_group, day_of_week, month, day):
    demand_model = xgb.XGBRegressor()
    demand_model.load_model('demand_model.bin')

    # Create a dataframe with the input values
    input_df = pd.DataFrame({
        'HourGroup': [hour_group],
        'DayOfWeek': [day_of_week],
        'Month': [month],
        'Day': [day]
    })

    """"# Convert input_df to xgb.DMatrix
    input_dmatrix = xgb.DMatrix(input_df)

    # Use the XGBoost model to make a prediction
    prediction = demand_model.predict(input_dmatrix)[0]
    """
    prediction = demand_model.predict(input_df)[0]

    return prediction


import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class RideHeatmap:
    def __init__(self, year, month, day):
        self.week_dates = self.create_week_list(year, month, day)
        self.ride_matrix = self.create_matrix(self.week_dates)

    def create_week_list(self, year, month, day):
        input_date = datetime(year, month, day)

        # Find the Sunday of the given week
        days_to_subtract = (input_date.weekday() + 1) % 7  # Sunday is 0, Saturday is 6
        sunday = input_date - timedelta(days=days_to_subtract)

        # Create a list of dates from Sunday through Saturday
        week_dates = [sunday + timedelta(days=i) for i in range(7)]

        # Format the dates as strings with the desired format
        week_info = [date.strftime("%d-%m-%Y") for date in week_dates]
        return week_info

    def create_matrix(self, week_dates):
        days = [int(date[:2]) for date in week_dates]
        months = [int(date[3:5]) for date in week_dates]

        ride_matrix = []

        for i in range(6):
            row = []
            for j in range(7):
                month = months[i]
                num_rides = predict_ride_count(i, j, months[j], days[j])  # Make sure this function is defined
                row.append(num_rides)
            ride_matrix.append(row)

        percentile_matrix = np.array(ride_matrix)
        percentile_matrix = percentile_matrix / np.amax(percentile_matrix)

        return percentile_matrix

    def plot_matrix(self):
        hourgroups = ['0-3', '4-7', '8-11', '12-15', '16-19', '20-23']

        data = self.ride_matrix

        # Convert data to a numpy array
        data = np.array(data)

        # Create a color map
        cmap = plt.cm.get_cmap('coolwarm')

        # Create a figure and axis object
        fig, ax = plt.subplots()

        # Plot the heatmap with color map
        im = ax.imshow(data, cmap=cmap)

        # Add a color bar
        cbar = ax.figure.colorbar(im, ax=ax)

        # Set the tick labels
        ax.set_xticks(np.arange(len(self.week_dates)))
        ax.set_yticks(np.arange(len(hourgroups)))
        ax.set_xticklabels(self.week_dates)
        ax.set_yticklabels(hourgroups)

        # Rotate the tick labels and set their alignment
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Loop over the data and add annotations to the heatmap
        for i in range(len(hourgroups)):
            for j in range(len(self.week_dates)):
                text = ax.text(j, i, "{:.1f}".format(data[i, j]),
                               ha="center", va="center", color="black")

            # Set the title
        ax.set_title("Ride Count Heatmap")

        # Show the plot
        return(fig)

#RideHeatmap(2019,1,1).plot_matrix()
