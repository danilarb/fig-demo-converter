import json
import os
from requests_oauthlib import OAuth2Session

import helpers


def get_oauth_session():
    return OAuth2Session(
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


def get_access_token(client_secret):
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(helpers.auth_url)
    print('Please go to the following URL and authorize the application:', authorization_url)

    authorization_code = input('Enter the authorization code: ')

    return oauth.fetch_token(helpers.token_url, code=authorization_code, client_secret=client_secret)


def save_oauth_details(token, file_path=os.path.join(os.path.dirname(__file__), 'oauth.json')):
    with open(file_path, 'w') as file:
        json.dump(token, file, ensure_ascii=True, indent=4)


def setup_oauth2():
    client_id = helpers.client_id
    client_secret = helpers.client_secret
    oauth_file_path = os.path.join(os.path.dirname(__file__), 'oauth.json')

    if not os.path.exists(oauth_file_path):
        token = get_access_token(client_secret)
        save_oauth_details(token, oauth_file_path)

    elif os.path.getsize(oauth_file_path) == 0:
        token = get_access_token(client_secret)
        save_oauth_details(token, oauth_file_path)

    else:
        if helpers.get_access_token() is None:
            token = get_access_token(client_secret)
            save_oauth_details(token, oauth_file_path)
        else:
            oauth_details = helpers.get_oauth_details()
            if oauth_details is not None:
                oauth = get_oauth_session()
                helpers.access_token = None
                token = oauth.refresh_token(helpers.token_url, client_id=client_id,
                                            client_secret=client_secret,
                                            refresh_token=oauth_details.get('refresh_token'))
                save_oauth_details(token, oauth_file_path)
