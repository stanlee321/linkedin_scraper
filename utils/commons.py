from typing import Any
import uuid


def generate_uuid():
    """
    Generates a new UUID.
    
    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())



def transform_data(data: Any, page: int, search_url: str) -> dict:
    
    new_data = {
            "page": page,
            "search_url": search_url,
            "status": "active",
            "uuid":  generate_uuid()
        }
    
    return {**data, **new_data }   



