# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import boto3
import urllib.parse
import utils
import logger
import auth_manager
import requests

from aws_lambda_powertools import Tracer
tracer = Tracer()

from utils import FaunaClients
from faunadb import query as q
from faunadb.errors import FaunaError, BadRequest, Unauthorized, NotFound
clients = {}

region = os.environ['AWS_REGION']


#This method has been locked down to be only called from tenant registration service
def create_tenant(event, context):
    api_gateway_url = ''       
    tenant_details = json.loads(event['body'])

    dynamodb = boto3.resource('dynamodb')
    settings_table_name = os.environ['SETTINGS_TABLE_NAME']
    table_system_settings = dynamodb.Table(settings_table_name)

    try:          
        # for pooled tenants the apigateway url is saved in settings during stack creation
        # update from there during tenant creation
        if(tenant_details['dedicatedTenancy'].lower()!= 'true'):
            settings_response = table_system_settings.get_item(
                Key={
                    'settingName': 'apiGatewayUrl-Pooled'
                } 
            )
            api_gateway_url = settings_response['Item']['settingValue']              

        tenant_id = tenant_details['tenantId'] if 'tenantId' in tenant_details else None
        data = {
          'isActive': True,
          'apiGatewayUrl': api_gateway_url
        }
        for key in tenant_details:
          data[key] = tenant_details[key]

        # Note:
        # 1) This method has been locked down to be only called from tenant registration service
        # 2) Is doing an UPSERT
        global clients
        db = FaunaClients(clients)
        if tenant_id:
            tenant = db.query(
              q.let(
                {
                  'tenant': q.update(q.ref(q.collection('tenant'), tenant_id), { 'data': data } ),
                  'tenantId': q.select(['ref', 'id'], q.var('tenant'), 0)
                },
                { 'tenantId': q.var('tenantId') }
              )
            )            
        else:
            tenant = db.query(
              q.let(
                {
                  'tenant': q.create(q.collection('tenant'), { 'data': data } ),
                  'tenantId': q.select(['ref', 'id'], q.var('tenant'), 0),
                  'db': q.create_database({ 'name': q.concat(['tenant_', q.var('tenantId')]) })
                },
                { 'tenantId': q.var('tenantId') }
              )
            )
    except FaunaError as fe:
        logger.error(fe)
        raise Exception('Error adding a new tenant', fe)
    except Exception as e:
        raise Exception('Error creating a new tenant', e)
    else:
        return utils.generate_response(tenant)


def get_tenants(event, context):
    tenants = []
    try:
        tenant_id = event['requestContext']['authorizer']['tenantId']
        user_role = event['requestContext']['authorizer']['userRole']
        global clients
        db = FaunaClients(clients)

        if auth_manager.isSystemAdmin(user_role):
            results = db.query(
              q.map_(
                q.lambda_('x', 
                  q.let(
                    { 'tenant': q.get(q.var('x')) },
                    q.merge(
                      { 'tenantId': q.select(['ref', 'id'], q.var('tenant')) },
                      q.select(['data'], q.var('tenant'))
                    )
                  )
                ),
                q.paginate(q.documents(q.collection('tenant')))
              )
            )
        else:
            results = db.query(
              q.let(
                { 'tenant': q.get(q.ref(q.collection('tenant'), tenant_id)) },
                q.merge(
                  { 'tenantId': q.select(['ref', 'id'], q.var('tenant')) },
                  q.select(['data'], q.var('tenant'))
                )
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
          q.let(
            {
              'tenantRef': q.ref(q.collection('tenant'), tenant_id),
              'existingTier': q.select(['data', 'tenantTier'], q.get(q.var('tenantRef'))),
              'existingApiKey': q.select(['data', 'apiKey'], q.get(q.var('tenantRef'))),
              'apiKey': q.if_(
                q.equals(tenant_details['tenantTier'], q.var('existingTier')),
                q.var('existingApiKey'),
                __getApiKey(tenant_details['tenantTier'])
              )
            },
            q.update(
              q.var('tenantRef'), {
                'data': {
                    'tenantName' : tenant_details['tenantName'],
                    'tenantAddress': tenant_details['tenantAddress'],
                    'tenantEmail': tenant_details['tenantEmail'],
                    'tenantPhone': tenant_details['tenantPhone'],
                    'tenantTier': tenant_details['tenantTier'],
                    'apiKey': q.var('apiKey')
                }
              }
            )
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
            { 'tenant': q.get(q.ref(q.collection('tenant'), tenant_id)) },
            q.merge(
              q.select(['data'], q.var('tenant')),
              { 'tenantId':  q.select(['ref', 'id'], q.var('tenant')) }
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
    url_deprovision_tenant = os.environ['DEPROVISION_TENANT']
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
            q.get(q.ref(q.collection('tenant'), tenant_id)),
            { 'data': { 'active': False } }
          )
        )                  

        logger.log_with_tenant_context(event, response)

        if (response["Attributes"]["dedicatedTenancy"].upper() == "TRUE"):
            update_details = {}
            update_details['tenantId'] = tenant_id            
            update_user_response = __invoke_deprovision_tenant(update_details, headers, auth, host, stage_name, url_deprovision_tenant)

        
        update_details = {}
        update_details['userPoolId'] = response["Attributes"]['userPoolId']
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
    url_provision_tenant = os.environ['PROVISION_TENANT']
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
            q.get(q.ref(q.collection('tenant'), tenant_id)),
            { 'data': { 'active': True } }
          )
        )        

        logger.log_with_tenant_context(event, response)

        if (response["Attributes"]["dedicatedTenancy"].upper() == "TRUE"):
            update_details = {}
            update_details['tenantId'] = tenant_id            
            provision_response = __invoke_provision_tenant(update_details, headers, auth, host, stage_name, url_provision_tenant)
            logger.log_with_tenant_context(event, provision_response)
        
        update_details = {}
        update_details['userPoolId'] = response["Attributes"]['userPoolId']
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


