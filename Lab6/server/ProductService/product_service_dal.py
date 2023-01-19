# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logger
from product_models import Product
from utils import FaunaClients
from faunadb.query import let, get, ref, collection, merge, select, var, delete, create, update, \
  map_, lambda_, paginate, documents
from faunadb.errors import FaunaError
clients = {}

def get_product(event, key):    
    try:
        productId = key
        tenantId = event['requestContext']['authorizer']['tenantId']

        global clients
        db = FaunaClients(clients, tenantId)

        item = db.query(
          let(
            { 'product': get(ref(collection('product'), productId)) },
            merge(
              select(['data'], var('product')),
              { 'productId':  select(['ref', 'id'], var('product')) }
            )
          )
        )
        product = Product(item['productId'], item['sku'], item['name'], item['description'], item['price'], item['quantity'], item['backorderedLimit'], item['backordered'])
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('GetItem succeeded:'+ str(product))
        return product

def delete_product(event, key):    
    try:
        productId = key
        tenantId = event['requestContext']['authorizer']['tenantId']

        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
          select(
            ['ref', 'id'],
            delete(
              ref(collection('product'), productId)
            )
          )
        )
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('DeleteItem succeeded:')
        return response


def create_product(event, payload):
    tenantId = event['requestContext']['authorizer']['tenantId']        
    try:
        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
          let(
            {
              'result': create(collection('product'), {
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
              'id': select(['ref', 'id'], var('result')),
              'backordered': select(['data', 'backordered'], var('result'))
            }
          )
        )
        product = Product(response['id'], payload.sku, payload.name, payload.description, payload.price, payload.quantity, payload.backorderedLimit, response['backordered'])
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('PutItem succeeded:')
        return product

def update_product(event, payload, key):    
    try:
        productId = key
        tenantId = event['requestContext']['authorizer']['tenantId']  

        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
          let(
            {
              'result': update(
                ref(collection('product'), productId), {
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
              'id': select(['ref', 'id'], var('result')),
              'backordered': select(['data', 'backordered'], var('result'))
            }
          )
        )
        product = Product(productId, payload.sku, payload.name, payload.description, payload.price, payload.quantity, payload.backorderedLimit, response['backordered'])
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('UpdateItem succeeded:')
        return product        

def get_products(event, tenantId):
    products =[]
    try:
        tenantId = event['requestContext']['authorizer']['tenantId']
        global clients
        db = FaunaClients(clients, tenantId)

        results = db.query(
          map_(
            lambda_('x', 
              let(
                { 'product': get(var('x')) },
                merge(
                  { 'productId': select(['ref', 'id'], var('product')) },
                  select(['data'], var('product'))
                )
              )
            ),
            paginate(documents(collection('product')))
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
        logger.info('Get products succeeded')
        return products
