from typing import Any
import uuid


def generate_uuid():
    """
    Generates a new UUID.
    
    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())



def transform_data(data: Any, page: int) -> dict:
    
    new_data = {
            "message_sent": False,
            "message": None,
            "page": page,
            "status": "active",
            "uuid":  generate_uuid()
        }
    
    return {**data, **new_data }   



