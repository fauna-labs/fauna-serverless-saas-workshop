# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# import os
# import boto3
from botocore.exceptions import ClientError
import uuid
from order_models import Order
# import json
# import utils
# from types import SimpleNamespace
import logger
# import random

from utils import Fauna, load_config
from faunadb import query as q
from faunadb.errors import FaunaError, BadRequest, Unauthorized, NotFound
db = None

# table_name = os.environ['ORDER_TABLE_NAME']
# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(table_name)

def get_order(event, orderId):
    
    try:
        # response = table.get_item(Key={'orderId': orderId})
        # item = response['Item']

        global db
        if db is None:
            db = Fauna.from_config(load_config())

        item = db.query(
          q.let(
            {
              "order": q.get(q.ref(q.collection("order"), orderId)),
              "orderProducts": q.map_(
                q.lambda_(
                  "x",
                  {
                    "quantity": q.select(["quantity"], q.var("x")),
                    "price": q.select(["price"], q.var("x")),
                    "key": q.select(["data", "name"], q.get(q.select(["product"], q.var("x"))))
                  }
                ),
                q.select(["data", "orderProducts"], q.var("order"))
              )
            },
            {
              "orderId": q.select(["ref", "id"], q.var("order")),
              "orderName": q.select(["data", "orderName"], q.var("order")),
              "orderProducts": q.var("orderProducts")
            }
          )
        )
        order = Order(item['orderId'], item['orderName'], item['orderProducts'])

    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error getting a order', e)
    except FaunaError as e:
      logger.error(e)
      raise Exception('Error getting a order', e)
    else:
        return order

def delete_order(event, orderId):

    try:
        # response = table.delete_item(Key={'orderId': orderId})
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.select(
            ["ref", "id"],
            q.delete(
              q.ref(q.collection("order"), orderId)
            )
          )
        )
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error deleting a order', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error deleting a order', e)
    else:
        logger.info("DeleteItem succeeded:")
        return response


def create_order(event, payload):
    
    # order = Order(str(uuid.uuid4()), payload.orderName, payload.orderProducts)
    order = None

    try:
        # response = table.put_item(Item={
        # 'orderId': order.orderId, 
        # 'orderName': order.orderName,
        # 'orderProducts': get_order_products_dict(order.orderProducts)
        # })
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.let(
            {
              "result": q.create(q.collection("order"), {
                    "data": {
                      "orderName": payload.orderName,
                      "orderProducts": _format_order_products(payload.orderProducts)
                    }
                  })
            },
            { "id": q.select(["ref", "id"], q.var("result")) }
          )
        )
        order = Order(response["id"], payload.orderName, payload.orderProducts)
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error adding a order', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error adding a order', e)
    else:
        logger.info("PutItem succeeded:")
        return order

def update_order(event, payload, orderId):
    
    try:
        order = Order(orderId,payload.orderName, payload.orderProducts)

        # response = table.update_item(Key={'orderId': order.orderId},
        #     UpdateExpression="set orderName=:orderName, "
        #     +"orderProducts=:orderProducts",
        #     ExpressionAttributeValues={
        #         ':orderName': order.orderName,
        #         ':orderProducts': get_order_products_dict(order.orderProducts)
        #     },
        #     ReturnValues="UPDATED_NEW")

        global db
        if db is None:
            db = Fauna.from_config(load_config())

        db.query(
          q.update(
            q.ref(q.collection("order"), orderId), {
              "data": {
                "orderName": payload.orderName,
                "orderProducts": _format_order_products(payload.orderProducts)
              }
            }
          )
        )
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error updating a order', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error updating a order', e)
    else:
        logger.info("UpdateItem succeeded:")
        return order

def get_orders(event):
    orders = []

    try:
        # response = table.scan()    
        # if (len(response['Items']) > 0):
        #     for item in response['Items']:
        #         order = Order(item['orderId'], item['orderName'], item['orderProducts'])
        #         orders.append(order)
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        results = db.query(
          q.map_(
            q.lambda_("x", 
              q.let(
                { "order": q.get(q.var("x")) },
                q.merge(
                  { "orderId": q.select(["ref", "id"], q.var("order")) },
                  q.select(["data"], q.var("order"))
                )
              )
            ),
            q.paginate(q.documents(q.collection("order")))
          )
        )
        results = results['data']
        for item in results:
            order = Order(item['orderId'], item['orderName'], item['orderProducts'])
            orders.append(order)

    # except ClientError as e:
    #     logger.error("Error getting all orders")
    #     raise Exception('Error getting all orders', e) 
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error getting all orders', e)
    else:
        logger.info("Get orders succeeded")
        return orders


# def get_order_products_dict(orderProducts):
#     orderProductList = []
#     for i in range(len(orderProducts)):
#         product = orderProducts[i]
#         orderProductList.append(vars(product))
#     return orderProductList    


def _format_order_products(orderProducts):
    print("orderProducts: {}".format(orderProducts))
    orderProductList = []
    for i in range(len(orderProducts)):
        product = {
          "product": q.ref(q.collection("product"), orderProducts[i].productId),
          "price": orderProducts[i].price,
          "quantity": orderProducts[i].quantity
        }
        orderProductList.append(product)
    return orderProductList    

  

