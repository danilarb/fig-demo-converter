import getpass
import json
import os
import signal

from requests import HTTPError, Timeout
from requests_oauthlib import OAuth2Session

import helpers

# Constants
OAUTH_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'oauth.json'))
AUTH_ERROR_MESSAGE = 'An error occurred during the authorization process:'
OAUTH_OBJ_ERROR_MESSAGE = 'Error creating OAuth2Session object:'

# Non-local Variables
oauth_session = None


def get_oauth_session():
    """
    Returns an OAuth2 session object.
    :return: OAuth2 session object.
    """
    global oauth_session
    if oauth_session is not None:
        return oauth_session

    try:
        oauth_session = OAuth2Session(
            helpers.CLIENT_ID,
            token=helpers.get_oauth_details(),
            auto_refresh_url=helpers.TOKEN_URL,
            auto_refresh_kwargs={
                'client_id': helpers.CLIENT_ID,
                'client_secret': helpers.CLIENT_SECRET,
            },
            redirect_uri=helpers.REDIRECT_URL,
            token_updater=save_oauth_details,
        )
    except Exception as e:
        print(OAUTH_OBJ_ERROR_MESSAGE, e)
        return None

    return oauth_session


def get_authorization_code():
    """
    Prompts the user to enter the authorization code.
    :return: The authorization code entered by the user.
    """
    try:
        signal.alarm(60)
        return getpass.getpass('Enter the authorization code: ').strip()
    except KeyboardInterrupt:
        print('Authorization process interrupted by user.')
        return None
    except Exception as e:
        print(AUTH_ERROR_MESSAGE, e)
        return None
    finally:
        signal.alarm(0)


def get_access_token():
    """
    Fetches an OAuth2 access token for the application.
    :return: Token dictionary if successful, None otherwise.
    """
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(helpers.AUTH_URL)
    print('Please go to the following URL and authorize the application:', authorization_url)

    try:
        authorization_code = get_authorization_code()
        return oauth.fetch_token(helpers.TOKEN_URL, code=authorization_code, client_secret=helpers.CLIENT_SECRET)
    except (HTTPError, Timeout, ConnectionError) as e:
        print(AUTH_ERROR_MESSAGE, e)
        return None


def refresh_token():
    """
    Refreshes the OAuth2 access token.
    """
    oauth = get_oauth_session()
    token = oauth.refresh_token(helpers.TOKEN_URL,
                                client_id=helpers.CLIENT_ID,
                                client_secret=helpers.CLIENT_SECRET,
                                refresh_token=helpers.get_oauth_details().get('refresh_token'))
    helpers.reset_oauth_details()
    save_oauth_details(token)


def save_oauth_details(token, file_path=os.path.join(os.path.dirname(__file__), 'oauth.json')):
    """
    Saves the OAuth2 access token to a JSON file.
    :param token: The token to save.
    :param file_path: Filepath to JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(token, file, ensure_ascii=True, indent=4)


def initialise_oauth2():
    """
    Initialises the OAuth2 process.
    """
    if helpers.get_oauth_details() is None:
        token = get_access_token()
        if token is not None:
            save_oauth_details(token, OAUTH_FILE_PATH)
    else:
        helpers.token_check_and_refresh()
