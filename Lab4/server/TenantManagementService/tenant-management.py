# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import utils
import logger
import requests
import auth_manager

from aws_lambda_powertools import Tracer
tracer = Tracer()

from utils import FaunaClients
from faunadb import query as q
from faunadb.errors import FaunaError, BadRequest, Unauthorized, NotFound
clients = {}


region = os.environ['AWS_REGION']

#This method has been locked down to be only called from tenant registration service
def create_tenant(event, context):
    tenant_details = json.loads(event['body'])

    try:
        global clients
        db = FaunaClients(clients)

        tenant = db.query(
          q.let(
            {
              "tenant": q.create(
                  q.collection("tenant"), {
                    "data": {
                      'tenantName' : tenant_details['tenantName'],
                      'tenantAddress': tenant_details['tenantAddress'],
                      'tenantEmail': tenant_details['tenantEmail'],
                      'tenantPhone': tenant_details['tenantPhone'],
                      'tenantTier': tenant_details['tenantTier'],                    
                      'isActive': True
                    }
                  }
                ),
              "tenantId": q.select(["ref", "id"], q.var("tenant")),
              "db": q.create_database({ "name": q.concat(["tenant_", q.var("tenantId")]) })
            },
            { "tenantId": q.var("tenantId") }
          )
        )
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error adding a new tenant', e)
    else:
        return utils.generate_response(tenant)

def get_tenants(event, context):    
    tenants = []
    try:
        global clients
        db = FaunaClients(clients)

        results = db.query(
          q.map_(
            q.lambda_("x", 
              q.let(
                { "tenant": q.get(q.var("x")) },
                q.merge(
                  { "tenantId": q.select(["ref", "id"], q.var("tenant")) },
                  q.select(["data"], q.var("tenant"))
                )
              )
            ),
            q.paginate(q.documents(q.collection("tenant")))
          )
        )
        tenants = results['data']
    except FaunaError as e:
        logger.error(e)
        raise Exception('Error getting all tenants', e)
    else:
        return utils.generate_response(tenants)


@tracer.capture_lambda_handler
def update_tenant(event, context):
    
    requesting_tenant_id = event['requestContext']['authorizer']['tenantId']    
    user_role = event['requestContext']['authorizer']['userRole']

    tenant_details = json.loads(event['body'])
    tenant_id = event['pathParameters']['tenantid']
    
    tracer.put_annotation(key="TenantId", value=tenant_id)
    
    logger.log_with_tenant_context(event, "Request received to update tenant")
    
    if ((auth_manager.isTenantAdmin(user_role) and tenant_id == requesting_tenant_id) or auth_manager.isSystemAdmin(user_role)):
        global clients
        db = FaunaClients(clients)

        response_update = db.query(
          q.update(
            q.ref(q.collection("tenant"), tenant_id), {
              "data": {
                  'tenantName' : tenant_details['tenantName'],
                  'tenantAddress': tenant_details['tenantAddress'],
                  'tenantEmail': tenant_details['tenantEmail'],
                  'tenantPhone': tenant_details['tenantPhone'],
                  'tenantTier': tenant_details['tenantTier']
              }
            }
          )
        )            
        
        logger.log_with_tenant_context(event, response_update)     

        logger.log_with_tenant_context(event, "Request completed to update tenant")
        return utils.create_success_response("Tenant Updated")
    else:
        logger.log_with_tenant_context(event, "Request completed as unauthorized. Only tenant admin or system admin can update tenant!")        
        return utils.create_unauthorized_response()

@tracer.capture_lambda_handler
def get_tenant(event, context):
    requesting_tenant_id = event['requestContext']['authorizer']['tenantId']    
    user_role = event['requestContext']['authorizer']['userRole']
    tenant_id = event['pathParameters']['tenantid']    
    
    tracer.put_annotation(key="TenantId", value=tenant_id)
    
    logger.log_with_tenant_context(event, "Request received to get tenant details")
    
    if ((auth_manager.isTenantAdmin(user_role) and tenant_id == requesting_tenant_id) or auth_manager.isSystemAdmin(user_role)):
        global clients
        db = FaunaClients(clients)

        item = db.query(
          q.let(
            { "tenant": q.get(q.ref(q.collection("tenant"), tenant_id)) },
            q.merge(
              q.select(["data"], q.var("tenant")),
              { "tenantId":  q.select(["ref", "id"], q.var("tenant")) }
            )
          )
        )
        tenant_info = TenantInfo(item['tenantName'], item['tenantAddress'],item['tenantEmail'], item['tenantPhone'])        
        logger.log_with_tenant_context(event, tenant_info)
        
        logger.log_with_tenant_context(event, "Request completed to get tenant details")
        return utils.create_success_response(tenant_info.__dict__)
    else:
        logger.log_with_tenant_context(event, "Request completed as unauthorized. Only tenant admin or system admin can deactivate tenant!")        
        return utils.create_unauthorized_response()  