def load_tenant_config(event, context):
    params = event['pathParameters']
    tenantName = urllib.parse.unquote(params['tenantname'])    
    try:
        global clients
        db = FaunaClients(clients)

        response = db.query(
          q.map_(
            q.lambda_('x', q.select(['data'], q.get(q.var('x')))),
            q.select(['data'], q.paginate(q.match(q.index('tenants_by_name'), tenantName)))  
          )
        )
    except Exception as e:
        raise Exception('Error getting tenant config', e)
    else:
        if len(response) == 0:
            return utils.create_notfound_response("Tenant not found."+
            "Please enter exact tenant name used during tenant registration.")
        else:
            return utils.generate_response(response[0])


def __invoke_disable_users(update_details, headers, auth, host, stage_name, invoke_url):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url])
        response = requests.put(url, data=json.dumps(update_details), auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while disabling users for the tenant')     
        
    except Exception as e:
        logger.error('Error occured while disabling users for the tenant')
        raise Exception('Error occured while disabling users for the tenant', e) 
    else:
        return "Success invoking disable users"


def __invoke_deprovision_tenant(update_details, headers, auth, host, stage_name, invoke_url):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url + update_details['tenantId']])
        response = requests.put(url, data=json.dumps(update_details), auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while deprovisioning tenant')     
        
    except Exception as e:
        logger.error('Error occured while deprovisioning tenant')
        raise Exception('Error occured while deprovisioning tenant', e) 
    else:
        return "Success invoking deprovision tenant"


def __invoke_enable_users(update_details, headers, auth, host, stage_name, invoke_url):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url])
        response = requests.put(url, data=json.dumps(update_details), auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while enabling users for the tenant')     
        
    except Exception as e:
        logger.error('Error occured while enabling users for the tenant')
        raise Exception('Error occured while enabling users for the tenant', e) 
    else:
        return "Success invoking enable users"


def __invoke_provision_tenant(update_details, headers, auth, host, stage_name, invoke_url):
    try:
        url = ''.join(['https://', host, '/', stage_name, invoke_url])
        response = requests.post(url, data=json.dumps(update_details), auth=auth, headers=headers) 
        
        logger.info(response.status_code)
        if (int(response.status_code) != int(utils.StatusCodes.SUCCESS.value)):
            raise Exception('Error occured while provisioning tenant')     
        
    except Exception as e:
        logger.error('Error occured while provisioning tenant')
        raise Exception('Error occured while provisioning tenant', e) 
    else:
        return "Success invoking provision tenant"


def __getApiKey(tenant_tier):
    if (tenant_tier.upper() == utils.TenantTier.PLATINUM.value.upper()):
        return os.environ['PLATINUM_TIER_API_KEY']
    elif (tenant_tier.upper() == utils.TenantTier.PREMIUM.value.upper()):
        return os.environ['PREMIUM_TIER_API_KEY']
    elif (tenant_tier.upper() == utils.TenantTier.STANDARD.value.upper()):
        return os.environ['STANDARD_TIER_API_KEY']
    elif (tenant_tier.upper() == utils.TenantTier.BASIC.value.upper()):
        return os.environ['BASIC_TIER_API_KEY']


class TenantInfo:
    def __init__(self, tenant_name, tenant_address, tenant_email, tenant_phone):
        self.tenant_name = tenant_name
        self.tenant_address = tenant_address
        self.tenant_email = tenant_email
        self.tenant_phone = tenant_phone

   