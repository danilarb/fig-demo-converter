"""
Converts the farm's transactions into the needed JSON format.
"""

import json
import os
from datetime import datetime

import helpers

REVENUE_ACCOUNT_CODES = set()
EQUITY_ACCOUNT_CODES = set()


def get_rev_equity_codes():
    """
    Creates the global variables for revenue and equity account codes.
    """
    global REVENUE_ACCOUNT_CODES
    global EQUITY_ACCOUNT_CODES

    with open(os.path.join('Accounts/revenue.json'), 'r', encoding='utf-8') as file:
        REVENUE_ACCOUNT_CODES = set(json.load(file))
    with open(os.path.join('Accounts/equity.json'), 'r', encoding='utf-8') as file:
        EQUITY_ACCOUNT_CODES = set(json.load(file))


def get_cashflow_api(data_type: str) -> dict:
    """
    Returns the cashflow report API request data.
    :return: Dictionary of the cashflow report for dates two years in the future to two years in the past. e.g.: Currently it's 2023-06. Cashflow period: 2020-12 - 2025-12
    """
    date_string = f'{helpers.get_current_year() + 2}-12'
    query = {
        'compare': 60,
        'date_start': date_string,
        'date_end': date_string,
        'data_type': data_type
    }

    return helpers.get_api('cashflow', query)


def create_cashflows():
    """
    Generates the cashflow files using the cashflow report API.
    """
    actuals_cashflow = get_cashflow_api('actuals')
    forecast_cashflow = get_cashflow_api('forecast')

    with open(os.path.join(os.path.dirname(__file__), 'actuals_cashflow.json'), 'w', encoding='utf-8') as file:
        json.dump(actuals_cashflow, file, indent=4)
    with open(os.path.join(os.path.dirname(__file__), 'forecast_cashflow.json'), 'w', encoding='utf-8') as file:
        json.dump(forecast_cashflow, file, indent=4)


def get_json_transactions() -> list:
    """
    Gets a list of transaction dictionaries from the x_cashflow.json files.
    :return: list of transaction dictionaries
    """
    create_cashflows()
    json_data = []

    for file_name in os.listdir(os.path.dirname(__file__)):
        if file_name.endswith('cashflow.json'):
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data.append(json.load(file).get('data'))

    return json_data


def create_transactions_from_row(rows: dict, periods: dict) -> list:
    """
    Reformats a cashflow report's row into demo farm template transaction objects.
    :return: list of formatted transaction dicts for the row
    """
    global REVENUE_ACCOUNT_CODES
    global EQUITY_ACCOUNT_CODES
    transactions = []
    for row in rows.values():
        account = row.get('account_code') or row.get('account_name')

        try:
            inv_account = account in REVENUE_ACCOUNT_CODES \
                          or account in EQUITY_ACCOUNT_CODES \
                          or int(account) in REVENUE_ACCOUNT_CODES \
                          or int(account) in EQUITY_ACCOUNT_CODES
        except ValueError:
            # Error comes from int(account) if account is a string
            inv_account = False

        for data in row.get('data').values():
            date = data.get('date')
            amount = float(data.get('value'))
            datetime_date = datetime.strptime(date, '%Y-%m')
            year = datetime_date.year - helpers.get_current_year()

            if amount == 0:
                continue
            if account in {'', None}:
                account = row.get('account_name')
            if inv_account:
                amount = 0 - amount

            transactions.append({
                'Type': periods.get(date).get('data_type').capitalize(),
                'Account': account,
                'Amount': amount,
                'Year': year,
                'Month': datetime.strptime(date, '%Y-%m').month,
            })

    return transactions


def totals_is_zero(totals) -> bool:
    """
    Checks if the totals are all 0
    :return: True or False
    """
    for period in totals.values():
        if period.get('value') != 0:
            return False
    return True


def sum_rows_of_sections(sections: dict, periods: dict) -> list:
    """
    Recursive. Adds the section's rows to a single list with formatted transactions.
    :return: Flattened list of all rows with transactions
    """
    transactions = []

    for section in sections.values():
        if section.get('totals') is not None and totals_is_zero(section.get('totals')):
            continue

        if section.get('rows') is not None:
            transactions += create_transactions_from_row(section.get('rows'), periods)
        if section.get('sections') is not None:
            transactions += sum_rows_of_sections(section.get('sections'), periods)

    return transactions


def convert_transactions_from_json(transactions_json: list) -> list:
    """
    Converts the cashflows into a list of formatted transactions
    :return: List of formatted transactions
    """
    transactions = []

    for cashflow in transactions_json:
        sections = cashflow.get('sections')
        periods = cashflow.get('period')

        transactions += sum_rows_of_sections(sections, periods)

    return transactions


