# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import utils
import logger
from types import SimpleNamespace

from utils import Fauna, load_config
from fauna import fql

db = None


def get_order(event, context):
    logger.info("Request received to get a order")
    params = event['pathParameters']
    orderId = params['id']
    try:
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
            fql("""
            let o = order.byId(${orderId}) 
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
            """,
            orderId=orderId
            )
        )
        logger.info("Request completed to get a order")
        order = response.data
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)        


def create_order(event, context):  
    logger.info("Request received to create a order")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
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
                orderName,
                creationDate,
                status,
                orderProducts
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
        logger.info("Request completed to create a order")
        order = response.data
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


def update_order(event, context):    
    logger.info("Request received to update a order")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    params = event['pathParameters']
    orderId = params['id']
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
                orderName,
                status,
                creationDate,
                orderProducts
              }
            """,
            orderId=orderId,
            orderName=payload.orderName,
            orderStatus=payload.orderStatus,
            cart=_format_order_products(payload.orderProducts)
          )
        )        
        logger.info("Request completed to update a order")
        order = response.data  
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


def delete_order(event, context):
    logger.info("Request received to delete a order")
    params = event['pathParameters']
    orderId = params['id']
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
        logger.info("Request completed to delete a order")
        return utils.create_success_response("Successfully deleted the order")
    except Exception as e:
        return utils.generate_error_response(e)


def get_orders(event, context):
    logger.info("Request received to get all orders")
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
        logger.info("Request completed to get all orders")
        orders = response.data['data']
        return utils.generate_response(orders)
    except Exception as e:
        return utils.generate_error_response(e)


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