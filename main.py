import OAuth2.oauth as oauth
import Accounts.accounts as accounts
import Livestock.livestock as livestock


def main():
    oauth.setup_oauth2()
    accounts.convert()
    livestock.convert()
    print('Done!')


if __name__ == '__main__':
    main()