@tracer.capture_lambda_handler
def deactivate_tenant(event, context):
    
    url_disable_users = os.environ['DISABLE_USERS_BY_TENANT']
    stage_name = event['requestContext']['stage']
    host = event['headers']['Host']
    auth = utils.get_auth(host, region)
    headers = utils.get_headers(event)

    requesting_tenant_id = event['requestContext']['authorizer']['tenantId']    
    user_role = event['requestContext']['authorizer']['userRole']
    tenant_id = event['pathParameters']['tenantid']
    
    tracer.put_annotation(key="TenantId", value=tenant_id)    
    logger.log_with_tenant_context(event, "Request received to deactivate tenant")

    if ((auth_manager.isTenantAdmin(user_role) and tenant_id == requesting_tenant_id) or auth_manager.isSystemAdmin(user_role)):
        global clients
        db = FaunaClients(clients)

        response = db.query(
          q.update(
            q.get(q.ref(q.collection("tenant"), tenant_id)),
            { "data": { "active": False } }
          )
        )                  
        logger.log_with_tenant_context(event, response)

        update_details = {}
        update_details['tenantId'] = tenant_id
        update_details['requestingTenantId'] = requesting_tenant_id
        update_details['userRole'] = user_role
        update_user_response = __invoke_disable_users(update_details, headers, auth, host, stage_name, url_disable_users)
        logger.log_with_tenant_context(event, update_user_response)

        logger.log_with_tenant_context(event, "Request completed to deactivate tenant")
        return utils.create_success_response("Tenant Deactivated")
    else:
        logger.log_with_tenant_context(event, "Request completed as unauthorized. Only tenant admin or system admin can deactivate tenant!")        
        return utils.create_unauthorized_response()  

@tracer.capture_lambda_handler
def activate_tenant(event, context):
    url_enable_users = os.environ['ENABLE_USERS_BY_TENANT']
    stage_name = event['requestContext']['stage']
    host = event['headers']['Host']
    auth = utils.get_auth(host, region)
    headers = utils.get_headers(event)

    requesting_tenant_id = event['requestContext']['authorizer']['tenantId']    
    user_role = event['requestContext']['authorizer']['userRole']

    tenant_id = event['pathParameters']['tenantid']
    tracer.put_annotation(key="TenantId", value=tenant_id)
    
    logger.log_with_tenant_context(event, "Request received to activate tenant")

    if (auth_manager.isSystemAdmin(user_role)):
        global clients
        db = FaunaClients(clients)

        response = db.query(
          q.update(
            q.get(q.ref(q.collection("tenant"), tenant_id)),
            { "data": { "active": True } }
          )
        )           
        logger.log_with_tenant_context(event, response)

        update_details = {}
        update_details['tenantId'] = tenant_id
        update_details['requestingTenantId'] = requesting_tenant_id
        update_details['userRole'] = user_role
        update_user_response = __invoke_enable_users(update_details, headers, auth, host, stage_name, url_enable_users)
        logger.log_with_tenant_context(event, update_user_response)

        logger.log_with_tenant_context(event, "Request completed to activate tenant")
        return utils.create_success_response("Tenant Activated")
    else:
        logger.log_with_tenant_context(event, "Request completed as unauthorized. Only system admin can activate tenant!")        
        return utils.create_unauthorized_response()   
    
def __invoke_disable_users(update_details, headers, auth, host, stage_name, invoke_url):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url, '/'])
        response = requests.put(url, data=json.dumps(update_details), auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while disabling users for the tenant')     
        
    except Exception as e:
        logger.error('Error occured while disabling users for the tenant')
        raise Exception('Error occured while disabling users for the tenant', e) 
    else:
        return "Success invoking disable users"

def __invoke_enable_users(update_details, headers, auth, host, stage_name, invoke_url):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url, '/'])
        response = requests.put(url, data=json.dumps(update_details), auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while enabling users for the tenant')     
        
    except Exception as e:
        logger.error('Error occured while enabling users for the tenant')
        raise Exception('Error occured while enabling users for the tenant', e) 
    else:
        return "Success invoking enable users"


class TenantInfo:
    def __init__(self, tenant_name, tenant_address, tenant_email, tenant_phone):
        self.tenant_name = tenant_name
        self.tenant_address = tenant_address
        self.tenant_email = tenant_email
        self.tenant_phone = tenant_phone

   