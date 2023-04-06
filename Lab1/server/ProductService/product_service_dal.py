# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logger
from product_models import Product

from utils import Fauna, load_config
from fauna import fql
from fauna.errors import FaunaException

db = None

def get_product(event, productId):
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.byId("${productId}") {
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
        item = response.data
        product = Product(item['id'], 
                          item['sku'], 
                          item['name'], 
                          item['description'], 
                          item['price'], 
                          item['quantity'], 
                          item['backorderedLimit'], 
                          item['backordered'])
    except FaunaException as e:
        logger.error("Error getting a product: {}".format(e))
        raise e
    else:
        logger.info("GetItem succeeded:"+ str(product))
        return product

def delete_product(event, productId):
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            product.byId("${productId}").delete()
            """, 
            productId = productId
            )
        )

    except FaunaException as e:
        logger.error("Error deleting a product: {}".format(e))
        raise e
    else:
        logger.info("DeleteItem succeeded:")
        return None


def create_product(event, payload):
    product = None
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
        response = response.data
        product = Product(response['id'], 
                          payload.sku,
                          payload.name, 
                          payload.description, 
                          payload.price, 
                          payload.quantity, 
                          payload.backorderedLimit, 
                          response['backordered'])
    except FaunaException as e:
        logger.error("Error adding a product: {}".format(e))
        raise e
    else:
        logger.info("PutItem succeeded:")
        return product

def update_product(event, payload, productId):
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
        response = response.data
        product = Product(productId, 
                          payload.sku, 
                          payload.name, 
                          payload.description, 
                          payload.price, 
                          payload.quantity, 
                          payload.backorderedLimit, 
                          response['backordered'])
    except FaunaException as e:
        logger.error("Error updating a product: {}".format(e))
        raise e
    else:
        logger.info("UpdateItem succeeded:")
        return product        

def get_products(event): 
    products =[]

    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        results = db.query(
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
        results = results.data['data']
        for item in results:
            product = Product(item['id'], 
                              item['sku'], 
                              item['name'], 
                              item['description'], 
                              item['price'], 
                              item['quantity'], 
                              item['backorderedLimit'], 
                              item['backordered'])
            products.append(product)
    except FaunaException as e:
        logger.error("Error getting all products: {}".format(e))
        raise e
    else:
        logger.info("Get products succeeded")
        return products



