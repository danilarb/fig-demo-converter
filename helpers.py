import json
import os
import requests
from time import time
from dotenv import load_dotenv

from OAuth2 import oauth

load_dotenv()

# Constants
FARM_ID = os.environ['FARM_ID']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
API_URL = os.environ['API_URL']
TOKEN_URL = os.environ['TOKEN_URL']
AUTH_URL = os.environ['AUTH_URL']
REDIRECT_URL = os.environ['REDIRECT_URI']

# Global Variables
oauth_details = None


def get_headers():
    """
    Returns a dictionary of headers for API requests.
    :return: Headers dictionary.
    """
    return {
        'Authorization': f'Bearer {get_access_token()}',
        'Accept': 'application/json',
    }


def get_oauth_details():
    """
    Returns the OAuth2 details from the JSON file.
    :return: Token dictionary if successful, None otherwise.
    """
    global oauth_details

    if oauth_details is not None:
        return oauth_details

    try:
        with open('OAuth2/oauth.json', 'r') as file:
            oauth_details = json.load(file)
            return oauth_details
    except FileNotFoundError:
        print("OAuth JSON file not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format in the OAuth JSON file.")

    return None


def get_access_token():
    """
    Returns the access token from the OAuth2 details.
    :return: Access token value if successful, None otherwise.
    """
    global oauth_details

    if oauth_details is None:
        oauth_details = get_oauth_details()

    if oauth_details is not None:
        return oauth_details.get('access_token')

    return None


def get_url(api_type: str) -> str:
    """
    Returns the URL for the specified API.
    :param api_type: String from: 'accounts', 'livestock_list', 'livestock_transactions'
    :return: API URL
    """
    match api_type:
        case 'accounts':
            return f'{API_URL}/farms/{FARM_ID}/accounts'
        case 'livestock_list':
            return f'{API_URL}/farms/{FARM_ID}/livestock/trackers'
        case 'livestock_transactions':
            return f'{API_URL}/farms/{FARM_ID}/livestock/transactions'


def get_api(api_type: str, query_params: dict = None):
    """
    Returns the JSON response from the specified GET request.
    :param api_type: String from: 'accounts', 'livestock_list', 'livestock_transactions'
    :param query_params: dictionary of query parameters
    :return: JSON-encoded content of a response if successful, None otherwise.
    """
    url = get_url(api_type)
    request = requests.get(url, headers=get_headers(), params=query_params or {})
    if request.status_code == 200:
        return request.json()
    else:
        print('Error getting ' + api_type)
        print(request.status_code)
        print(request.text)
        return None


def refresh_token_if_expired(force_refresh: bool = False):
    """
    Checks if the access token is still valid and refreshes it if necessary.
    """
    if force_refresh or oauth_details.get('expires_at', 0) <= time():
        oauth.refresh_token()


def reset_oauth_details():
    """
    Resets the OAuth2 details.
    """
    global oauth_details
    oauth_details = None
