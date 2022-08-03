# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# import os, traceback, configparser, json
# import boto3
# from botocore.exceptions import ClientError
import uuid
import logger

from product_models import Product
# from types import SimpleNamespace
# from boto3.dynamodb.conditions import Key

from utils import Fauna, load_config
from faunadb import query as q
from faunadb.errors import FaunaError, BadRequest, Unauthorized, NotFound

# table_name = os.environ['PRODUCT_TABLE_NAME']
# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(table_name)

db = None

def get_product(event, productId):
    try:
        # response = table.get_item(Key={'productId': productId})
        # item = response['Item']
        # product = Product(item['productId'], item['sku'], item['name'], item['price'], item['category'])

        global db
        if db is None:
            db = Fauna.from_config(load_config())

        item = db.query(
          q.let(
            { "product": q.get(q.ref(q.collection("product"), productId)) },
            q.merge(
              q.select(["data"], q.var("product")),
              { "productId":  q.select(["ref", "id"], q.var("product")) }
            )
          )
        )
        product = Product(item['productId'], item['sku'], item['name'], item['price'], item['category'])
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error getting a product', e)
    except FaunaError as e:
      logger.error(e)
      raise Exception('Error getting a product', e)
    else:
        logger.info("GetItem succeeded:"+ str(product))
        return product

def delete_product(event, productId):
    try:
        # response = table.delete_item(Key={'productId': productId})

        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.select(
            ["ref", "id"],
            q.delete(
              q.ref(q.collection("product"), productId)
            )
          )
        )
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error deleting a product', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error deleting a product', e)
    else:
        logger.info("DeleteItem succeeded:")
        return response


def create_product(event, payload):
    # product = Product(str(uuid.uuid4()), payload.sku,payload.name, payload.price, payload.category)
    product = None
    try:
        # response = table.put_item(
        #     Item=
        #         {
        #             'productId': product.productId,
        #             'sku': product.sku,
        #             'name': product.name,
        #             'price': product.price,
        #             'category': product.category
        #         }
        # )
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        response = db.query(
          q.let(
            {
              "result": q.create(q.collection("product"), {
                    "data": {
                      "sku": payload.sku,
                      "name": payload.name,
                      "price": payload.price,
                      "category": payload.category
                    }
                  })
            },
            { "id": q.select(["ref", "id"], q.var("result")) }
          )
        )
        product = Product(response["id"], payload.sku,payload.name, payload.price, payload.category)
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error adding a product', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error adding a product', e)
    else:
        logger.info("PutItem succeeded:")
        return product

def update_product(event, payload, productId):
    try:
        product = Product(productId,payload.sku, payload.name, payload.price, payload.category)

        # response = table.update_item(Key={'productId': product.productId},
        # UpdateExpression="set sku=:sku, #n=:productName, price=:price, category=:category",
        # ExpressionAttributeNames= {'#n':'name'},
        # ExpressionAttributeValues={
        #     ':sku': product.sku,
        #     ':productName': product.name,
        #     ':price': product.price,
        #     ':category': product.category
        # },
        # ReturnValues="UPDATED_NEW")
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        db.query(
          q.update(
            q.ref(q.collection("product"), productId), {
              "data": {
                "sku": product.sku,
                "name": product.name,
                "price": product.price,
                "category": product.category
              }
            }
          )
        )
    # except ClientError as e:
    #     logger.error(e.response['Error']['Message'])
    #     raise Exception('Error updating a product', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error updating a product', e)
    else:
        logger.info("UpdateItem succeeded:")
        return product        

def get_products(event): 
    products =[]

    try:
        # response = table.scan()    
        # if (len(response['Items']) > 0):
        #     for item in response['Items']:
        #         product = Product(item['productId'], item['sku'], item['name'], item['price'], item['category'])
        #         products.append(product)
        global db
        if db is None:
            db = Fauna.from_config(load_config())

        results = db.query(
          q.map_(
            q.lambda_("x", 
              q.let(
                { "product": q.get(q.var("x")) },
                q.merge(
                  { "productId": q.select(["ref", "id"], q.var("product")) },
                  q.select(["data"], q.var("product"))
                )
              )
            ),
            q.paginate(q.documents(q.collection("product")))
          )
        )
        results = results['data']
        for item in results:
            product = Product(item['productId'], item['sku'], item['name'], item['price'], item['category'])
            products.append(product)

    # except ClientError as e:
        # logger.error(e.response['Error']['Message'])
        # raise Exception('Error getting all products', e)
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error getting all products', e)
    else:
        logger.info("Get products succeeded")
        return products



