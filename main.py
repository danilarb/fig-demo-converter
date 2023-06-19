"""
Main file for the program.
"""
from OAuth2 import oauth
from Accounts import accounts
from Livestock import livestock
from Transactions import transactions
import helpers


def main():
    """
    Main function.
    """
    oauth.initialise_oauth2()
    accounts.convert()
    helpers.refresh_token_if_expired()
    livestock.convert()
    helpers.refresh_token_if_expired()
    transactions.convert()
    print('Done!')


if __name__ == '__main__':
    main()
