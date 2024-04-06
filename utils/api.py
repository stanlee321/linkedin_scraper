import requests
import json

def make_post_request(url, data, headers=None):
    """
    Makes a POST request to the specified URL with the given data.
    
    Args:
        url (str): The URL to make the POST request to.
        data (dict): The data to be sent in the POST request.
        headers (dict, optional): Any headers to be included in the request.
    
    Returns:
        requests.Response: The response object from the POST request.
    """
    if headers is None:
        headers = {}
    
    try:
        response = requests.post(url, data=serialize_json(data), headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making POST request: {e}")
        return None
    
    
def serialize_json(data):
    """
    Serializes the given data to JSON format.
    
    Args:
        data (dict): The data to be serialized.
    
    Returns:
        str: The JSON-serialized data.
    """
    return json.dumps(data, separators=(',', ':'), sort_keys=True, indent=2, default=str)