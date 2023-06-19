"""
Converts the farm's transactions from a .csv file to a .json file.
"""

import csv
import json
import os
from datetime import datetime


REVENUE_ACCOUNT_CODES = []
EQUITY_ACCOUNT_CODES = []


def get_rev_exp_codes():
    global REVENUE_ACCOUNT_CODES
    global EQUITY_ACCOUNT_CODES
    with open(os.path.join('Accounts/revenue.json'), 'r') as file:
        REVENUE_ACCOUNT_CODES = json.load(file)
    with open(os.path.join('Accounts/equity.json'), 'r') as file:
        EQUITY_ACCOUNT_CODES = json.load(file)


def is_valid_date(date_string):
    try:
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False


def get_json_transactions():
    folder_path = 'Transactions'
    json_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('cashflow.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data.append(json.load(file).get('data'))
    return json_data


def create_transactions_from_row(rows, periods):
    global REVENUE_ACCOUNT_CODES
    global EQUITY_ACCOUNT_CODES
    transactions = []
    for row in rows.values():
        account = row.get('account_code') or row.get('account_id')
        try:
            inv_account = int(account) in REVENUE_ACCOUNT_CODES or int(account) in EQUITY_ACCOUNT_CODES
        except Exception:
            inv_account = False

        if account is None:
            continue

        for data in row.get('data').values():
            date = data.get('date')
            amount = float(data.get('value'))
            datetime_date = datetime.strptime(date, '%Y-%m')
            year = datetime_date.year - 2023
            if amount == 0:
                continue
            if account == '155' and datetime_date > datetime(2022, 7, 1):
                continue
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


def totals_is_zero(totals):
    for period in totals.values():
        if period.get('value') != 0:
            return False
    return True


def sum_rows_of_sections(sections, periods):
    transactions = []

    for section in sections.values():
        if section.get('totals') is not None and totals_is_zero(section.get('totals')):
            continue

        if section.get('rows') is not None:
            transactions += create_transactions_from_row(section.get('rows'), periods)
        if section.get('sections') is not None:
            transactions += sum_rows_of_sections(section.get('sections'), periods)

    return transactions


def convert_transactions_from_json(transactions_json):
    transactions = []
    for cashflow in transactions_json:
        sections = cashflow.get('sections')
        periods = cashflow.get('period')

        transactions += sum_rows_of_sections(sections, periods)
    return transactions


def convert():
    transactions = []
    get_rev_exp_codes()
    transactions_json = get_json_transactions()
    transactions += convert_transactions_from_json(transactions_json)

    with open(os.path.join(os.path.dirname(__file__), 'transactions.json'), 'w') as file:
        json.dump(transactions, file, indent=4)
