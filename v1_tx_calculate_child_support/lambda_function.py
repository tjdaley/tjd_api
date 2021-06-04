"""
lambda_function.py - AWS Lambda Function to calculate child support in Texas.

Copyright (c) 2021 by Thomas J. Daley. All. Rights. Reserved.
"""
import json
import logging
import math
from config import *

def lambda_handler(event, context):
    """
    Function to calculate child support in Texas.
    """
    raise Exception("Event: " + json.dumps(event))
    missing_fields = verify_fields(event)
    if missing_fields:
        raise Exception("Missing fields: " + ", ".join(missing_fields))
    user_data = copy_event_data(event)
    clean_data(user_data)

    net_resources_cap = 9200.0 * 12.0
    user_data['gross_income_annual'] = user_data['income_amount'] * user_data['income_frequency']
    user_data['medical_annual'] = user_data['medical_ins_amount'] * user_data['medical_ins_frequency']
    user_data['dental_annual'] = user_data['dental_ins_amount'] * user_data['dental_ins_frequency']
    user_data['union_dues_annual'] = user_data['union_dues_amount'] * user_data['union_dues_frequency']
    user_data['social_sec_annual'] = social_security(user_data)
    user_data['medicare_annual'] = medicare(user_data)
    user_data['income_tax_annual'] = federal_income_tax(user_data)
    user_data['net_resources_annual'] = annual_net_resources(user_data)
    user_data['support_factor'] = support_factor(user_data)
    user_data['child_support_annual'] = min(user_data['net_resources_annual'], net_resources_cap) * user_data['support_factor']
    scale_numbers(user_data)
    return user_data


def verify_fields(event: dict) -> list:
    keys = [
        'income_amount', 'income_frequency', 'medical_ins_amount', 'medical_ins_frequency',
        'dental_ins_amount', 'dental_ins_frequency', 'union_dues_amount', 'union_dues_frequency',
        'self_employed', 'children_inside', 'children_outside'
    ]
    return [k for k in keys if k not in event]



def copy_event_data(event: dict) -> dict:
    """
    Localize the data we receive.
    """
    keys = [
        'income_amount', 'income_frequency', 'medical_ins_amount', 'medical_ins_frequency',
        'dental_ins_amount', 'dental_ins_frequency', 'union_dues_amount', 'union_dues_frequency',
        'self_employed', 'children_inside', 'children_outside'
    ]

    # return {k: event.get(k, None) for k in keys}
    return {k: event[k] for k in keys}


def clean_data(user_data):
    edit_data(user_data)
    convert_types(user_data)


def scale_numbers(user_data: dict):
    fields = [
        'gross_income_annual', 'medical_annual', 'dental_annual', 'union_dues_annual',
        'social_sec_annual', 'medicare_annual', 'income_tax_annual', 'net_resources_annual',
        'child_support_annual'
    ]

    for field in fields:
        user_data[field] = round_up(user_data[field])
        month_key = field.replace('_annual', '_monthly')
        user_data[month_key] = round_up(user_data[field] / 12.0)


def round_up(number, decimals: int = 2) -> float:
    factor = int('1' + ('0' * decimals))
    return math.ceil(number * factor) / factor


def support_factor(user_data: dict):
    factors = [
        [],
        [.2, .175, .16, .1475, .1360, .1333, .1314, .13],
        [.25, .225, .2063, .19, .1833, .1786, .175, .1722],
        [.3, .2738, .2520, .24, .2314, .225, .22, .216],
        [.35, .322, .3033, .29, .28, .2722, .266, .2609],
        [.4, .3733, .3543, .34, .3289, .32, .3127, .3067],
        [.4, .3771, .36, .3467, .336, .3273, .32, .3138],
        [.4, .38, .3644, .352, .3418, .3333, .3262, .32]
    ]
    children_in = min(user_data['children_inside'], len(CHILD_SUPPORT_FACTORS)-1)
    children_out = min(len(CHILD_SUPPORT_FACTORS[children_in])-1, user_data['children_outside'])
    return CHILD_SUPPORT_FACTORS[children_in][children_out]


