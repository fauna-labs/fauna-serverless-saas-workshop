# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from botocore.exceptions import ClientError
from order_models import Order
import logger

from utils import Fauna, load_config
from faunadb import query as q
from faunadb.errors import FaunaError, BadRequest, Unauthorized, NotFound
db = None

def get_order(event, orderId):
    
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        item = db.query(
          q.let(
            {
              'order': q.get(q.ref(q.collection('order'), orderId)),
              'orderProducts': q.map_(
                q.lambda_(
                  'x',
                  q.let(
                    { 'product': q.get(q.select(['product'], q.var('x'))) },
                    {
                      'quantity': q.select(['quantity'], q.var('x')),
                      'price': q.select(['price'], q.var('x')),
                      'productId': q.select(['ref', 'id'], q.var('product')),
                      'productName': q.select(['data', 'name'], q.var('product'), ''),
                      'productSku': q.select(['data', 'sku'], q.var('product'), ''),
                      'productDescription': q.select(['data', 'description'], q.var('product'), '')
                    }
                  )
                ),
                q.select(['data', 'orderProducts'], q.var('order'))
              )
            },
            q.merge(
              q.select(['data'], q.var('order')),
              {
                'orderId': q.select(['ref', 'id'], q.var('order')),
                'creationDate': q.to_string(q.select(['data', 'creationDate'], q.var('order'))),
                'orderProducts': q.var('orderProducts')
              },
            )
          )
        )
        order = Order(item['orderId'], item['orderName'], item['creationDate'], item['status'], item['orderProducts'])
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        return order

def delete_order(event, orderId):

    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.select(
            ['ref', 'id'],
            q.delete(
              q.ref(q.collection('order'), orderId)
            )
          )
        )
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('DeleteItem succeeded:')
        return response


def create_order(event, payload):
    
    order = None

    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.let(
            {
              'products': q.map_(
                q.lambda_(
                  'requestedProduct',
                  q.let(
                    {
                      'requestedQuantity': q.select(['quantity'], q.var('requestedProduct')),
                      'product': q.get(q.select(['product'], q.var('requestedProduct'))),
                      'currentQuantity': q.select(['data', 'quantity'], q.var('product')),
                      'backorderedLimit': q.select(['data', 'backorderedLimit'], q.var('product')),
                      'updatedQuantity': q.subtract(q.var('currentQuantity'), q.var('requestedQuantity')),
                    },
                    {
                      'ref': q.select('ref', q.var('product')),
                      'price': q.select(['data', 'price'], q.var('product')),
                      'name': q.select(['data', 'name'], q.var('product')),
                      'requestedQuantity': q.var('requestedQuantity'),
                      'updatedQuantity': q.var('updatedQuantity'),
                      'backorderedLimit': q.var('backorderedLimit'),
                      'backordered': q.lt(q.var('updatedQuantity'), q.var('backorderedLimit')) # if remaining stock < backorderedLimit, then backordered = True
                    }
                  )
                ),
                _format_order_products(payload.orderProducts)
              )
            },
            q.do(
              # for each product, check if stocked quantity is sufficient to fulfill the order
              q.foreach(
                q.lambda_(
                  'product',
                  q.if_(
                    q.lt(q.select(['updatedQuantity'], q.var('product')), 0), # if updatedQuantity < 0 then abort
                    q.abort(
                      q.concat(['Stock quantity for Product [', q.select(['name'], q.var('product')), '] not enough'])
                    ),
                    # else
                    # adjust the products' quantity by subtracting quantity requested
                    # if remaining stock < backorderedLimit, then set backordered = True
                    q.update(q.select('ref', q.var('product')), {
                      'data': {
                        'quantity': q.select(['updatedQuantity'], q.var('product')),
                        'backordered': q.select(['backordered'], q.var('product'))
                      }
                    })
                  )
                ),
                q.var('products')
              ),
              q.let(
                {
                  'orderProducts': q.map_(
                    q.lambda_('product', {
                      'product': q.select('ref', q.var('product')),
                      'quantity': q.select('requestedQuantity', q.var('product')),
                      'price': q.select('price', q.var('product'))
                    }),
                    q.var('products')
                  ),
                  'result': q.create(q.collection('order'), {
                      'data': {
                        'orderName': payload.orderName,
                        'creationDate': q.time('now'),
                        'status': 'processing',
                        'orderProducts': q.var('orderProducts')
                      }
                    })
                },
                {
                  'id': q.select(['ref', 'id'], q.var('result')),
                  'creationDate': q.to_string(q.select(['data', 'creationDate'], q.var('result')))
                }
              )
            )
          )
        )
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('PutItem succeeded:')
        order = Order(response['id'], payload.orderName, response['creationDate'], 'processing', payload.orderProducts)
        return order

def update_order(event, payload, orderId):
    
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.let(
            {
              'update': q.update(
                q.ref(q.collection('order'), orderId), {
                  'data': {
                    'orderName': payload.orderName,
                    'status': payload.orderStatus,
                    'orderProducts': _format_order_products(payload.orderProducts)
                  }
                }
              )
            },
            {
              'id': orderId,
              'status': q.select(['data', 'status'], q.var('update')),
              'creationDate': q.to_string(q.select(['data', 'creationDate'], q.var('update')))
            }
          )
        )
        order = Order(orderId, payload.orderName, response['creationDate'], response['status'], payload.orderProducts)
    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('UpdateItem succeeded:')
        return order

def get_orders(event):
    orders = []

    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        results = db.query(
          q.map_(
            q.lambda_('x', 
              q.let(
                {
                  'order': q.get(q.var('x')),
                  'orderProducts': q.map_(
                    q.lambda_(
                      'x',
                      q.let(
                        { 'product': q.get(q.select(['product'], q.var('x'))) },
                        {
                          'quantity': q.select(['quantity'], q.var('x')),
                          'price': q.select(['price'], q.var('x')),
                          'productId': q.select(['ref', 'id'], q.var('product')),
                          'productName': q.select(['data', 'name'], q.var('product'), ''),
                          'productSku': q.select(['data', 'sku'], q.var('product'), ''),
                          'productDescription': q.select(['data', 'description'], q.var('product'), '')
                        }
                      )
                    ),
                    q.select(['data', 'orderProducts'], q.var('order'))
                  )
                },
                q.merge(
                  q.select(['data'], q.var('order')),
                  {
                    'orderId': q.select(['ref', 'id'], q.var('order')),
                    'creationDate': q.to_string(q.select(['data', 'creationDate'], q.var('order'))),
                    'orderProducts': q.var('orderProducts')
                  },
                )
              )
            ),
            q.paginate(q.documents(q.collection('order')))
          )
        )
        results = results['data']
        for item in results:
            order = Order(item['orderId'], item['orderName'], item['creationDate'], item['status'], item['orderProducts'])
            orders.append(order)

    except FaunaError as e:
        logger.error(e)
        raise e
    else:
        logger.info('Get orders succeeded')
        return orders


def _format_order_products(orderProducts):
    print('orderProducts: {}'.format(orderProducts))
    orderProductList = []
    for i in range(len(orderProducts)):
        product = {
          'product': q.ref(q.collection('product'), orderProducts[i].productId),
          'price': orderProducts[i].price,
          'quantity': orderProducts[i].quantity
        }
        orderProductList.append(product)
    return orderProductList    

  

