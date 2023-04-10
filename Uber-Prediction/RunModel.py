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
        self.layout.addWidget(self.date_edit, 0, 1)

        # Create a QLabel to display the prompt for distance
        distance_label = QLabel('Enter the Distance in Miles:')
        self.layout.addWidget(distance_label, 0, 2)

        # Create a QLineEdit widget for distance input
        self.distance_edit = QLineEdit()
        self.layout.addWidget(self.distance_edit, 0, 3)

        # Create a QLabel to display the prompt for passengers
        distance_label = QLabel('Enter the # of Passengers:')
        self.layout.addWidget(distance_label, 1, 2)

        # Create a QLineEdit widget for passengers input
        self.passenger_edit = QLineEdit()
        self.layout.addWidget(self.passenger_edit, 1, 3)

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

        # Set the layout for the CarDashboard widget
        self.setLayout(self.layout)

    def handle_fare(self):
        distance = float(self.distance_edit.text())
        passengers = float(self.passenger_edit.text())
        est_tz = pytz.timezone('US/Eastern')

        # Get the current date and time in EST
        now = datetime.datetime.now(est_tz)

        # Extract the hour, day, day of week, and month from the datetime object
        hour = now.hour
        day = now.day
        day_of_week = now.weekday() #should this be 0 or 1???? need to check
        month = now.month
        print(predict_fare_amount(passengers, hour, day_of_week, month, distance))


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
        
        heatmap = RideHeatmap(year,month,day).plot_matrix()
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
