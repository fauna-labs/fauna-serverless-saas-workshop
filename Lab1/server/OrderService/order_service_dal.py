# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from botocore.exceptions import ClientError
from order_models import Order
import logger

from utils import Fauna, load_config
from faunadb.query import get, ref, collection, map_, lambda_, let, select, var, merge, to_string, delete, create, update, \
  lt, do, foreach, if_, abort, concat, subtract, time, paginate, documents
from faunadb.errors import FaunaError
db = None

def get_order(event, orderId):
    
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        item = db.query(
          let(
            {
              'order': get(ref(collection('order'), orderId)),
              'orderProducts': map_(
                lambda_(
                  'x',
                  let(
                    { 'product': get(select(['product'], var('x'))) },
                    {
                      'quantity': select(['quantity'], var('x')),
                      'price': select(['price'], var('x')),
                      'productId': select(['ref', 'id'], var('product')),
                      'productName': select(['data', 'name'], var('product'), ''),
                      'productSku': select(['data', 'sku'], var('product'), ''),
                      'productDescription': select(['data', 'description'], var('product'), '')
                    }
                  )
                ),
                select(['data', 'orderProducts'], var('order'))
              )
            },
            merge(
              select(['data'], var('order')),
              {
                'orderId': select(['ref', 'id'], var('order')),
                'creationDate': to_string(select(['data', 'creationDate'], var('order'))),
                'orderProducts': var('orderProducts')
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
          select(
            ['ref', 'id'],
            delete(
              ref(collection('order'), orderId)
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
          let(
            {
              'products': map_(
                lambda_(
                  'requestedProduct',
                  let(
                    {
                      'requestedQuantity': select(['quantity'], var('requestedProduct')),
                      'product': get(select(['product'], var('requestedProduct'))),
                      'currentQuantity': select(['data', 'quantity'], var('product')),
                      'backorderedLimit': select(['data', 'backorderedLimit'], var('product')),
                      'updatedQuantity': subtract(var('currentQuantity'), var('requestedQuantity')),
                    },
                    {
                      'ref': select('ref', var('product')),
                      'price': select(['data', 'price'], var('product')),
                      'name': select(['data', 'name'], var('product')),
                      'requestedQuantity': var('requestedQuantity'),
                      'updatedQuantity': var('updatedQuantity'),
                      'backorderedLimit': var('backorderedLimit'),
                      'backordered': lt(var('updatedQuantity'), var('backorderedLimit')) # if remaining stock < backorderedLimit, then backordered = True
                    }
                  )
                ),
                _format_order_products(payload.orderProducts)
              )
            },
            do(
              # for each product, check if stocked quantity is sufficient to fulfill the order
              foreach(
                lambda_(
                  'product',
                  if_(
                    lt(select(['updatedQuantity'], var('product')), 0), # if updatedQuantity < 0 then abort
                    abort(
                      concat(['Stock quantity for Product [', select(['name'], var('product')), '] not enough'])
                    ),
                    # else
                    # adjust the products' quantity by subtracting quantity requested
                    # if remaining stock < backorderedLimit, then set backordered = True
                    update(select('ref', var('product')), {
                      'data': {
                        'quantity': select(['updatedQuantity'], var('product')),
                        'backordered': select(['backordered'], var('product'))
                      }
                    })
                  )
                ),
                var('products')
              ),
              let(
                {
                  'orderProducts': map_(
                    lambda_('product', {
                      'product': select('ref', var('product')),
                      'quantity': select('requestedQuantity', var('product')),
                      'price': select('price', var('product'))
                    }),
                    var('products')
                  ),
                  'result': create(collection('order'), {
                      'data': {
                        'orderName': payload.orderName,
                        'creationDate': time('now'),
                        'status': 'processing',
                        'orderProducts': var('orderProducts')
                      }
                    })
                },
                {
                  'id': select(['ref', 'id'], var('result')),
                  'creationDate': to_string(select(['data', 'creationDate'], var('result')))
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
          let(
            {
              'update': update(
                ref(collection('order'), orderId), {
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
              'status': select(['data', 'status'], var('update')),
              'creationDate': to_string(select(['data', 'creationDate'], var('update')))
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
          map_(
            lambda_('x', 
              let(
                {
                  'order': get(var('x')),
                  'orderProducts': map_(
                    lambda_(
                      'x',
                      let(
                        { 'product': get(select(['product'], var('x'))) },
                        {
                          'quantity': select(['quantity'], var('x')),
                          'price': select(['price'], var('x')),
                          'productId': select(['ref', 'id'], var('product')),
                          'productName': select(['data', 'name'], var('product'), ''),
                          'productSku': select(['data', 'sku'], var('product'), ''),
                          'productDescription': select(['data', 'description'], var('product'), '')
                        }
                      )
                    ),
                    select(['data', 'orderProducts'], var('order'))
                  )
                },
                merge(
                  select(['data'], var('order')),
                  {
                    'orderId': select(['ref', 'id'], var('order')),
                    'creationDate': to_string(select(['data', 'creationDate'], var('order'))),
                    'orderProducts': var('orderProducts')
                  },
                )
              )
            ),
            paginate(documents(collection('order')))
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
          'product': ref(collection('product'), orderProducts[i].productId),
          'price': orderProducts[i].price,
          'quantity': orderProducts[i].quantity
        }
        orderProductList.append(product)
    return orderProductList    

  

