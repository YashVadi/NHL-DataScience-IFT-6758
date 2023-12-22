# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import json

# Define the URL for your serving app
SERVING_APP_URL = "http://0.0.0.0:5000"

# Function to download the model from CometML
def download_model(workspace, model, version):
    # download_url = f"https://www.comet.ml/api/rest/v2/model/download/{workspace}/{model}/{version}"
    # response = requests.get(download_url)
    
    # if response.status_code == 200:
    #     # Save the downloaded model to a file or load it directly
    #     # Replace this with your actual model loading logic
    st.success("Model downloaded successfully.")
    # else:
    #     st.error("Failed to download the model.")

# Function to ping the game and display results
def ping_game(game_id):
    # Ping the game using your game client (replace with your actual implementation)
    # X, idx, ... = game_client.ping_game(game_id, idx, ...)
    
    X = [0,0]
    # Send a request to the serving app for predictions
    predict_url = f"{SERVING_APP_URL}/predict"
    response = requests.post(predict_url, json=X)
    predictions = response.json().get('predictions', [])
    
    # Display the results
    st.subheader("Game Info:")
    st.write(f"Game ID: {game_id}")
    st.write("Home Team: ...")  # Replace with actual data
    st.write("Away Team: ...")  # Replace with actual data
    st.write("Period: ...")  # Replace with actual data
    st.write("Time Left: ...")  # Replace with actual data
    st.write("Current Score: ...")  # Replace with actual data
    
    st.subheader("Expected Goals:")
    st.write("Sum of xG for Home Team: ...")  # Replace with actual data
    st.write("Sum of xG for Away Team: ...")  # Replace with actual data
    st.write("Difference: ...")  # Replace with actual data
    
    st.subheader("Model Output:")
    st.write("Dataframe of Features and Model Output:")
    # Display the dataframe with features and model output
    # You may need to adjust this based on your specific dataframe structure
    st.write(pd.DataFrame({'Feature 1': ..., 'Feature 2': ..., 'Model Output': predictions}))

# Streamlit app UI
st.title("Expected Goals Dashboard")

# Inputs in the left sidebar
with st.sidebar:
    st.subheader("Model Information:")
    workspace = st.text_input("Workspace:")
    model = st.text_input("Model:")
    version = st.text_input("Version:")
    if st.button("Download Model"):
        download_model(workspace, model, version)

# Text input for game ID
game_id = st.text_input("Game ID:")
if st.button("Ping Game"):
    ping_game(game_id)