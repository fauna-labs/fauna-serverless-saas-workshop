# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# import os
# import boto3
# from botocore.exceptions import ClientError
import uuid
import logger

from product_models import Product
# from types import SimpleNamespace
# from boto3.dynamodb.conditions import Key

from utils import FaunaFromConfig
from faunadb import query as q
from faunadb.errors import FaunaError

# table_name = os.environ['PRODUCT_TABLE_NAME']
# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(table_name)

db = None

def get_product(event, productId):
    try:
        global db
        if db is None:
            db = FaunaFromConfig()

        item = db.query(
          q.let(
            { 'product': q.get(q.ref(q.collection('product'), productId)) },
            q.merge(
              q.select(['data'], q.var('product')),
              { 'productId':  q.select(['ref', 'id'], q.var('product')) }
            )
          )
        )
        product = Product(item['productId'], item['sku'], item['name'], item['description'], item['price'], item['quantity'], item['backorderedLimit'], item['backordered'])
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info("GetItem succeeded:"+ str(product))
        return product

def delete_product(event, productId):
    try:
        global db
        if db is None:
            db = FaunaFromConfig()

        response = db.query(
          q.select(
            ['ref', 'id'],
            q.delete(
              q.ref(q.collection('product'), productId)
            )
          )
        )        
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info("DeleteItem succeeded:")
        return response


def create_product(event, payload):
    product = None    
    try:
        global db
        if db is None:
            db = FaunaFromConfig()

        response = db.query(
          q.let(
            {
              'result': q.create(q.collection('product'), {
                    'data': {
                      'sku': payload.sku,
                      'name': payload.name,
                      'description': payload.description,
                      'price': payload.price,
                      'quantity': payload.quantity,
                      'backorderedLimit': payload.backorderedLimit,
                      'backordered': True if payload.quantity < payload.backorderedLimit else False
                    }
                  })
            },
            {
              'id': q.select(['ref', 'id'], q.var('result')),
              'backordered': q.select(['data', 'backordered'], q.var('result'))
            }
          )
        )
        product = Product(response['id'], payload.sku, payload.name, payload.description, payload.price, payload.quantity, payload.backorderedLimit, response['backordered'])
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info("PutItem succeeded:")
        return product

def update_product(event, payload, productId):
    try:
        global db
        if db is None:
            db = FaunaFromConfig()

        response = db.query(
          q.let(
            {
              'result': q.update(
                q.ref(q.collection('product'), productId), {
                  'data': {
                    'sku': payload.sku,
                    'name': payload.name,
                    'description': payload.description,
                    'price': payload.price,
                    'quantity': payload.quantity,
                    'backorderedLimit': payload.backorderedLimit,
                    'backordered': True if payload.quantity < payload.backorderedLimit else False
                  }
                }
              )
            },
            {
              'id': q.select(['ref', 'id'], q.var('result')),
              'backordered': q.select(['data', 'backordered'], q.var('result'))
            }
          )
        )
        product = Product(productId, payload.sku, payload.name, payload.description, payload.price, payload.quantity, payload.backorderedLimit, response['backordered'])

    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info("UpdateItem succeeded:")
        return product        

def get_products(event):    
    products =[]
    try:
        global db
        if db is None:
            db = FaunaFromConfig()

        results = db.query(
          q.map_(
            q.lambda_('x', 
              q.let(
                { 'product': q.get(q.var('x')) },
                q.merge(
                  { 'productId': q.select(['ref', 'id'], q.var('product')) },
                  q.select(['data'], q.var('product'))
                )
              )
            ),
            q.paginate(q.documents(q.collection('product')))
          )
        )
        results = results['data']
        for item in results:
            product = Product(item['productId'], item['sku'], item['name'], item['description'], item['price'], item['quantity'], item['backorderedLimit'], item['backordered'])
            products.append(product)
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info("Get products succeeded")
        return products



