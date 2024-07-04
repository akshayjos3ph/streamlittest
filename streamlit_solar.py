import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
import os

# Streamlit app title
st.title('Solar Generation in Germany: SARIMA Forecast')


# Path to the forecast vs actual image
forecast_image_path = 'forecast_vs_actual.png'

# Check if the forecast image exists and display it
if os.path.exists(forecast_image_path):
    st.subheader('Forecast vs Actual Image')
    st.image(forecast_image_path)
else:
    st.error(f"Forecast vs actual image not found at {forecast_image_path}")


# Display the SARIMA model parameters
st.subheader('SARIMA Model Parameters')

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
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV file to inspect its columns
        user_data = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Columns:")
        st.write(user_data.columns)
        
        # Display the first few rows of the uploaded data
        st.write("First few rows of the uploaded data:")
        st.write(user_data.head())
        
        # Strip any leading/trailing whitespace from column names
        user_data.columns = user_data.columns.str.strip()
        
        # Check if the required columns are present
        required_columns = {'datetime', 'actual'}
        if not required_columns.issubset(user_data.columns):
            st.error(f"The CSV file must contain the following columns: {required_columns}")
        else:
            # Explicitly parse the 'datetime' column
            user_data['datetime'] = pd.to_datetime(user_data['datetime'], errors='coerce')
            
            # Drop rows with invalid datetime
            user_data = user_data.dropna(subset=['datetime'])
            
            # Set 'datetime' as the index
            user_data = user_data.set_index('datetime')
            st.write("Uploaded Data Preview after setting 'datetime' as index:")
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
else:
    st.info('Please upload a CSV file to proceed.')