def annual_net_resources(user_data: dict):
    """
    From Texas Family Code 154.062.
    """
    return user_data['gross_income_annual'] - \
           user_data['medical_annual'] - \
           user_data['dental_annual'] - \
           user_data['union_dues_annual'] - \
           user_data['social_sec_annual'] - \
           user_data['medicare_annual'] - \
           user_data['income_tax_annual']


def social_security(user_data):
    """
    Calculate annual Social Security Taxes.
    """
    if user_data['self_employed']:
        taxable_income = min(user_data['gross_income_annual'] * US_SELF_EMPLOYMENT_FACTOR, US_MAX_SOC_SEC_WAGES)
        return taxable_income * US_SOC_SEC_RATE_1099
    taxable_income = min(user_data['gross_income_annual'], US_MAX_SOC_SEC_WAGES)
    return taxable_income * US_SOC_SEC_RATE_W2


def medicare(user_data):
    """
    Calculate annual Medicare taxes.
    """
    if user_data['self_employed']:
        taxable_income = user_data['gross_income_annual'] * US_SELF_EMPLOYMENT_FACTOR
        return taxable_income * US_MEDICARE_RATE_1099
    return user_data['gross_income_annual'] * US_MEDICARE_RATE_W2


def federal_income_tax(user_data: dict) -> float:
    """
    Compute US federal income taxes.
    """
    gross = user_data['gross_income_annual'] - US_IRC_PERSONAL_EXEMPTION - US_IRC_STANDARD_DEDUCTION

    if user_data['self_employed']:
        gross -= user_data['social_sec_annual'] / 2
        gross -= user_data['medicare_annual'] / 2

    if gross >= 518400.0:
        return 156235.0 + .37 * max(gross-518400.0, 0.0)

    if gross >= 207351.0:
        return 47367.5 + .35 * max(gross-207350.0, 0.0)

    if gross >= 163301.0:
        return 33217.5 + .32 * max(gross-163300.0, 0.0)

    if gross >= 85526.0:
        return 14605.5 + .24 * max(gross-85525.0, 0.0)

    if gross >= 40126.0:
        return 4617.5 + .22 * max(gross-40125.0, 0.0)

    if gross >= 9876.0:
        return 987.5 + .12 * max(gross-9875.0, 0.0)

    return .1 * gross


def edit_data(user_data: dict):
    """
    Remove common characters that we don't need and that will blow up numeric conversions.
    """
    for key, value in user_data.items():
        user_data[key] = value.replace('$', '').replace(',', '').strip()


def convert_types(user_data):
    types = {
        'income_frequency': int,
        'medical_ins_frequency': int,
        'dental_ins_frequency': int,
        'self_employed': bool,
        'union_dues_frequency': int,
        'income_amount': float,
        'medical_ins_amount': float,
        'dental_ins_amount': float,
        'children_inside': int,
        'children_outside': int,
        'union_dues_amount': float
    }

    for key, value in user_data.items():
        if types.get(key) == int:
            user_data[key] = int(value)
            continue
        if types.get(key) == bool:
            user_data[key] = value.upper() == 'YES'
            continue
        if types.get(key) == float:
            user_data[key] = float(value)
            continue

def test():
    data = {
        'income_amount': '$5,000.00',
        'income_frequency': '12',
        'children_inside': '1',
        'children_outside': '0',
        'medical_ins_amount': '350.00',
        'medical_ins_frequency': '12',
        'dental_ins_amount': '54.50',
        'dental_ins_frequency': '12',
        'self_employed': 'YES',
        'union_dues_amount': '$50.00 ',
        'union_dues_frequency': ' 12 ',
    }
    print(json.dumps(lambda_handler(data, {}), indent=4))


if __name__ == '__main__':
    test()
