import xgboost as xgb
import pandas as pd
from Models import predict_fare_amount, predict_ride_count

"""
Predict_Fare_Amount
*passenger_count: #
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

import sys
from PyQt6.QtWidgets import *
import json
import os


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


class CarInfo(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Car Info')
        self.setGeometry(100, 100, 500, 400)

        # create buttons
        self.enter_button = QPushButton('Enter Car Info')
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
        print('Going to dashboard...')




app = QApplication(sys.argv)
car_info = CarInfo()
sys.exit(app.exec())
