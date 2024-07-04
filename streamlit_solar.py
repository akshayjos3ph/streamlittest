"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script creates a Streamlit dashboard to fetch and forecast solar energy generation data for the next 14 days.
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from fetch_solar_data import fetch_solar_data  # Import the function

# Load data
@st.cache
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['datetime_Europe_Brussels'] = pd.to_datetime(data['datetime_Europe_Brussels'])
    return data

# Get API key from secrets
api_key = st.secrets["api_key"]

# Fetch last month's data and note the fetch date
fetch_date = datetime.now()
filename = fetch_solar_data(api_key)  # Call the function

# Display last fetch date
st.write(f"### Last data fetch date: {fetch_date.strftime('%Y-%m-%d %H:%M:%S')}")

# File path for forecast data
forecast_file_path = 'forecasted_solar_energy.csv'

# Load forecast data
forecast_data = load_data(forecast_file_path)

# Title and description
st.title('14-Day Solar Energy Forecast')
st.write('This dashboard shows the forecast of solar energy for the next 14 days in MWh.')

# Plotting
chart = alt.Chart(forecast_data).mark_bar().encode(
    x='datetime_Europe_Brussels:T',
    y='Forecast (MWh):Q',
    tooltip=['datetime_Europe_Brussels', 'Forecast (MWh)']
).properties(
    title='14-Day Solar Energy Forecast'
)

st.altair_chart(chart, use_container_width=True)
