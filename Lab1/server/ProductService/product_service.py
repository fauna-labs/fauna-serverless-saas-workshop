# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import utils
import logger
from types import SimpleNamespace

from aws_xray_sdk.core import patch_all
patch_all()

from utils import Fauna, load_config
from fauna import fql

db = None


def get_product(event, context):
    logger.info("Request received to get a product")
    params = event['pathParameters']
    productId = params['id']
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.byId(${productId}) {
              id,
              name,
              description,
              sku,
              price,
              quantity,
              backorderedLimit,
              backordered            
            }
            """,
            productId = productId)
        )
        logger.info("Request completed to get a product")    
        product = response.data
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


def create_product(event, context):    
    logger.info("Request received to create a product")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    logger.info(payload)
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.create({
              'sku': ${sku},
              'name': ${name},
              'description': ${description},
              'price': ${price},
              'quantity': ${quantity},
              'backorderedLimit': ${backorderedLimit},
              'backordered': ${backordered}
            }) {
              id,
              sku,
              name,
              description,
              price,
              quantity,
              backorderedLimit,
              backordered
            }
            """,
            sku=payload.sku,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            quantity=payload.quantity,
            backorderedLimit=payload.backorderedLimit,
            backordered=True if payload.quantity < payload.backorderedLimit else False
            )
        )        
        logger.info("Request completed to create a product")
        product = response.data
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


def update_product(event, context):
    logger.info("Request received to update a product")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    params = event['pathParameters']
    productId = params['id']
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.byId(${productId}).update({
              'sku': ${sku},
              'name': ${name},
              'description': ${description},
              'price': ${price},
              'quantity': ${quantity},
              'backorderedLimit': ${backorderedLimit},
              'backordered': ${backordered}
            }) {
              id,
              sku,
              name,
              description,
              price,
              quantity,
              backorderedLimit,
              backordered
            }
            """,
            productId=productId,
            sku=payload.sku,
            name=payload.name, 
            description=payload.description,
            price=payload.price,
            quantity=payload.quantity,
            backorderedLimit=payload.backorderedLimit,
            backordered=True if payload.quantity < payload.backorderedLimit else False
            )
        )        
        logger.info("Request completed to update a product") 
        product = response.data
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


def delete_product(event, context):
    logger.info("Request received to delete a product")
    params = event['pathParameters']
    productId = params['id']
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.byId(${productId}).delete()
            """, 
            productId = productId
            )
        )
        logger.info("Request completed to delete a product")
        return utils.create_success_response("Successfully deleted the product")
    except Exception as e:
        return utils.generate_error_response(e)


def get_products(event, context):
    logger.info("Request received to get all products")
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.all() {
              id,
              name,
              description,
              sku,
              price,
              quantity,
              backorderedLimit,
              backordered
            }
            """)
        )        
        logger.info("Request completed to get all products")
        results = response.data['data']
        return utils.generate_response(results)
    except Exception as e:
        return utils.generate_error_response(e)

  