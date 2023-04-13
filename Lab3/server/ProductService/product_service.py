# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import utils
import logger
import metrics_manager
from aws_lambda_powertools import Tracer
from types import SimpleNamespace
tracer = Tracer()

from utils import FaunaClients
from fauna import fql

clients = {}


@tracer.capture_lambda_handler
def get_product(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)
    
    logger.log_with_tenant_context(event, "Request received to get a product")
    params = event['pathParameters']
    logger.log_with_tenant_context(event, params)
    productId = params['id']
    logger.log_with_tenant_context(event, productId)
    try:
        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
            fql("""
            product.byId(${productId}) {
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

        logger.log_with_tenant_context(event, "Request completed to get a product")
        metrics_manager.record_metric(event, "SingleProductRequested", "Count", 1)
        product = response.data
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def create_product(event, context):    
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)

    logger.log_with_tenant_context(event, "Request received to create a product")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    try:
        global clients
        db = FaunaClients(clients, tenantId)

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
              sku,
              name,
              description,
              price,
              quantity,
              backorderedLimit,
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
        logger.log_with_tenant_context(event, "Request completed to create a product")
        metrics_manager.record_metric(event, "ProductCreated", "Count", 1)
        product = response.data
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def update_product(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)

    logger.log_with_tenant_context(event, "Request received to update a product")
    payload = json.loads(event['body'], object_hook=lambda d: SimpleNamespace(**d))
    params = event['pathParameters']
    productId = params['id']
    try:
        global clients
        db = FaunaClients(clients, tenantId)

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
              sku,
              name,
              description,
              price,
              quantity,
              backorderedLimit,
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
        logger.log_with_tenant_context(event, "Request completed to update a product") 
        metrics_manager.record_metric(event, "ProductUpdated", "Count", 1)   
        product = response.data
        return utils.generate_response(product)
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def delete_product(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)

    logger.log_with_tenant_context(event, "Request received to delete a product")
    params = event['pathParameters']
    productId = params['id']
    try:
        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
            fql("""
            product.byId(${productId}).delete()
            """, 
            productId = productId
            )
        )            
        logger.log_with_tenant_context(event, "Request completed to delete a product")
        metrics_manager.record_metric(event, "ProductDeleted", "Count", 1)
        return utils.create_success_response("Successfully deleted the product")
    except Exception as e:
        return utils.generate_error_response(e)


@tracer.capture_lambda_handler
def get_products(event, context):
    tenantId = event['requestContext']['authorizer']['tenantId']
    tracer.put_annotation(key="TenantId", value=tenantId)
    
    logger.log_with_tenant_context(event, "Request received to get all products")
    try:
        global clients
        db = FaunaClients(clients, tenantId)

        response = db.query(
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
        results = response.data['data']        
        metrics_manager.record_metric(event, "ProductsRetrieved", "Count", len(results))
        logger.log_with_tenant_context(event, "Request completed to get all products")
        return utils.generate_response(results)
    except Exception as e:
        return utils.generate_error_response(e)

  