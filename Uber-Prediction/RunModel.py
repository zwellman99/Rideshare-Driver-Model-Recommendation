import sys

# Add path of the base environment to sys.path
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages')

import pandas as pd
from Models import predict_fare_amount, predict_ride_count
from Models import RideHeatmap
import matplotlib.pyplot as plt
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtCharts import *
from PyQt6.QtGui import *
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import json
import os
import pytz
import datetime
import numpy as np

"""
Predict_Fare_Amount
*passenger_count: #$ccd
*hour: 0-23
*day_of_week: 0-6
*month: 1-12
*distance: 0-X

Predict_Ride_Count
*hour_group: 0-6
*day_of_week: 0-6
*month: 1-12
*day: 1-30
"""




class CarInfoWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enter Car Info')
        self.setGeometry(100, 100, 500, 400)

        if os.path.exists('car_info.json'):
            with open('car_info.json', 'r') as f:
                data = json.load(f)
            car_data = [str(value) for value in data.values()]
        else:
            car_data = ["","","",""]
        # create labels and input fields
        year_label = QLabel('Enter your car\'s year (ex. 2011):')
        self.year_input = QLineEdit(car_data[0])

        mpg_label = QLabel('Enter your car\'s mpg (ex. 25.0):')
        self.mpg_input = QLineEdit(car_data[1])

        mileage_label = QLabel('Enter your car\'s est. mileage (ex. 65000):')
        self.mileage_input = QLineEdit(car_data[2])

        value_label = QLabel('Enter your car\'s est. value (ex. 15000):')
        self.value_input = QLineEdit(car_data[3])

        # create layout for labels and input fields
        form_layout = QVBoxLayout()
        form_layout.addWidget(year_label)
        form_layout.addWidget(self.year_input)
        form_layout.addWidget(mpg_label)
        form_layout.addWidget(self.mpg_input)
        form_layout.addWidget(mileage_label)
        form_layout.addWidget(self.mileage_input)
        form_layout.addWidget(value_label)
        form_layout.addWidget(self.value_input)

        # create button to submit input
        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.submit_car_info)

        # create main layout
        main_layout = QVBoxLayout()

        # create text box to display car info from json file
        if os.path.exists('cars.json'):
            with open('cars.json', 'r') as f:
                car_data = json.load(f)
            car_info_text = QTextEdit()
            car_info_text.setPlainText(json.dumps(car_data, indent=4))
            main_layout.addWidget(car_info_text)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(submit_button)

        # set main layout
        self.setLayout(main_layout)

    def submit_car_info(self):
        year = self.year_input.text()
        mpg = self.mpg_input.text()
        mileage = self.mileage_input.text()
        value = self.value_input.text()

        try:
            year = int(year)
            mpg = float(mpg)
            mileage = int(mileage)
            value = float(value)
            print(f'Car Info: year={year}, mpg={mpg}, mileage={mileage}, value={value}')
            data = {'year': year, 'mpg': mpg, 'mileage': mileage, 'value': value}
            with open('car_info.json', 'w') as f:
                json.dump(data, f)

            self.close()
        except ValueError:
            # reset input fields
            self.year_input.clear()
            self.mpg_input.clear()
            self.mileage_input.clear()
            self.value_input.clear()

            # display error message
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Icon.Warning)
            error_msg.setText('Invalid input. Please enter a valid number.')
            error_msg.setWindowTitle('Error')
            error_msg.exec()


class CarDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enter Car Info')
        self.setGeometry(100, 100, 700, 400)

        # Create a QGridLayout to hold the widgets
        self.layout = QGridLayout()

        # Create a QLabel to display the prompt
        prompt_label = QLabel('Select the Date for Weekly Demand Projections:')
        self.layout.addWidget(prompt_label, 0, 0)

        # Create a QDateEdit widget for date selection
        self.date_edit = QDateEdit()

        # Set an initial date for the date edit widget
        self.date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(self.date_edit, 0, 1, 1, 1)

        # Create a QLabel to display the prompt for distance
        distance_label = QLabel('Enter the Distance in Miles:')
        self.layout.addWidget(distance_label, 0, 2, 1, 1)

        # Create a QLineEdit widget for distance input
        self.distance_edit = QLineEdit()
        self.layout.addWidget(self.distance_edit, 0, 3, 1, 1)

        # Create a QLabel to display the prompt for passengers
        distance_label = QLabel('Enter the # of Passengers:')
        self.layout.addWidget(distance_label, 1, 2, 1, 1)

        # Create a QLineEdit widget for passengers input
        self.passenger_edit = QLineEdit()
        self.layout.addWidget(self.passenger_edit, 1, 3, 1, 1)

        # Create a QPushButton widget for submission
        submit_date = QPushButton('Submit date')

        # Connect the clicked signal of the submit button to a slot function
        submit_date.clicked.connect(self.handle_demand)

        # Add the submit button to the layout
        self.layout.addWidget(submit_date, 2, 0, 1, 2)

        # Create a QPushButton widget for submission
        submit_distance = QPushButton('Submit distance')

        # Connect the clicked signal of the submit button to a slot function
        submit_distance.clicked.connect(self.handle_fare)

        # Add the submit button to the layout
        self.layout.addWidget(submit_distance, 2, 2, 1, 2)

        self.fare_label = QLabel("Enter info above to calculate fare")
        self.layout.addWidget(self.fare_label, 3, 2, 1, 2)

                # Create a QLabel to display the top 5 indices
        self.top_5_label = QLabel('Top 5 driving times will be displayed here... ')
        font = QFont()
        font.setBold(True)
        self.top_5_label.setFont(font)
        self.layout.addWidget(self.top_5_label, 3, 0, 1,1)

        # Set the layout for the CarDashboard widget
        self.setLayout(self.layout)

    def handle_fare(self):
        distance = float(self.distance_edit.text())
        passengers = float(self.passenger_edit.text())
        est_tz = pytz.timezone('US/Eastern')
        current_datetime = QDateTime.currentDateTime()

        # Get the current date and time in EST
        now = datetime.datetime.now(est_tz)

        # Extract the hour, day, day of week, and month from the datetime object
        year = now.year
        hour = now.hour
        day = now.day
        day_of_week = current_datetime.date().dayOfWeek()%7
        month = now.month
        fare = predict_fare_amount(passengers, hour, day_of_week, month, distance)

        week_dates = RideHeatmap(year, month, day).create_week_list(year, month, day)
        matrix = RideHeatmap(year, month, day).create_matrix(week_dates)

        #get the value in matrix corresponding to the current weekday and hour
        current_value = matrix[hour//4][day_of_week]
        print(current_value)
        self.fare_label.setText(f'Estimated fare amount: ${fare:.2f}')
        
        


    # Slot function to handle submission of the date
    def handle_demand(self):
        # Get the selected date from the date edit widget
        selected_date = self.date_edit.date()

        # Get the day, month, and year from the selected date
        day = selected_date.day()
        month = selected_date.month()
        year = selected_date.year()

        # Print the selected date to the console
        print(f'Selected Date: {day}/{month}/{year}')

        # Get the matrix for the week
        week_dates = RideHeatmap(year, month, day).create_week_list(year, month, day)
        hourgroups = ['12:00-3:59am', '4:00-7:59am', '8:00-11:59am', '12:00-3:59pm', '4:00-7:59pm', '8:00-11:59pm']
        day_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

# Create the ride matrix for the week
        matrix = RideHeatmap(year, month, day).create_matrix(week_dates)

        print(matrix)

        # Get the indices of the top 5 values in the matrix
        top_5_indices = np.argpartition(matrix.flatten(), -5)[-5:]
        top_5_values = [matrix.flatten()[i] for i in top_5_indices]

        # Create a dictionary with values as keys and indices as values
        value_index_dict = dict(zip(top_5_values, top_5_indices))

        # Sort the dictionary by keys in descending order
        sorted_dict = dict(sorted(value_index_dict.items(), key=lambda item: item[0], reverse=True))

        top_5_indices = [value_index_dict[value] for value in sorted_dict.keys()]
        top_5_values = list(sorted_dict.keys())[:5]

        # Set the text of the top_5_indices_label to display the results of the top 5 indices
        self.top_5_label.setText('\n'.join([f'{week_dates[i%7]}, {day_of_week[i%7]} between {hourgroups[i//7]}' for i in top_5_indices]))

        heatmap = RideHeatmap(year, month, day).plot_matrix()
        heatmap.show()

class CarInfo(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Car Info')
        self.setGeometry(100, 100, 500, 400)

        # create buttons
        self.enter_button = QPushButton('Update Car Info')
        self.dashboard_button = QPushButton('Go to Dashboard')

        # create layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.enter_button)
        button_layout.addWidget(self.dashboard_button)

        # create main layout
        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)

        # set main layout
        self.setLayout(main_layout)

        # connect button signals to slots
        self.enter_button.clicked.connect(self.enter_car_info)
        self.dashboard_button.clicked.connect(self.go_to_dashboard)

        self.show()

    def enter_car_info(self):
        self.car_info_window = CarInfoWindow()
        self.car_info_window.show()

    def go_to_dashboard(self):
        self.dashboard_window = CarDashboard()
        self.dashboard_window.show()




app = QApplication(sys.argv)
car_info = CarInfo()
sys.exit(app.exec())
