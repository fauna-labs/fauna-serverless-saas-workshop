# Copyright Fauna, Inc.
# SPDX-License-Identifier: MIT-0

import json
import utils
import logger
import metrics_manager
from aws_lambda_powertools import Tracer
tracer = Tracer()

from utils import FaunaClients
from fauna import fql

clients = {}


@tracer.capture_lambda_handler
def get_order(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)

    logger.log_with_tenant_context(event, "Request received to get a order")
    params = event['pathParameters']
    orderId = params['id']
    logger.log_with_tenant_context(event, params)
    try:
        global clients
        db = FaunaClients(clients, tenantId)

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
        logger.log_with_tenant_context(event, "Request completed to get a order")
        metrics_manager.record_metric(event, "SingleOrderRequested", "Count", 1)
        order = response.data
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def create_order(event, context):  
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)

    logger.log_with_tenant_context(event, "Request received to create a order")
    payload = json.loads(event['body'])
    try:
        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
            fql("""
              ${cart}.forEach(x=>{              
                let p = product.byId(x.productId)
                let updatedQty = p.quantity - x.quantity

                if (updatedQty < 0) {                  
                  abort("Insufficient stock for product " + p.name + 
                        ": Requested quantity=" + x.quantity)
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
            cart=payload['orderProducts'],
            orderName=payload['orderName']
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
        logger.log_with_tenant_context(event, "Request completed to create a order")
        metrics_manager.record_metric(event, "OrderCreated", "Count", 1)
        order = response.data
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def update_order(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)
    
    logger.log_with_tenant_context(event, "Request received to update a order")
    payload = json.loads(event['body'])
    params = event['pathParameters']
    orderId = params['id']
    try:
        global clients
        db = FaunaClients(clients, tenantId)

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
            orderName=payload['orderName'],
            orderStatus=payload['orderStatus'],
            cart=payload['orderProducts']
          )
        )        
        logger.log_with_tenant_context(event, "Request completed to update a order") 
        metrics_manager.record_metric(event, "OrderUpdated", "Count", 1)   
        order = response.data
        return utils.generate_response(order)
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def delete_order(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)

    logger.log_with_tenant_context(event, "Request received to delete a order")
    params = event['pathParameters']
    orderId = params['id']
    try:
        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
            fql("""
            order.byId(${orderId}).delete()
            """, 
            orderId = orderId
            )
        )
        logger.log_with_tenant_context(event, "Request completed to delete a order")
        metrics_manager.record_metric(event, "OrderDeleted", "Count", 1)
        return utils.create_success_response("Successfully deleted the order")
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def get_orders(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)
    
    logger.log_with_tenant_context(event, "Request received to get all orders")
    try:
        global clients
        db = FaunaClients(clients, tenantId)

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
        results = response.data.data
        metrics_manager.record_metric(event, "OrdersRetrieved", "Count", len(results))
        logger.log_with_tenant_context(event, "Request completed to get all orders")
        return utils.generate_response(results)
    except Exception as e:
        return utils.generate_error_response(e)
