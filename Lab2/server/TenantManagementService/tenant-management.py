# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import utils
import logger
import requests

from utils import FaunaClients
from fauna import fql
from fauna.errors import FaunaException

clients = {}

region = os.environ['AWS_REGION']

#This method has been locked down to be only called from tenant registration service
def create_tenant(event, context):
    tenant_details = json.loads(event['body'])

    try:
        global clients
        db = FaunaClients(clients)

        response = db.query(
            fql("""
            // create tenant entry
            let t = tenant.create({
              tenantName : ${tenantName},
              tenantAddress: ${tenantAddress},
              tenantEmail: ${tenantEmail},
              tenantPhone: ${tenantPhone},
              tenantTier: ${tenantTier},
              isActive: ${isActive}         
            }) {
              id
            }

            // create child database
            Database.create({
              name: "tenant_" + t.id
            })

            // return the tenant id in the response
            {
              id: t.id
            }
            """,
            tenantName=tenant_details['tenantName'],
            tenantAddress=tenant_details['tenantAddress'],
            tenantEmail=tenant_details['tenantEmail'],
            tenantPhone=tenant_details['tenantPhone'],
            tenantTier=tenant_details['tenantTier'],
            isActive=True
            )
        )
        tenant = response.data
        __create_tenantdb_resources(tenant["id"])

    except FaunaException as e:
        logger.error(e)
        raise Exception('Error creating a new tenant', e)
    else:
        return utils.generate_response(tenant)


def get_tenants(event, context):
    tenants = []
    try:
        global clients
        db = FaunaClients(clients)
        results = db.query(
            fql("""
            tenant.all() {
              id,
              tenantName,
              tenantAddress,
              tenantEmail,
              tenantPhone,
              tenantTier,
              isActive
            }
            """)
        )
        tenants = results.data['data']
    except FaunaException as e:
        logger.error(e)
        raise Exception('Error getting all tenants', e)
    else:
        return utils.generate_response(tenants)


def update_tenant(event, context):
    
    tenant_details = json.loads(event['body'])
    tenant_id = event['pathParameters']['tenantid']
    logger.info("Request received to update tenant")        

    global clients
    db = FaunaClients(clients)

    response_update = db.query(
        fql("""
        tenant.byId(${tenant_id}).update({
          tenantName: ${tenantName},
          tenantAddress: ${tenantAddress},
          tenantEmail: ${tenantEmail},
          tenantPhone: ${tenantPhone},
          tenantTier: ${tenantTier}        
        })
        """,
        tenant_id=tenant_id,
        tenantName=tenant_details['tenantName'],
        tenantAddress=tenant_details['tenantAddress'],
        tenantEmail=tenant_details['tenantEmail'],
        tenantPhone=tenant_details['tenantPhone'],
        tenantTier=tenant_details['tenantTier']
        )
    )
    logger.info(response_update)     

    logger.info("Request completed to update tenant")
    return utils.create_success_response("Tenant Updated")    


# TODO: Implement the below method
def get_tenant(event, context):
    tenant_id = event['pathParameters']['tenantid']    
    logger.info("Request received to get tenant details")

    global clients
    db = FaunaClients(clients)

    response = db.query(
        fql("""
        tenant.byId(${tenant_id}) {
          id,
          tenantName,
          tenantAddress,
          tenantEmail,
          tenantPhone
        }
        """,
        tenant_id=tenant_id)
    )
    item = response.data
    tenant_info = TenantInfo(item['tenantName'], 
                             item['tenantAddress'],
                             item['tenantEmail'], 
                             item['tenantPhone'])
    logger.info(tenant_info)    
    logger.info("Request completed to get tenant details")
    return utils.create_success_response(tenant_info.__dict__)


def deactivate_tenant(event, context):
    url_disable_users = os.environ['DISABLE_USERS_BY_TENANT']
    stage_name = event['requestContext']['stage']
    host = event['headers']['Host']
    auth = utils.get_auth(host, region)
    headers = utils.get_headers(event)

    tenant_id = event['pathParameters']['tenantid']
    
    logger.info("Request received to deactivate tenant")

    global clients
    db = FaunaClients(clients)

    response = db.query(
        fql("""
        tenant.byId(${tenant_id}).update({
          active: ${active}
        })
        """,
        tenant_id=tenant_id,
        active=False)
    )               
    logger.info(response)

    update_user_response = __invoke_disable_users(headers, auth, host, stage_name, url_disable_users, tenant_id)
    logger.info(update_user_response)

    logger.info("Request completed to deactivate tenant")
    return utils.create_success_response("Tenant Deactivated")


def activate_tenant(event, context):
    url_enable_users = os.environ['ENABLE_USERS_BY_TENANT']
    stage_name = event['requestContext']['stage']
    host = event['headers']['Host']
    auth = utils.get_auth(host, region)
    headers = utils.get_headers(event)

    tenant_id = event['pathParameters']['tenantid']
    
    logger.info("Request received to activate tenant")
       
    global clients
    db = FaunaClients(clients)

    response = db.query(
        fql("""
        tenant.byId(${tenant_id}).update({
          active: ${active}
        })
        """,
        tenant_id=tenant_id,
        active=True)
    )    
    logger.info(response)

    update_user_response = __invoke_enable_users(headers, auth, host, stage_name, url_enable_users, tenant_id)
    logger.info(update_user_response)

    logger.info("Request completed to activate tenant")
    return utils.create_success_response("Tenant activated")
    

def __invoke_disable_users(headers, auth, host, stage_name, invoke_url, tenant_id):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url, '/', tenant_id])
        response = requests.put(url, auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while disabling users for the tenant')     
        
    except Exception as e:
        logger.error('Error occured while disabling users for the tenant')
        raise Exception('Error occured while disabling users for the tenant', e) 
    else:
        return "Success invoking disable users"


def __invoke_enable_users(headers, auth, host, stage_name, invoke_url, tenant_id):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url, '/', tenant_id])
        response = requests.put(url, auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while enabling users for the tenant')     
        
    except Exception as e:
        logger.error('Error occured while enabling users for the tenant')
        raise Exception('Error occured while enabling users for the tenant', e) 
    else:
        return "Success invoking enable users"


def __create_tenantdb_resources(tenant_id):
    global clients
    db = FaunaClients(clients, tenant_id)
    result = db.query(
        fql("""
        Collection.create({ name: 'order' })
        Collection.create({ name: 'product' })
        """)
    )


class TenantInfo:
    def __init__(self, tenant_name, tenant_address, tenant_email, tenant_phone):
        self.tenant_name = tenant_name
        self.tenant_address = tenant_address
        self.tenant_email = tenant_email
        self.tenant_phone = tenant_phone

   