"""
Converts the farm's accounts into the needed JSON format.
"""
import json
import os

import helpers

# Constants
SYSTEM_ACCOUNTS = {
    'Accounts Payable': 'CREDITORS',
    'Accounts Payable (Xero)': 'CREDITORS',
    'Accounts Receivable': 'DEBTORS',
    'Accounts Receivable (Xero)': 'DEBTORS',
    'Bank Revaluations': 'BANKREVALUATIONS',
    'GST': 'GST',
    'Historical Adjustment': 'HISTORICAL',
    'Realised Currency Gains': 'REALISEDCURRENCYGAIN',
    'Retained Earnings': 'RETAINEDEARNINGS',
    'Rounding': 'ROUNDING',
    'Tracking Transfers': 'TRACKINGTRANSFERS',
    'Unpaid Expense Claims': 'UNPAIDEXPCLM',
    'Unrealised Currency Gains': 'UNREALISEDCURRENCYGAIN',
    'Wages Payable': 'WAGESPAYABLE',
    'Sales Tax': 'GST',
    'Realized Currency Gains': 'REALISEDCURRENCYGAIN',
    'Unrealized Currency Gains': 'UNREALISEDCURRENCYGAIN',
}


def get_accounts_api() -> dict:
    """
    Returns the accounts API request data.
    :return: Dictionary of farm accounts.
    """
    return helpers.get_api('accounts')


def get_accounts() -> dict:
    """
    Returns the farm's accounts from the JSON file or API request.
    :return: Dictionary of farm accounts.
    """
    # Check if file exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'original_accounts.json')):
        return get_accounts_api()
    # Check if file is empty
    if os.path.getsize(os.path.join(os.path.dirname(__file__), 'original_accounts.json')) == 0:
        return get_accounts_api()
    # Return file contents
    with open(os.path.join(os.path.dirname(__file__), 'original_accounts.json'), 'r') as file:
        accounts = json.load(file)
        return accounts


def convert_accounts(data_list: dict) -> None:
    """
    Converts the farm's accounts from API into the needed JSON format.
    Found in accounts.json
    :param data_list: Dictionary of farm accounts.
    """
    new_list = []
    errors = False
    revenue = []
    equity = []

    for item in data_list.values():
        code = item.get('code')

        if code is None:
            continue

        try:
            code = int(code)
        except ValueError:
            pass

        name = item.get('name')
        is_system_account = item.get('system_account')

        if name in SYSTEM_ACCOUNTS and is_system_account:
            obj = create_account(code, name, item, SYSTEM_ACCOUNTS.get(name))
        elif name not in SYSTEM_ACCOUNTS and is_system_account:
            print(
                f"Error: {name} is a system account but is not in the system_accounts dictionary.")
            errors = True
            break
        else:
            obj = create_account(code, name, item, '')

        if any(d['Code'] == obj['Code'] for d in new_list):
            continue

        if obj['Class'] == 'REVENUE':
            revenue.append(obj.get('Code'))
        elif obj['Class'] == 'EQUITY':
            equity.append(obj.get('Code'))
        elif obj['SystemAccount'] == 'GST':
            equity.append(obj.get('Code'))

        new_list.append(obj)

    if not errors:
        with open(os.path.join(os.path.dirname(__file__), 'accounts.json'), 'w', encoding='utf-8') as new:
            json.dump(new_list, new, ensure_ascii=False, indent=4)
        print('Accounts converted successfully.')
        with open(os.path.join(os.path.dirname(__file__), 'revenue.json'), 'w', encoding='utf-8') as new:
            json.dump(revenue, new, ensure_ascii=False, indent=4)
        with open(os.path.join(os.path.dirname(__file__), 'equity.json'), 'w', encoding='utf-8') as new:
            json.dump(equity, new, ensure_ascii=False, indent=4)
    else:
        print('Accounts not converted due to errors.')


def create_account(code: str | int, name: str, item: dict, system_account: str) -> dict:
    """
    Creates an account object.
    :param code: Account code.
    :param name: Account name.
    :param item: Original account object.
    :param system_account: System account name
    :return: Account dictionary.
    """
    return {
        'Code': code,
        'Name': name,
        'Class': item.get('class'),
        'Type': item.get('type'),
        'TaxType': item.get('tax_type'),
        'SystemAccount': system_account,
    }


def convert():
    """
    Converts the farm's accounts into the needed JSON format.
    """
    accounts = get_accounts()
    if accounts is not None:
        convert_accounts(accounts)
    else:
        print('Could not get accounts.')
