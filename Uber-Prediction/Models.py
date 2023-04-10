import xgboost as xgb
import pandas as pd


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
    demand_model = xgb.Booster()
    demand_model.load_model('fare_model.bin')

    # Create a dataframe with the input values
    input_df = pd.DataFrame({
        'HourGroup': [hour_group],
        'DayOfWeek': [day_of_week],
        'Month': [month],
        'Day': [day]
    })

    # Use the XGBoost model to make a prediction
    prediction = demand_model.predict(input_df)[0]

    return prediction
