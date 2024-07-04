"""
Author: Akshay Joseph
Version: 1.7
Date: 2024-07-04
Description: This script fetches the last 1 month of solar energy generation data
             for Germany, resamples it to daily intervals, performs SARIMA forecasting
             for the next 14 days, and saves the forecasted results to a CSV file.
"""

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import warnings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_csv(file_path: str) -> pd.DataFrame:
    """
    Reads data from a CSV file.

    :param file_path: Path to the input CSV file
    :return: DataFrame containing the data
    """
    try:
        df = pd.read_csv(file_path, parse_dates=['datetime_Europe_Brussels'])
        return df
    except Exception as e:
        logging.error(f"Error reading the CSV file: {e}")
        raise

def write_to_csv(df: pd.DataFrame, output_file_path: str) -> None:
    """
    Writes data to a CSV file.

    :param df: DataFrame containing the data
    :param output_file_path: Path to the output CSV file
    """
    try:
        df.to_csv(output_file_path, index=False)
        logging.info(f"Forecasted data has been written to {output_file_path}")
    except Exception as e:
        logging.error(f"Error writing the CSV file: {e}")
        raise

def sarima_forecast(df: pd.DataFrame, forecast_column: str, best_p: int, best_d: int, best_q: int,
                    best_P: int, best_D: int, best_Q: int, best_S: int, forecast_periods: int) -> pd.Series:
    """
    Performs SARIMA forecasting on the given data.

    :param df: DataFrame containing the data
    :param forecast_column: Column name for the forecast data
    :param best_p: Non-seasonal AR order
    :param best_d: Non-seasonal differencing
    :param best_q: Non-seasonal MA order
    :param best_P: Seasonal AR order
    :param best_D: Seasonal differencing
    :param best_Q: Seasonal MA order
    :param best_S: Seasonal periodicity
    :param forecast_periods: Number of periods to forecast
    :return: Series containing the forecasted values
    """
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")  # Ignore warnings during SARIMA fitting
            model = SARIMAX(df[forecast_column], order=(best_p, best_d, best_q),
                            seasonal_order=(best_P, best_D, best_Q, best_S))
            model_fit = model.fit(disp=False)
            forecast = model_fit.predict(start=len(df), end=len(df) + forecast_periods - 1, dynamic=False)
        return forecast
    except Exception as e:
        logging.error(f"Error during SARIMA forecasting: {e}")
        raise

def check_stationarity(timeseries: pd.Series) -> bool:
    """
    Checks the stationarity of the time series using Augmented Dickey-Fuller test.

    :param timeseries: Time series data
    :return: Boolean indicating whether the series is stationary
    """
    result = adfuller(timeseries.dropna())
    return result[1] <= 0.05  # p-value less than 0.05 indicates stationarity

def forecast_solar_data(input_file_path: str, output_file_path: str, forecast_column: str, unit: str) -> None:
    """
    Function to read data, resample to daily intervals, perform SARIMA forecasting for the next 14 days, and write results to a CSV file.

    :param input_file_path: Path to the input CSV file
    :param output_file_path: Path to the output CSV file
    :param forecast_column: Column name for the forecast data
    :param unit: Unit of the forecasted values
    """
    # Read data from CSV
    df = read_csv(input_file_path)
    logging.info(f"Column names: {df.columns}")

    # Set datetime column as index and convert to UTC
    df['datetime_Europe_Brussels'] = pd.to_datetime(df['datetime_Europe_Brussels'], utc=True)
    df.set_index('datetime_Europe_Brussels', inplace=True)
    logging.info(f"Index type: {type(df.index)}")

    # Filter the last 1 month of data
    one_month_ago = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=1)
    df = df[df.index >= one_month_ago]

    # Resample the data to daily intervals
    df = df.resample('D').sum()

    # Check if the time series is stationary
    if not check_stationarity(df[forecast_column]):
        logging.info("Time series is not stationary. Differencing is required.")
        df[forecast_column] = df[forecast_column].diff().dropna()

    # Perform SARIMA forecasting for the next 14 days
    forecast_periods = 14
    best_p, best_d, best_q, best_P, best_D, best_Q, best_S = (4, 1, 7, 1, 0, 1, 52)
    forecast = sarima_forecast(df, forecast_column, best_p, best_d, best_q, best_P, best_D, best_Q, best_S, forecast_periods)

    # Replace negative forecast values with the previous day's value
    for i in range(1, len(forecast)):
        if forecast[i] < 0:
            forecast[i] = forecast[i - 1]

    # Create a DataFrame for the forecast results
    forecast_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_periods, freq='D')
    forecast_df = pd.DataFrame({'datetime_Europe_Brussels': forecast_dates, 'Forecast': forecast})

    # Write forecast data to a new CSV file
    forecast_df.columns = ['datetime_Europe_Brussels', f'Forecast ({unit})']
    write_to_csv(forecast_df, output_file_path)

if __name__ == "__main__":
    input_file_path = 'DE_solar_energy_last_1_month.csv'  # Source CSV file
    output_file_path = 'forecasted_solar_energy.csv'  # Output CSV file
    forecast_column = 'solar_actual_MWh'  # Correct column name for solar energy values
    unit = 'MWh'  # Unit for the forecasted values

    try:
        forecast_solar_data(input_file_path, output_file_path, forecast_column, unit)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
