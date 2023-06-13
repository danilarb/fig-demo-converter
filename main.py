import OAuth2.oauth as oauth
import Accounts.accounts as accounts
import Livestock.livestock as livestock
import helpers


def main():
    oauth.setup_oauth2()
    accounts.convert()
    helpers.token_check_and_refresh()
    livestock.convert()
    helpers.token_check_and_refresh()
    print('Done!')


if __name__ == '__main__':
    main()
