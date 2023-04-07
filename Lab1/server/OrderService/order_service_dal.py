# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from order_models import Order
import logger

from utils import Fauna, load_config
from fauna import fql
from fauna.errors import FaunaException

db = None

def get_order(event, orderId):
    
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            let o = order.byId(${orderId}) 
            let cart = o.orderProducts
            {
              id: o.id,
              orderName: o.orderName,
              creationDate: o.creationDate,
              status: o.status,
              orderProducts: cart.map(x=>{
                price: x.price,
                quantity: x.quantity,
                productId: x.product.id,
                productName: x.product.name,
                productSku: x.product.sku,
                productDescription: x.product.description
              })
            }
            """,
            orderId=orderId
            )
        )
    except FaunaException as e:
        logger.error(e)
        raise e
    else:
        item = response.data        
        order = Order(item['id'], 
                      item['orderName'], 
                      item['creationDate'], 
                      item['status'], 
                      item['orderProducts'])        
        return order


def delete_order(event, orderId):
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            order.byId(${orderId}).delete()
            """, 
            orderId = orderId
            )
        )
    except FaunaException as e:
        logger.error(e)
        raise e
    else:
        logger.info('DeleteItem succeeded:')
        return None


def create_order(event, payload):
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
              ${cart}.forEach(x=>{              
                let p = product.byId(x.productId)
                let updatedQty = p.quantity - x.quantity

                if (updatedQty < 0) {                  
                  abort("Insufficient stock for product " + p.name + ": Requested quantity=" + x.quantity)
                } else {
                  p.update({
                    quantity: updatedQty,
                    backordered: p.backorderedLimit > updatedQty
                  })
                }
              })

              order.create({
                orderName: ${orderName},
                creationDate: Time.now(),
                status: 'processing',
                orderProducts: ${cart}.map(x=>{
                  product: product.byId(x.productId),
                  quantity: x.quantity,
                  price: x.price
                })
              }) {
                id,
                creationDate
              }           
            """,
            cart=_format_order_products(payload.orderProducts),
            orderName=payload.orderName
          )
          # payload has the following shape:
          # {
          #     "orderName": "Example",
          #     "orderProducts":
          #     [
          #         {
          #             "price": "6.27",
          #             "productId": "361199918684045380",
          #             "quantity": 1
          #         },
          #     ]
          # }
        )
    except FaunaException as e:
        logger.error(e)
        raise e
    except Exception as err:
        logger.error(err)
        raise err
    else:
        logger.info('PutItem succeeded:')
        response = response.data
        order = Order(response['id'], 
                      payload.orderName, 
                      response['creationDate'], 
                      'processing', 
                      payload.orderProducts)
        return order


def update_order(event, payload, orderId):
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
              order.byId(${orderId}).update({
                orderName: ${orderName},
                status: ${orderStatus},
                orderProducts: ${cart}.map(x=>{
                  product: product.byId(x.productId),
                  quantity: x.quantity,
                  price: x.price
                })
              }) {
                id,
                status,
                creationDate
              }
            """,
            orderId=orderId,
            orderName=payload.orderName,
            orderStatus=payload.orderStatus,
            cart=_format_order_products(payload.orderProducts)
          )
        )
    except FaunaException as e:
        logger.error(e)
        raise e
    else:
        logger.info('UpdateItem succeeded:')
        response = response.data
        order = Order(orderId, 
                      payload.orderName, 
                      response['creationDate'], 
                      response['status'], 
                      payload.orderProducts)
        return order

def get_orders(event):
    orders = []
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            order.all().map(o=>{
              {
                id: o.id,
                orderName: o.orderName,
                creationDate: o.creationDate,
                status: o.status,
                orderProducts: o.orderProducts.map(x=>{
                  price: x.price,
                  quantity: x.quantity,
                  productId: x.product.id,
                  productName: x.product.name,
                  productSku: x.product.sku,
                  productDescription: x.product.description
                })
              }
            })
            """)
        )
    except FaunaException as e:
        logger.error(e)
        raise e
    else:
        logger.info('Get orders succeeded')
        results = response.data['data']
        for item in results:
            order = Order(item['id'], 
                          item['orderName'], 
                          item['creationDate'], 
                          item['status'], 
                          item['orderProducts'])
            orders.append(order)
        return orders

  
def _format_order_products(orderProducts):
  orderProductList = []
  for i in range(len(orderProducts)):
      product = {
        'productId': orderProducts[i].productId,
        'price': orderProducts[i].price,
        'quantity': orderProducts[i].quantity
      }
      orderProductList.append(product)
  return orderProductList   
