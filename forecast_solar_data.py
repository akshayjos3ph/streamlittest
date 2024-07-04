"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script fetches the last 14 weeks of solar energy generation data
             for Germany, resamples it to weekly intervals, performs SARIMA forecasting
             for the next 14 weeks, and saves the forecasted results to a CSV file.
"""

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import warnings

# Function to read data from CSV
def read_csv(file_path: str) -> pd.DataFrame:
    """
    Reads data from a CSV file.

    :param file_path: Path to the input CSV file
    :return: DataFrame containing the data
    """
    df = pd.read_csv(file_path, parse_dates=['datetime_Europe_Brussels'])
    return df

# Function to write data to CSV
def write_to_csv(df: pd.DataFrame, output_file_path: str) -> None:
    """
    Writes data to a CSV file.

    :param df: DataFrame containing the data
    :param output_file_path: Path to the output CSV file
    """
    df.to_csv(output_file_path, index=False)

# Function to perform SARIMA forecasting
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
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")  # Ignore warnings during SARIMA fitting
        model = SARIMAX(df[forecast_column], order=(best_p, best_d, best_q),
                        seasonal_order=(best_P, best_D, best_Q, best_S))
        model_fit = model.fit(disp=False)
        forecast = model_fit.predict(start=len(df), end=len(df) + forecast_periods - 1, dynamic=False)
    return forecast

# Function to check stationarity using Augmented Dickey-Fuller test
def check_stationarity(timeseries: pd.Series) -> bool:
    """
    Checks the stationarity of the time series using Augmented Dickey-Fuller test.

    :param timeseries: Time series data
    :return: Boolean indicating whether the series is stationary
    """
    result = adfuller(timeseries.dropna())
    return result[1] <= 0.05  # p-value less than 0.05 indicates stationarity

# Function to read, resample, forecast and write data
def forecast_solar_data(input_file_path: str, output_file_path: str, forecast_column: str,
                                  best_p: int, best_d: int, best_q: int, best_P: int, best_D: int, best_Q: int, best_S: int, unit: str) -> None:
    """
    Function to read data, resample to weekly intervals, perform SARIMA forecasting for the next 14 weeks, and write results to a CSV file.

    :param input_file_path: Path to the input CSV file
    :param output_file_path: Path to the output CSV file
    :param forecast_column: Column name for the forecast data
    :param best_p: Non-seasonal AR order
    :param best_d: Non-seasonal differencing
    :param best_q: Non-seasonal MA order
    :param best_P: Seasonal AR order
    :param best_D: Seasonal differencing
    :param best_Q: Seasonal MA order
    :param best_S: Seasonal periodicity
    :param unit: Unit of the forecasted values
    """
    # Read data from CSV
    df = read_csv(input_file_path)

    # Print column names for debugging
    print("Column names:", df.columns)

    # Set datetime column as index and convert to UTC
    df['datetime_Europe_Brussels'] = pd.to_datetime(df['datetime_Europe_Brussels'], utc=True)
    df.set_index('datetime_Europe_Brussels', inplace=True)
    print("Index type:", type(df.index))

    # Resample the data to weekly intervals
    df = df.resample('W').sum()

    # Check if the time series is stationary
    if not check_stationarity(df[forecast_column]):
        print("Time series is not stationary. Differencing is required.")
        df[forecast_column] = df[forecast_column].diff().dropna()
        best_d += 1  # Increase the differencing order

    # Perform SARIMA forecasting for the next 14 weeks
    forecast_periods = 14
    forecast = sarima_forecast(df, forecast_column, best_p, best_d, best_q, best_P, best_D, best_Q, best_S, forecast_periods)

    # Convert forecast to strings with units
    forecast_with_unit = [f"{value} {unit}" for value in forecast]

    # Create a DataFrame for the forecast results
    forecast_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(weeks=1), periods=forecast_periods, freq='W')
    forecast_df = pd.DataFrame({'datetime_Europe_Brussels': forecast_dates, 'Forecast': forecast_with_unit})

    # Write forecast data to a new CSV file
    write_to_csv(forecast_df, output_file_path)
    print(f"Forecasted data has been written to {output_file_path}")

# Example usage as a function call
if __name__ == "__main__":
    input_file_path = 'DE_solar_energy_last_14_weeks.csv'  # Source CSV file
    output_file_path = 'forecasted_solar_energy.csv'  # Output CSV file
    forecast_column = 'solar_actual'  # Correct column name for solar energy values
    best_p, best_d, best_q, best_P, best_D, best_Q, best_S = (9, 1, 5, 1, 0, 1, 52)
    unit = 'MWh'  # Unit for the forecasted values

    forecast_solar_data(input_file_path, output_file_path, forecast_column, best_p, best_d, best_q, best_P, best_D, best_Q, best_S, unit)
