import json
import os
import requests

from dotenv import load_dotenv

load_dotenv()

farm_id = os.getenv('FARM_ID')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
api_url = os.getenv('API_URL')
token_url = os.getenv('TOKEN_URL')
auth_url = os.getenv('AUTH_URL')
redirect_uri = os.getenv('REDIRECT_URI')
access_token = None


def get_headers():
    print(get_access_token())
    return {
        'Authorization': f'Bearer {get_access_token()}',
        'Accept': 'application/json',
    }


def get_oauth_details():
    try:
        with open('OAuth2/oauth.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("OAuth JSON file not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format in the OAuth JSON file.")

    return None


def get_access_token():
    global access_token

    if access_token is not None:
        return access_token

    oauth_details = get_oauth_details()
    if oauth_details is not None:
        access_token = oauth_details.get('access_token')
        return access_token

    return None


def get_url(api_type):
    match api_type:
        case 'accounts':
            return f'{api_url}/farms/{farm_id}/accounts'
        case 'livestock':
            return f'{api_url}/farms/{farm_id}/livestock/transactions'


def get_api(api_type):
    url = get_url(api_type)
    request = requests.get(url, headers=get_headers())
    if request.status_code == 200:
        return request.json()
    else:
        print('Error getting ' + api_type)
        print(request.status_code)
        print(request.text)
        return None
