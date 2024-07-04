import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import nbformat
from nbconvert import PythonExporter
import tempfile
import os

# Streamlit app title
st.title('Solar Generation in Germany: Actual vs Predicted')

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

# Assuming the notebooks have saved the necessary data into these variables
# Check if the necessary variables are defined
if 'df' in globals():
    # Display the SARIMA model parameters
    st.subheader('SARIMA Model Parameters')
    if 'sarima_order' in globals() and 'sarima_seasonal_order' in globals():
        st.write(f"Order: {sarima_order}")
        st.write(f"Seasonal Order: {sarima_seasonal_order}")
    else:
        st.write("SARIMA model parameters not found in the dataset.")

    # Filtering the dataset for solar generation data in Germany
    solar_data_actual = df['DE_solar_generation_actual']
    solar_data_predicted = df['DE_solar_generation_predicted'] if 'DE_solar_generation_predicted' in df.columns else None
    
    # Resampling data to daily frequency
    daily_solar_actual = solar_data_actual.resample('D').sum()
    daily_solar_predicted = solar_data_predicted.resample('D').sum() if solar_data_predicted is not None else None

    # Plotting the actual data
    st.subheader('Daily Solar Generation Actual')
    st.line_chart(daily_solar_actual)

    if daily_solar_predicted is not None:
        # Plotting the actual and predicted data
        st.subheader('Daily Solar Generation: Actual vs Predicted')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_solar_actual, label='Observed')
        ax.plot(daily_solar_predicted, label='Predicted', linestyle='--')
        ax.legend()
        st.pyplot(fig)
else:
    st.info('Failed to load data. Please check the notebooks and try again.')
