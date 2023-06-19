"""
Converts the farm's livestock trackers and transactions into the needed JSON format.
"""
import json
import os

from datetime import datetime

import helpers


def get_farm_account(uuid: str) -> dict | None:
    """
    Returns the farm account API request data.
    :param uuid:
    :return:
    """
    return helpers.get_api('account', path_vars=[uuid])


def get_account_mappings_api(tracker_id: str) -> list | None:
    """
    Returns the tracker's account mappings.
    :return: List of the tracker's account mappings.
    """
    return helpers.get_api('livestock_account_mappings', path_vars=[tracker_id])


def get_list_api(per_page: int = 15) -> list | None:
    """
    Returns the livestock list API request data.
    :return: List of livestock trackers.
    """
    return helpers.get_api('livestock_list', {'per_page': per_page}).get('data')


def get_transactions_api(per_page: int = 15) -> list | None:
    """
    Returns the livestock transactions API request data.
    :return: List of livestock transactions.
    """
    return helpers.get_api('livestock_transactions', {'per_page': per_page}).get('data')


def get_trackers_total_api() -> int | None:
    """
    Returns the total number of livestock trackers.
    :return: total livestock trackers.
    """
    return helpers.get_api('livestock_list', {'per_page': 1}).get('meta').get('total')


def get_transactions_total_api() -> int | None:
    """
    Returns the total number of livestock transactions.
    :return: total livestock transactions.
    """
    return helpers.get_api('livestock_transactions', {'per_page': 1}).get('meta').get('total')


def get_trackers() -> list | None:
    """
    Returns the farm's livestock trackers from the JSON file or API request.
    :return: List of livestock trackers.
    """
    return get_list_api(get_trackers_total_api())


def get_transactions() -> list | None:
    """
    Returns the farm's livestock transactions from the JSON file or API request.
    :return: List of livestock transactions.
    """
    # Check if file exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'original_livestock.json')):
        return get_transactions_api(get_transactions_total_api())
    # Check if file is empty
    if os.path.getsize(os.path.join(os.path.dirname(__file__), 'original_livestock.json')) == 0:
        return get_transactions_api(get_transactions_total_api())
    # Return file contents
    with open(os.path.join(os.path.dirname(__file__), 'original_livestock.json'), 'r') as file:
        transactions = json.load(file)
        return transactions


def convert_transactions(transactions: list, trackers: list):
    """
    Converts the farm's livestock transactions from API into the needed JSON format.
    :param transactions: List of livestock transactions.
    :param trackers: List of livestock trackers.
    """
    trackers_dict = {}
    trackers_transactions_dict = {}
    for tracker in trackers:
        trackers_dict[tracker.get('id')] = {
            'tracker': tracker.get('name'),
            'stock_classes': {
                item['uuid']: item['name'] for item in tracker.get('stock_classes')
            }
        }
        trackers_transactions_dict[tracker.get('name')] = []

    for transaction in transactions:
        date_string = transaction.get('accrual_date').get('date')
        date_format = "%Y-%m-%d %H:%M:%S"
        date_object = datetime.strptime(date_string, date_format)

        new_transaction = {
            'StockClass': trackers_dict.get(transaction.get('tracker_id'))
            .get('stock_classes')
            .get(transaction.get('stock_class_id')),
            'Transition': transaction.get('transition'),
            'Quantity': transaction.get('quantity'),
            'Year': date_object.year - 2023,
            'Month': date_object.month,
        }

        if transaction.get('amount'):
            new_transaction['Amount'] = abs(transaction.get('amount'))
        if transaction.get('weight_per_head') == 0 or transaction.get('weight_per_head'):
            new_transaction['Weight'] = transaction.get('weight_per_head')
        if transaction.get('type'):
            new_transaction['Type'] = transaction.get('type')
        else:
            new_transaction['Type'] = None

        trackers_transactions_dict[trackers_dict.get(transaction.get('tracker_id')).get('tracker')]\
            .append(new_transaction)

    parent_dir = os.path.dirname(__file__)

    for tracker, transactions_list in trackers_transactions_dict.items():
        dir_path = os.path.join(parent_dir, tracker)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, 'transactions.json'), 'w') as file:
            json.dump(transactions_list, file, indent=4)


def convert_trackers(trackers):
    """
    Converts the farm's livestock trackers from API into the needed JSON format.
    :param trackers: List of livestock trackers.
    """
    parent_dir = os.path.dirname(__file__)

    trackers_dict = {}
    for tracker in trackers:
        account_mappings = get_account_mappings_api(tracker.get('id'))

        purchase_uuid = next(item["account_id"] for item in account_mappings if item["transition"] == "purchase")
        sale_uuid = next(item["account_id"] for item in account_mappings if item["transition"] == "sale")

        purchase_account = get_farm_account(purchase_uuid)
        sale_account = get_farm_account(sale_uuid)


        trackers_dict[tracker.get('name')] = {
            'TrackerType': 'stock',
            'StockTypeUuid': tracker.get('stock_type_id'),
            'PurchaseAccount': int(purchase_account.get('code')),
            'SalesAccount': int(sale_account.get('code')),
            'StockClasses': []
        }

        for stock_class in tracker.get('stock_classes'):
            trackers_dict[tracker.get('name')]['StockClasses'].append({
                'Name': stock_class.get('name'),
                'Enabled': stock_class.get('enabled'),
                'OpeningQuantity': None
            })

    for tracker in trackers:
        dir_path = os.path.join(parent_dir, tracker.get('name'))
        with open(os.path.join(dir_path, 'tracker.json'), 'w') as file:
            json.dump(trackers_dict.get(tracker.get('name')), file, indent=4)


def convert():
    """
    Converts the farm's livestock from API into the needed JSON format.
    """
    transactions = get_transactions()
    trackers = get_list_api()
    if transactions is not None and trackers is not None:
        convert_transactions(transactions, trackers)
        convert_trackers(trackers)
    else:
        print('Could not get transactions or trackers.')
