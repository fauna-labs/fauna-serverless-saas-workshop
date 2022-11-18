# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import utils
import logger
import product_service_dal
from types import SimpleNamespace

def get_product(event, context):
    logger.info("Request received to get a product")
    params = event['pathParameters']
    productId = params['id']
    try:
        product = product_service_dal.get_product(event, productId)
        logger.info("Request completed to get a product")    
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


def create_product(event, context):    
    logger.info("Request received to create a product")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    logger.info(payload)
    try:
        product = product_service_dal.create_product(event, payload)
        logger.info("Request completed to create a product")
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


def update_product(event, context):
    logger.info("Request received to update a product")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    params = event['pathParameters']
    key = params['id']
    try:
        product = product_service_dal.update_product(event, payload, key)
        logger.info("Request completed to update a product") 
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


def delete_product(event, context):
    logger.info("Request received to delete a product")
    params = event['pathParameters']
    key = params['id']
    try:
        response = product_service_dal.delete_product(event, key)
        logger.info("Request completed to delete a product")
        return utils.create_success_response("Successfully deleted the product")
    except Exception as e:
        return utils.generate_error_response(e)


def get_products(event, context):
    logger.info("Request received to get all products")
    try:
        response = product_service_dal.get_products(event)
        logger.info("Request completed to get all products")
        return utils.generate_response(response)
    except Exception as e:
        return utils.generate_error_response(e)

  