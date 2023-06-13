import json
import os

import helpers


def get_accounts_api():
    return helpers.get_api('accounts')


def get_accounts():
    # Check if file exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'original_accounts.json')):
        return get_accounts_api()
    # Check if file is empty
    elif os.path.getsize(os.path.join(os.path.dirname(__file__), 'original_accounts.json')) == 0:
        return get_accounts_api()
    # Return file contents
    else:
        with open(os.path.join(os.path.dirname(__file__), 'original_accounts.json'), 'r') as file:
            accounts = json.load(file)
            return accounts


def convert_accounts(data_list):
    new_list = []

    system_accounts = {
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

    errors = False

    for key, item in data_list.items():
        code = item.get('code')

        if code is None:
            continue

        try:
            code = int(code)
        except ValueError:
            pass

        name = item.get('name')
        is_system_account = item.get('system_account')

        if name in system_accounts and is_system_account:
            obj = create_account(code, name, item, system_accounts.get(name))
        elif name not in system_accounts and is_system_account:
            print(f"Error: {name} is a system account but is not in the system_accounts dictionary.")
            errors = True
            break
        else:
            obj = create_account(code, name, item, '')

        if any(d['Code'] == obj['Code'] for d in new_list):
            continue

        new_list.append(obj)

    if not errors:
        new = open(os.path.join(os.path.dirname(__file__), 'accounts.json'), 'w')
        json.dump(new_list, new, ensure_ascii=False, indent=4)
        new.close()
        print('Accounts converted successfully.')
    else:
        print('Accounts not converted due to errors.')


def create_account(code, name, item, system_account):
    return {
        'Code': code,
        'Name': name,
        'Class': item.get('class'),
        'Type': item.get('type'),
        'TaxType': item.get('tax_type'),
        'SystemAccount': system_account,
    }


def convert():
    accounts = get_accounts()
    if accounts is not None:
        convert_accounts(accounts)
    else:
        print('Could not get accounts.')
