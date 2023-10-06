"""
Helper functions.
- OAuth
- API requests
"""
import json
import os
from time import time
from typing import Any
from datetime import datetime

import requests
from dotenv import load_dotenv

from OAuth2 import oauth

load_dotenv()

# Constants
FARM_ID = os.environ['FARM_SHORTCODE_ID']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
API_URL = os.environ['API_URL']
TOKEN_URL = os.environ['TOKEN_URL']
AUTH_URL = os.environ['AUTH_URL']
REDIRECT_URL = os.environ['REDIRECT_URI']
FARM_COUNTRY = os.environ['FARM_COUNTRY']
USER_NAME = os.environ['USER_NAME']
PASSWORD = os.environ['PASSWORD']
CROP_URL = os.environ['CROP_URL']

# Global Variables
OAUTH_DETAILS = None
CURRENT_YEAR = None


def get_current_year() -> int:
    """
    Returns an integer of the current year.
    :return: Current year int.
    """
    global CURRENT_YEAR

    if CURRENT_YEAR is not None:
        return CURRENT_YEAR

    CURRENT_YEAR = datetime.now().year

    return CURRENT_YEAR


def get_headers() -> dict:
    """
    Returns a dictionary of headers for API requests.
    :return: Headers dictionary.
    """
    return {
        'Authorization': f'Bearer {get_access_token()}',
        'Accept': 'application/json',
    }


def get_oauth_details() -> dict | None:
    """
    Returns the OAuth2 details from the JSON file.
    :return: Token dictionary if successful, None otherwise.
    """
    global OAUTH_DETAILS

    if OAUTH_DETAILS is not None:
        return OAUTH_DETAILS

    try:
        with open('OAuth2/oauth.json', 'r', encoding='utf-8') as file:
            OAUTH_DETAILS = json.load(file)
            return OAUTH_DETAILS
    except FileNotFoundError:
        print("OAuth JSON file not found.")
    except json.JSONDecodeError:
        print("Invalid JSON format in the OAuth JSON file.")

    return None


def get_access_token() -> str | None:
    """
    Returns the access token from the OAuth2 details.
    :return: Access token value if successful, None otherwise.
    """
    global OAUTH_DETAILS

    if OAUTH_DETAILS is None:
        OAUTH_DETAILS = get_oauth_details()

    if OAUTH_DETAILS is not None:
        return OAUTH_DETAILS.get('access_token')

    return None


def get_url(api_type: str, path_vars: list = None) -> str:
    """
    Returns the URL for the specified API.
    :param path_vars:
    :param api_type: String from: 'accounts', 'account', 'livestock_list', 'livestock_transactions', 'livestock_account_mappings', 'cashflow'
    :return: API URL
    """
    match api_type:
        case 'accounts':
            return f'{API_URL}/farms/{FARM_ID}/accounts'
        case 'account':
            return f'{API_URL}/farms/{FARM_ID}/account/{path_vars[0]}'
        case 'livestock_list':
            return f'{API_URL}/farms/{FARM_ID}/livestock/trackers'
        case 'livestock_transactions':
            return f'{API_URL}/farms/{FARM_ID}/livestock/transactions'
        case 'livestock_account_mappings':
            return f'{API_URL}/farms/{FARM_ID}/livestock/{path_vars[0]}/account_mappings'
        case 'cashflow':
            return f'{API_URL}/farms/{FARM_ID}/reports/cashflow'


def get_api(api_type: str, query_params: dict = None, path_vars: list = None) -> Any | None:
    """
    Returns the JSON response from the specified GET request.
    :param path_vars:
    :param api_type: String from: 'accounts', 'livestock_list', 'livestock_transactions'
    :param query_params: dictionary of query parameters
    :return: JSON-encoded content of a response if successful, None otherwise.
    """
    url = get_url(api_type, path_vars)
    request = requests.get(url, headers=get_headers(), params=query_params or {}, timeout=10)
    if request.status_code == 200:
        return request.json()
    print('Error getting ' + api_type)
    print(request.status_code)
    print(request.text)
    return None


def refresh_token_if_expired(force_refresh: bool = False):
    """
    Checks if the access token is still valid and refreshes it if necessary.
    """
    global OAUTH_DETAILS
    if force_refresh or OAUTH_DETAILS.get('expires_at', 0) <= time():
        oauth.refresh_token()


def reset_oauth_details():
    """
    Resets the OAuth2 details.
    """
    global OAUTH_DETAILS
    OAUTH_DETAILS = None


def find_dictionary(outer_dict, target_dict) -> dict | None:
    """
    Finds a dictionary inside a dictionary
    """
    for key, inner_dict in outer_dict.items():
        if inner_dict == target_dict:
            return key
    return None
