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
    """
        data: {
                'name': '',
                'role': '',
                'location': '',
                'connection': '',
                'services': '',
                'profile_url': '',  # Added field for the profile URL
                'search_url': ''  # Added field for the search URL
            }
    """

    new_data = {
        "page": page,
        "search_url": search_url,
        "status": "active",
        "uuid":  generate_uuid(),

        "location_work": data.get('Pais.1', ""),
        "business_name_main": data.get('Unnamed: 0', ""),
        "business_name_secondary": data.get('Empresa', ""),
        "website": data.get("Sitio web", ""),
        "email": data.get("email/Alternativo", ""),
        "phone": data.get("phone", ""),
        "whatsapp": data.get("whatsapp", ""),

        "message_type": data.get("Tipo de mensaje", ''),
        "ci_intro_ippb": data.get("C.I. Intro iPPb", ''),
        "ci_staff_aug": data.get("C.I. Staff Aug", ''),
        "ci_gestion_datos": data.get("C.I. Gestion datos", ''),
        "ci_nkt_medio": data.get("C.I. MKT", ''),
        "medio": data.get("Medio", ''),
        "send_by": data.get("quien envió", ''),
        "linkedin_status": data.get("Estado LinkedIn", '')


    }
    # {'name': 'Luis Rodriguez', 
    #  'role': 'Software Engineer | Senior Full Stack Engineer | React | JavaScript | Typescript | NodeJS', 
    #  'location': 'Cochabamba, Bolivia', 
    #  'connection': '• 2nd2nd degree connection', 
    #  'services': 'Pierina Batalla', 
    #  'profile_url': 'https://www.linkedin.com/in/luis-rodriguez-a8531340', 
    #  'search_url': 'https://www.linkedin.com/search/results/people/?keywords=nodejs&origin=SWITCH_SEARCH_VERTICAL&sid=t~Y&page=2',
    #     'page': 2, 'status': 'active', 
    #     'uuid': 'b402181b-6505-4fa8-b441-df3168790a3b', 
    #     'location_work': '', 
    #     'business_name_main': '', 
    #     'business_name_secondary': '', 
    #     'website': '', 'email': '', 'phone': '', 'whatsapp': '', 
    #     'message_type': None, 
    #     'ci_intro_ippb': None, 
    #     'ci_staff_aug': None, 
    #     'ci_gestion_datos': None, 
    #     'ci_nkt_medio': None, 
    #     'medio': None, 
    #     'send_by': None, 
    #     'linkedin_status': None
    #     }

    return {**data, **new_data}
