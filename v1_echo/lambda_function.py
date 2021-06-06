"""
lambda_function.py - Echo the text param.

Copyright (c) 2021 by Thomas J. Daley, J.D. All Rights Reserved.
"""
import json


def lambda_handler(event, context):
    echo_string = event.get('queryStringParameters', {}).get('text', 'Mr. Noname')
    context_serializable = {k:v for k, v in context.__dict__.items() if type(v) in [int, float, bool, str, list, dict]}
    response = {
        'headers': event.get('headers'),
        'message': f"Say '{echo_string}'",
        'event': event,
        'context': context_serializable
    }
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
