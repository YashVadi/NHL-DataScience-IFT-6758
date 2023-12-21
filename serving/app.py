# serving/app.py
from flask import Flask, jsonify, request
import json
import logging
import pandas as pd
from comet_ml import API

from dotenv import load_dotenv, find_dotenv
import os

from pickle

load_dotenv(find_dotenv())

COMET_API_KEY = os.environ.get("COMET_API_KEY")



app = Flask(__name__)

current_model = None
comet_ml_wrokspace = 'ift6758-milestone2-udem'
comet_ml_project_name = 'baselines'

comet_api = API(api_key=COMET_API_KEY, cache=True)


app = Flask(__name__)

current_model = None
comet_ml_wrokspace = 'ift6758-milestone2-udem'
comet_ml_project_name = 'baselines'

comet_api = API(api_key=COMET_API_KEY, cache=True)

# #get the Model object
# model = comet_api.get_model(workspace=comet_ml_wrokspace, model_name)

# # Download a Registry Model:
# model.download("1.0.0", "./models/")

# Setup logger
logging.basicConfig(filename='app_logs.log', level=logging.INFO)

# endpoint for predicting
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("\n\n")
        print(data)
        print("\n\n")
        input_features = pd.read_json(json.dumps(data), orient='records')
        
        predictions = current_model.predict(input_features)
        
        result = {'predictions': predictions.tolist()}
        return jsonify(result)
    except Exception as e:
        logging.error(f'Error in /predict endpoint: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500

# endpoint for retrieving logs
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open('app_logs.log', 'r') as log_file:
            logs = log_file.read()
            print("request received")
        return jsonify({'logs': logs})
    except Exception as e:
        logging.error(f'Error in /logs endpoint: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500
    
# endpoint for retrieving the model from comet.ml
@app.route('/download_registry_model/<model_id>', methods=['GET', 'POST'])
def getdownload_model(model_id):
    try:
        if model_id==None:
            return jsonify({'logs': "request recievwd for null model"})
        global current_model
        model = comet_api.get_model(
            workspace=comet_ml_wrokspace,
            model_name=model_id
        )
        model.download("1.0.0", f"./{model_id}")

        model_file = None

        model_file = [f for f in os.listdir(f'./{model_id}/') if f.endswith('.pkl')][0]

        with open(f'./{model_id}/{model_file}', 'rb') as f:
            current_model = pickle.load(f)
        logging.info(f"Model {model_id} downloaded a nd loaded")
        return jsonify({'message': 'Model downloaded and loaded'})
    except Exception as e:
        logging.error(f'Error in /download_registry_model endpoint: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500



if __name__ == '__main__':
    app.run(debug=True)
