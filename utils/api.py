import httpx
import json

async def make_post_request(url, data, headers=None):
    """
    Makes an asynchronous POST request to the specified URL with the given data.
    
    Args:
        url (str): The URL to make the POST request to.
        data (dict): The data to be sent in the POST request.
        headers (dict, optional): Any headers to be included in the request.
    
    Returns:
        httpx.Response: The response object from the POST request.
    """
    if headers is None:
        headers = {}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=serialize_json(data), headers=headers)
            response.raise_for_status()
            return response
        except httpx.RequestError as e:
            print(f"Error making POST request: {e}")
            return None

async def make_put_request(url, data, headers=None):
    """
    Makes an asynchronous PUT request to the specified URL with the given data.
    
    Args:
        url (str): The URL to make the PUT request to.
        data (dict): The data to be sent in the PUT request.
        headers (dict, optional): Any headers to be included in the request.
    
    Returns:
        httpx.Response: The response object from the PUT request.
    """
    if headers is None:
        headers = {}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, data=serialize_json(data), headers=headers)
            response.raise_for_status()
            return response
        except httpx.RequestError as e:
            print(f"Error making PUT request: {e}")
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