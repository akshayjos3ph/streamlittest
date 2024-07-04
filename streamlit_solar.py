import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import nbformat
from nbconvert import PythonExporter
import tempfile
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Streamlit app title
st.title('Solar Generation in Germany: SARIMA Forecast')

# Function to extract and execute data from Jupyter notebooks
def extract_and_execute_notebook(notebook_path):
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    exporter = PythonExporter()
    source, _ = exporter.from_notebook_node(nb)
    
    # Save the extracted code to a temporary file to ensure it's clean
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(source.encode())
        temp_file_path = temp_file.name
    
    # Execute the extracted code
    with open(temp_file_path) as temp_file:
        exec(temp_file.read(), globals())
    
    # Clean up the temporary file
    os.remove(temp_file_path)

# Paths to the Jupyter notebooks
model_notebook_path = 'ModelSolar.ipynb'
data_notebook_path = 'DataSolar.ipynb'

# Extract and execute the code from the notebooks
extract_and_execute_notebook(model_notebook_path)
extract_and_execute_notebook(data_notebook_path)

# Display the SARIMA model parameters
st.subheader('SARIMA Model Parameters')
if 'sarima_order' in globals() and 'sarima_seasonal_order' in globals():
    st.write(f"Order: {sarima_order}")
    st.write(f"Seasonal Order: {sarima_seasonal_order}")
else:
    st.write("SARIMA model parameters not found in the dataset.")

# File uploader for CSV input
uploaded_file = st.file_uploader("Choose a CSV file with 'datetime' and 'actual' columns", type="csv")

if uploaded_file is not None:
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
else:
    st.info('Please upload a CSV file to proceed.')
