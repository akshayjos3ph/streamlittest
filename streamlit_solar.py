import streamlit as st
import opendatasets as od
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA

# Streamlit app title
st.title('Solar Generation Forecasting in Germany')

# Function to load data
@st.cache_data
def load_data():
    opsd_url = 'https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv'
    od.download(opsd_url)
    data_path = './time_series_60min_singleindex.csv'
    df = pd.read_csv(data_path, parse_dates=['utc_timestamp'], index_col='utc_timestamp')
    return df

# Button to update data
if st.button('Update Data'):
    # Clear the cache to force reloading the data
    st.cache_data.clear()

# Load the dataset
df = load_data()

# Filtering the dataset for solar generation data in Germany
solar_data = df.filter(regex='DE_solar_generation_actual')
# Resampling data to daily frequency for ARIMA modeling
daily_solar = solar_data.resample('D').sum()

# Adding a year filter
unique_years = daily_solar.index.year.unique()
years = st.multiselect('Select years', options=unique_years, default=list(unique_years))

# Filter the data based on selected years
daily_solar_filtered = daily_solar[daily_solar.index.year.isin(years)]

# Plotting the data
st.subheader('Daily Solar Generation Actual')
st.line_chart(daily_solar_filtered)

# Checking stationarity
result = adfuller(daily_solar_filtered.dropna())
st.write('ADF Statistic: %f' % result[0])
st.write('p-value: %f' % result[1])

# If data is not stationary, differencing the data
if result[1] > 0.05:
    daily_solar_diff = daily_solar_filtered.diff().dropna()
else:
    daily_solar_diff = daily_solar_filtered

# ACF and PACF plots
st.subheader('ACF and PACF plots')
fig, axes = plt.subplots(1, 2, figsize=(15, 4))
plot_acf(daily_solar_diff.dropna(), ax=axes[0])
plot_pacf(daily_solar_diff.dropna(), ax=axes[1])
st.pyplot(fig)

# Fitting the ARIMA model
model = ARIMA(daily_solar_diff, order=(1, 1, 1))
results = model.fit()
st.write(results.summary())

# Forecasting
forecast = results.get_prediction(start=1, end=len(daily_solar_diff) + 30)
forecast_df = forecast.summary_frame()

# Plotting the results
st.subheader('Forecasting Results')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(daily_solar_diff, label='Observed')
ax.plot(forecast_df['mean'], label='Forecast')
ax.fill_between(forecast_df.index, forecast_df['mean_ci_lower'], forecast_df['mean_ci_upper'], color='k', alpha=0.2)
ax.legend()
st.pyplot(fig)