def convert():
    """
    Converts a farm's transactions into the needed json format
    """
    transactions = []
    get_rev_equity_codes()
    transactions_json = get_json_transactions()
    transactions += convert_transactions_from_json(transactions_json)
    with open(os.path.join(os.path.dirname(__file__), 'transactions.json'), 'w', encoding='utf-8') as file:
        json.dump(transactions, file, indent=4)


def remove_duplicate_livestock_transactions():
    """
    Removes transactions found in both the livestock.json and transactions.json from the transactions.json
    """
    with open(os.path.join(os.path.dirname(__file__), 'transactions.json'), 'r', encoding='utf-8') as file:
        transactions = json.load(file)

    with open(os.path.join(os.path.dirname(__file__), 'livestock.json'), 'r', encoding='utf-8') as file:
        livestock = json.load(file)

    purchase_account = input('Tracker purchase account: ')
    sale_account = input('Tracker sales account: ')

    new_transactions = []
    bad_transactions = []

    for livestock_t in livestock:
        for transaction in transactions:
            if livestock_transaction_affected(livestock_t, transaction, purchase_account, sale_account):
                bad_transactions.append(transaction)

    for transaction in transactions:
        if transaction not in bad_transactions:
            new_transactions.append(transaction)

    with open(os.path.join(os.path.dirname(__file__), 'new_transactions.json'), 'w', encoding='utf-8') as file:
        json.dump(new_transactions, file, indent=4)


def livestock_transaction_affected(livestock_t: dict, transaction: dict, purchase_account: str, sale_account: str) -> bool:
    """
    Checks if the livestock transaction and farm transaction are identical
    :param livestock_t: livestock transaction
    :param transaction: farm transaction
    :param purchase_account: livestock tracker's purchase account
    :param sale_account: livestock tracker's sales account
    :return: True or False
    """
    if livestock_t.get('Transition') not in ['purchase', 'sale']:
        return False
    if abs(livestock_t.get('Amount')) != abs(transaction.get('Amount')):
        return False
    if livestock_t.get('Year') != transaction.get('Year'):
        return False
    if livestock_t.get('Month') != transaction.get('Month'):
        return False
    transition = livestock_t.get('Transition')
    if transition == 'purchase' and transaction.get('Account') != purchase_account:
        return False
    if transition == 'sale' and transaction.get('Account') != sale_account:
        return False
    return True


def remove_duplicate_crop_transactions():
    """
    Removes transactions found in both the invoices.json and transactions.json from the transactions.json
    """
    with open(os.path.join(os.path.dirname(__file__), 'transactions.json'), 'r', encoding='utf-8') as file:
        transactions = json.load(file)

    with open(os.path.join(os.path.dirname(__file__), 'invoices.json'), 'r', encoding='utf-8') as file:
        invoices = json.load(file)

    with open(os.path.join('Accounts', 'accounts.json'), 'r', encoding='utf-8') as file:
        all_accounts = json.load(file)

    new_transactions = []
    bad_transactions = []

    for invoice in invoices:
        for transaction in transactions:
            if crop_transaction_affected(invoice, transaction, all_accounts):
                bad_transactions.append(transaction)

    for transaction in transactions:
        if transaction not in bad_transactions:
            new_transactions.append(transaction)

    with open(os.path.join(os.path.dirname(__file__), 'new_transactions.json'), 'w', encoding='utf-8') as file:
        json.dump(new_transactions, file, indent=4)


def crop_transaction_affected(invoice: dict, transaction: dict, all_accounts: list) -> bool:
    """
    Checks if the invoice and transaction are identical
    :param invoice: crop season invoice dict
    :param transaction: farm transaction dict
    :param all_accounts: list of all account
    :return: True or False
    """
    invoice_date = datetime.fromisoformat(invoice.get('accrual_date'))
    invoice_accounts = resolve_account(invoice.get('lines')[0]['account'], all_accounts)

    if transaction.get('Account') not in invoice_accounts:
        return False
    if transaction.get('Year') != invoice_date.year - helpers.get_current_year():
        return False
    if transaction.get('Month') != invoice_date.month:
        return False
    if float(transaction.get('Amount')) != float(invoice.get('lines')[0]['amount']):
        return False
    if transaction.get('Type') != invoice.get('transaction_type').capitalize():
        return False
    return True


def resolve_account(account: str, all_accounts: list) -> list | None:
    """
    Gets the account's name and code
    :param account: account's name
    :param all_accounts: all farm accounts
    :return: list: [account_name, account_code]
    """
    for acc in all_accounts:
        if acc.get('Name') == account:
            return [account, str(acc.get('Code'))]
