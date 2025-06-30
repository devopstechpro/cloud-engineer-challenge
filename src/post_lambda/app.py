import logging
import json
import os
from typing import Any
import boto3
import time
from decimal import Decimal

logger = logging.getLogger()

TABLE_NAME = os.environ['TABLE_NAME']

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# Convert numbers to Decimal objects to avoid floating point precision issues because DynamoDB does not support floats
def convert_numbers(obj):
    if isinstance(obj, list):
        return [convert_numbers(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_numbers(v) for k, v in obj.items()}
    elif isinstance(obj, float) or isinstance(obj, int):
        return Decimal(str(obj))
    else:
        return obj


def save_to_db(records: list[dict[str, Any]]):
    """Save records to the DynamoDB table with TTL and log the outcome.

    Parameters
    ----------
    records: list[dict[str, Any]]
        The data to save to the table.

    Notes
    -----
    Each record will be assigned an 'expires_at' attribute for 24h expiry.
    If the batch write fails, the error will be logged and re-raised.
    Successful saves are also logged.
    """
    # Set TTL for 24 hours from now
    expires_at = int(time.time()) + 24 * 3600
    try:
        with table.batch_writer() as batch:
            for record in records:
                record['expires_at'] = expires_at
                batch.put_item(Item=record)
        logger.info("Records are successfully saved to the DB table %s.", TABLE_NAME)
    except Exception as e:
        logger.error("Failed to save records to DynamoDB: %s", e, exc_info=True)
        raise


def lambda_handler(event, context):
    """Process POST request to the API."""
    logger.info(
        'Received %s request to %s endpoint',
        event["httpMethod"],
        event["path"])

    body = event.get('body')
    if body is not None:
        try:
            orders = json.loads(body)
            orders = convert_numbers(orders)
        except Exception as e:
            logger.error("Invalid JSON in request body: %s", e)
            return {
                "isBase64Encoded": False,
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"errorMessage": "Invalid JSON in request body"})
            }
        logger.info("Orders received: %s.", orders)
        save_to_db(records=orders)

        return {
            "isBase64Encoded": False,
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": ""
        }

    return {
        "isBase64Encoded": False,
        "statusCode": 400,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({"errorMessage": "Request body is empty"})
    }
