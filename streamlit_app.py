# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
import json
import os

from ift6758.client.serving_client import ServingClient
from ift6758.client.game_client import GameClient

# Define the URL for your serving app
# SERVING_APP_URL = "0.0.0.0"
SERVING_APP_URL = "serving"
PORT: int = 6060

if "serving_client" not in st.session_state:
    st.session_state.serving_client = ServingClient(SERVING_APP_URL, PORT)

if not os.path.exists('tracker.json'):
    with open('tracker.json', 'w') as outfile:
        history = {}
        json.dump(history, outfile)

model_map = {
    'DistanceOnly': 'baseline_model_distance',
    'DistanceAndAngle': 'baseline_model_distance-angle'
}
model_map_inverse = {v: k for k, v in model_map.items()}

# Function to download the model from CometML
def load_model(workspace, model, version):

    model_map = {
        'DistanceOnly': 'baseline_model_distance',
        'DistanceAndAngle': 'baseline_model_distance-angle'
    }
    model_map_inverse = {v: k for k, v in model_map.items()}

    response = st.session_state.serving_client.download_registry_model(workspace=workspace, model=model_map[model], version=version)

    if response.status_code == 200:
        # Save the downloaded model to a file or load it directly
        # Replace this with your actual model loading logic
        st.success("Model loaded successfully.")
    else:
        st.error("Failed to load the model.")

# Function to ping the game and display results
def ping_game(game_id):
    # Ping the game using your game client (replace with your actual implementation)
    # X, idx, ... = game_client.ping_game(game_id, idx, ...)
    game_client = GameClient()
    
    df, live, game_id, home_team, away_team, home_score, away_score, period, timeRemaining = game_client.ping_game(game_id)

    # Make predictions using your serving client
    print(st.session_state.serving_client.feature_map)
    print(st.session_state.serving_client.model)
    features = st.session_state.serving_client.feature_map[st.session_state.serving_client.model]

    predict_proba = st.session_state.serving_client.predict(df[features])
    df['model_output'] = predict_proba
    # Display the results
    st.subheader("Game Info:")
    st.write(f"Game ID: {game_id}")
    st.write(f"Home Team: {home_team}")  
    st.write(f"Away Team: {away_team}")
    st.write(f"Period: {period}")  
    st.write(f"Time Left: {timeRemaining}")  
    st.subheader(f"Current Score:")
    st.write(f"Home Team(`{home_team}`):{home_score}")
    st.write(f"Away Team(`{away_team}`):{away_score}")

    st.subheader("Expected Goals:")
    xg_home = sum(df[df['home_or_away'] == 'home']['model_output'])
    xg_away = sum(df[df['home_or_away'] == 'away']['model_output'])
    st.write(f"Home Team: {sum(df[df['home_or_away'] == 'home']['model_output'])}")
    st.write(f"Away Team: {sum(df[df['home_or_away'] == 'away']['model_output'])}")



    # st.write(f"Sum of xG for Home Team: ...")  
    # st.write(f"Sum of xG for Away Team: ...")  
    st.subheader(f"Difference:")
    st.metric(label=f"{home_team}", value=f'{xg_home} ({home_score})', delta=xg_home - home_score)
    st.metric(label=f"{away_team}", value=f'{xg_away} ({away_score})', delta=xg_away - away_score)
    # st.metric(label="xG Difference", value=0.5)
    # st.metric(label="xG Difference", value=0.5)

    
    st.subheader("Model Output:")
    st.write("Dataframe of Features and Model Output:")
    st.write(pd.DataFrame({'distance': df['distance'], 'Angle': df['angle'], 'Model Output': predict_proba, 'isGoal': df['isGoal']}))

# Streamlit app UI
st.title("Expected Goals Dashboard")
 
# Inputs in the left sidebar
with st.sidebar:
    st.subheader("Model Information:")
    workspace = st.selectbox(
        "Select the comet workspace",
        ("ift6758-milestone2-udem", ""),
        index=1,
        placeholder="Write the workspace name",
    )
    model = st.selectbox(
        "Select the model",
        ('DistanceOnly', 'DistanceAndAngle'),
        index=None,
        placeholder="Write the model name",
    )
    version = st.selectbox(
        "Select the version",
        ('1.0.0', ''),
        index=None,
        placeholder="Write the version",
    )
    if st.button("Load Model"):
        load_model(workspace, model, version)

# Text input for game ID
game_id = st.text_input("Game ID:")
if st.button("Ping Game"):
    ping_game(game_id)