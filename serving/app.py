
from flask import Flask, jsonify, request
import json
import logging
import pandas as pd
from comet_ml import API

from dotenv import load_dotenv, find_dotenv
import os

import pickle

load_dotenv(find_dotenv())

COMET_API_KEY = os.environ.get("COMET_API_KEY")
LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
print(LOG_FILE)

app = Flask(__name__)


# current_model = None
comet_api = API(api_key=COMET_API_KEY, cache=True)

@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logging.info("App initialized")
    global current_model


@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""

    try:
        with open(LOG_FILE, "r") as log_file:
            logs = log_file.read()
        return jsonify({'logs': logs})
    except Exception as e:
        logging.error(f'Error in /logs endpoint: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500


# # endpoint for retrieving logs
# @app.route('/logs', methods=['GET'])
# def get_logs():
#     try:
#         with open('app_logs.log', 'r') as log_file:
#             logs = log_file.read()
#             print("request received")
#         return jsonify({'logs': logs})
#     except Exception as e:
#         logging.error(f'Error in /logs endpoint: {str(e)}')
#         return jsonify({'error': 'Internal Server Error'}), 500

@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.    
    """
    # Get POST json data
    global current_model
    json = request.get_json()
    app.logger.info(json)

    workspace = json['workspace']
    model_id = json['model']
    version = json['version']

    # TODO: check to see if the model you are querying for is already downloaded
    # check if the directory with model exists
    if os.path.exists(f'./models/{model_id}'):
        try:
            app.logger.info(f"{model_id} already downloaded")
            model_file = [f for f in os.listdir(f'./models/{model_id}/') if f.endswith('.pkl')][0]

            with open(f'./models/{model_id}/{model_file}', 'rb') as f:
                current_model = pickle.load(f)
            app.logger.info(f"{model_id} loaded")
            
            return jsonify({'message': f"Loaded the {model_id} from the previous download"})
        except Exception as e:
            app.logger.error(f'Error in /download_registry_model endpoint: {str(e)}')
            return jsonify({'error': 'Internal Server Error'}), 500


    else:
        try:
            model = comet_api.get_model(
                workspace=workspace,
                model_name=model_id
            )
            model.download(version, f"./models/{model_id}")

            model_file = None

            model_file = [f for f in os.listdir(f'./models/{model_id}/') if f.endswith('.pkl')][0]

            with open(f'./models/{model_id}/{model_file}', 'rb') as f:
                current_model = pickle.load(f)
            app.logger.info(f"Model {model_id} downloaded and loaded")
            return jsonify({'message': f"Model with model_id '{model}' downloaded and loaded"})
        except Exception as e:
            app.logger.error(f'Error in /download_registry_model endpoint: {str(e)}')
            return jsonify({'error': 'Internal Server Error'}), 500

@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    data = request.get_json()
    app.logger.info(json)

    # TODO:
    # try:
    input_features = pd.read_json(data, orient='records')
    
    predictions = current_model.predict_proba(input_features)
    
    result = {'predictions': predictions.tolist()}
    return jsonify(result)
    # except Exception as e:
    #     logging.error(f'Error in /predict endpoint: {str(e)}')
    #     return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=6060, host='0.0.0.0')
