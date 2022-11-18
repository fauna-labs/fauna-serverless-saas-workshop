# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import utils
import logger
import order_service_dal
from types import SimpleNamespace
from aws_lambda_powertools import Tracer

def get_order(event, context):
    logger.info("Request received to get a order")
    params = event['pathParameters']
    orderId = params['id']
    try:
        order = order_service_dal.get_order(event, orderId)

        logger.info("Request completed to get a order")
        
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


def create_order(event, context):  
    logger.info("Request received to create a order")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    try:
        order = order_service_dal.create_order(event, payload)
        logger.info("Request completed to create a order")
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


def update_order(event, context):    
    logger.info("Request received to update a order")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    params = event['pathParameters']
    orderId = params['id']
    try:
        order = order_service_dal.update_order(event, payload, orderId)
        logger.info("Request completed to update a order")     
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


def delete_order(event, context):
    logger.info("Request received to delete a order")
    params = event['pathParameters']
    orderId = params['id']
    try:
        response = order_service_dal.delete_order(event, orderId)
        logger.info("Request completed to delete a order")
        return utils.create_success_response("Successfully deleted the order")
    except Exception as e:
        return utils.generate_error_response(e)


def get_orders(event, context):
    logger.info("Request received to get all orders")
    try:
        response = order_service_dal.get_orders(event)
        logger.info("Request completed to get all orders")
        return utils.generate_response(response)
    except Exception as e:
        return utils.generate_error_response(e)

  