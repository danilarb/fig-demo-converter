import json
import os
from requests_oauthlib import OAuth2Session

import helpers

oauth_session = None


def get_oauth_session():
    global oauth_session
    if oauth_session is not None:
        return oauth_session

    oauth_session = OAuth2Session(
        helpers.client_id,
        token=helpers.get_oauth_details(),
        auto_refresh_url=helpers.token_url,
        auto_refresh_kwargs={
            'client_id': helpers.client_id,
            'client_secret': helpers.client_secret,
        },
        redirect_uri=helpers.redirect_uri,
        token_updater=save_oauth_details,
    )

    return oauth_session


def get_access_token():
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(helpers.auth_url)
    print('Please go to the following URL and authorize the application:', authorization_url)

    authorization_code = input('Enter the authorization code: ')

    return oauth.fetch_token(helpers.token_url, code=authorization_code, client_secret=helpers.client_secret)


def refresh_token():
    oauth = get_oauth_session()
    token = oauth.refresh_token(helpers.token_url,
                                client_id=helpers.client_id,
                                client_secret=helpers.client_secret,
                                refresh_token=helpers.get_oauth_details().get('refresh_token'))
    helpers.reset_oauth_details()
    save_oauth_details(token)


def save_oauth_details(token, file_path=os.path.join(os.path.dirname(__file__), 'oauth.json')):
    with open(file_path, 'w') as file:
        json.dump(token, file, ensure_ascii=True, indent=4)


def setup_oauth2():
    oauth_file_path = os.path.join(os.path.dirname(__file__), 'oauth.json')

    if helpers.get_access_token() is None:
        token = get_access_token()
        save_oauth_details(token, oauth_file_path)
    else:
        helpers.token_check_and_refresh()
