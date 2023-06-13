"""
Converts the farm's livestock trackers and transactions into the needed JSON format.
"""
import json
import os

import helpers


def get_list_api() -> list | None:
    """
    Returns the livestock list API request data.
    :return: List of livestock trackers.
    """
    return helpers.get_api('livestock_list').get('data')


def get_transactions_api() -> list | None:
    """
    Returns the livestock transactions API request data.
    :return: List of livestock transactions.
    """
    return helpers.get_api('livestock_transactions').get('data')


def get_transactions() -> list | None:
    """
    Returns the farm's livestock transactions from the JSON file or API request.
    :return: List of livestock transactions.
    """
    # Check if file exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'original_livestock.json')):
        return get_transactions_api()
    # Check if file is empty
    if os.path.getsize(os.path.join(os.path.dirname(__file__), 'original_livestock.json')) == 0:
        return get_transactions_api()
    # Return file contents
    with open(os.path.join(os.path.dirname(__file__), 'original_livestock.json'), 'r') as file:
        transactions = json.load(file)
        return transactions


def convert_transactions(data_list):
    """
    Converts the farm's livestock transactions from API into the needed JSON format.
    :param data_list: List of livestock transactions.
    """
    new_list = []

    errors = False


def convert():
    """
    Converts the farm's livestock from API into the needed JSON format.
    """
    transactions = get_transactions()
    print(transactions)
    if transactions is not None:
        convert_transactions(transactions)
    else:
        print('Could not get transactions.')
