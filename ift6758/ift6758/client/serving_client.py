import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 6060):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """
        data = X.to_json(orient='split')
        prediction_url = f"{self.base_url}/predict"
        response = requests.post(prediction_url, json = data.values)
        return pd.read_json(response.json(),orient = 'split')
    
    
    def logs(self) -> dict:
        """Get server logs"""
        response = requests.get(self.base_url +'/logs')

        logs_data = response.json()
        # logger.info("Logs finished")
        return logs_data['logs']
    
    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """
        response = requests.post(self.base_url+'/download_registry_model',
                                 json={'workspace': workspace, 'model': model, 'version': version})
        logger.info("Model download finished")
        return response.json()


if __name__ == '__main__':
    # Example usage
    client = ServingClient()
    # print(client.logs())
    print(client.download_registry_model(workspace='ift6758-milestone2-udem', model='baseline_model_angle', version='1.0.0'))
    # print(client.logs())
    # X= pd.DataFrame([[0]])
    # client.predict(X)
    # print(client.logs())
