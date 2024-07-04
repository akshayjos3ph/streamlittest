"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script fetches the last 14 weeks of solar energy generation data
             for Germany, resamples it to hourly intervals, and saves the result
             to a CSV file.
"""

from entsoe import EntsoePandasClient
import pandas as pd

def fetch_and_save_solar_data(api_key, filename='DE_solar_energy_last_14_weeks.csv'):
    """
    Fetch the last 14 weeks of solar energy generation data for Germany,
    resample to hourly intervals, and save to a CSV file.

    Args:
    api_key (str): The API key for accessing ENTSO-E data.
    filename (str): The name of the CSV file to save the data.
    """
    client = EntsoePandasClient(api_key=api_key)

    end = pd.Timestamp.now(tz='Europe/Brussels')
    start = end - pd.Timedelta(weeks=14)
    country_code = 'DE'

    df = client.query_generation(country_code, start=start, end=end, psr_type='B16')
    df_1hour = df.resample('1h').sum().reset_index()

    if len(df_1hour.columns) > 2:
        df_1hour = df_1hour.drop(df_1hour.columns[2], axis=1)

    df_1hour.columns = ['datetime_Europe_Brussels', 'solar_actual_MWh']
    df_1hour.to_csv(filename, index=False)

    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Example usage
    api_key = 'xxxxxxxx'  # Replace with your actual API key
    fetch_and_save_solar_data(api_key)

