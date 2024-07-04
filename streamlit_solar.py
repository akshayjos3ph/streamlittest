import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
import os

# Streamlit app title
st.title('Solar Generation in Germany: SARIMA Forecast')

# Display the SARIMA model parameters
st.subheader('SARIMA Model Parameters')

# Given SARIMA diagnostics parameters
p, d, q = 9, 1, 5
P, D, Q, s = 2, 1, 2, 52

sarima_order = (p, d, q)
sarima_seasonal_order = (P, D, Q, s)

st.write(f"Order: {sarima_order}")
st.write(f"Seasonal Order: {sarima_seasonal_order}")

# File uploader for CSV input
uploaded_file = st.file_uploader("Choose a CSV file with 'datetime' and 'actual' columns", type="csv")

if uploaded_file is not None:
    try:
        user_data = pd.read_csv(uploaded_file, parse_dates=['datetime'], index_col='datetime')
        st.write("Uploaded Data:")
        st.write(user_data.head())

        # Resample the data to daily frequency
        daily_user_data = user_data['actual'].resample('D').sum()

        # Fit SARIMA model to the user's data
        model = SARIMAX(daily_user_data, order=sarima_order, seasonal_order=sarima_seasonal_order)
        results = model.fit()

        # Forecast future values
        forecast_steps = st.number_input('Enter number of days to forecast', min_value=1, max_value=365, value=30)
        forecast = results.get_forecast(steps=forecast_steps)
        forecast_df = forecast.summary_frame()

        # Plotting the actual data and forecast
        st.subheader('Forecast Results')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_user_data, label='Actual')
        ax.plot(forecast_df['mean'], label='Forecast', linestyle='--')
        ax.fill_between(forecast_df.index, forecast_df['mean_ci_lower'], forecast_df['mean_ci_upper'], color='k', alpha=0.2)
        ax.legend()
        st.pyplot(fig)
    except ValueError as e:
        st.error(f"Error reading the CSV file: {e}")
        st.write("Please ensure the CSV file has 'datetime' and 'actual' columns.")
        st.write("Columns in the uploaded file:")
        uploaded_file.seek(0)  # Reset the file pointer to the beginning
        sample_df = pd.read_csv(uploaded_file, nrows=5)
        st.write(sample_df.columns)
else:
    st.info('Please upload a CSV file to proceed.')

# Path to the forecast vs actual image
forecast_image_path = 'forecast_vs_actual.png'

# Check if the forecast image exists and display it
if os.path.exists(forecast_image_path):
    st.subheader('Forecast vs Actual Image')
    st.image(forecast_image_path)
else:
    st.error(f"Forecast vs actual image not found at {forecast_image_path}")
