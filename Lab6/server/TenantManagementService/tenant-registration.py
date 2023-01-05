# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import os
import utils
import logger
import requests

region = os.environ['AWS_REGION']
create_tenant_admin_user_resource_path = os.environ['CREATE_TENANT_ADMIN_USER_RESOURCE_PATH']
create_tenant_resource_path = os.environ['CREATE_TENANT_RESOURCE_PATH']
provision_tenant_resource_path = os.environ['PROVISION_TENANT_RESOURCE_PATH']


lambda_client = boto3.client('lambda')


def register_tenant(event, context):
    try:
        tenant_details = json.loads(event['body'])

        if (tenant_details['tenantTier'].upper() == utils.TenantTier.PLATINUM.value.upper()):
            tenant_details['dedicatedTenancy'] = 'true'
        else:
            tenant_details['dedicatedTenancy'] = 'false'

        #TODO: Pass relevant apikey to tenant_details object based upon tenant tier
        tenant_details['apiKey'] = __getApiKey(tenant_details['tenantTier'])

        logger.info(tenant_details)

        stage_name = event['requestContext']['stage']
        host = event['headers']['Host']
        auth = utils.get_auth(host, region)
        headers = utils.get_headers(event)

        # first we create the tenant, and get the tenant_id
        create_tenant_response = __create_or_update_tenant(tenant_details, headers, auth, host, stage_name)
        tenant_details['tenantId'] = create_tenant_response['tenantId']
        logger.info(tenant_details)

        create_user_response = __create_tenant_admin_user(tenant_details, headers, auth, host, stage_name)        
        logger.info (create_user_response)
        tenant_details['userPoolId'] = create_user_response['message']['userPoolId']
        tenant_details['appClientId'] = create_user_response['message']['appClientId']

        # update the tenant with the userPoolId and appClientId
        create_tenant_response = __create_or_update_tenant(tenant_details, headers, auth, host, stage_name)
        logger.info (create_tenant_response)

        provision_tenant_response = __provision_tenant(tenant_details, headers, auth, host, stage_name)
        logger.info(provision_tenant_response)        
    except Exception as e:
        logger.error('Error registering a new tenant')
        raise Exception('Error registering a new tenant', e)
    else:
        return utils.create_success_response("You have been registered in our system")


def __create_tenant_admin_user(tenant_details, headers, auth, host, stage_name):
    try:
        url = ''.join(['https://', host, '/', stage_name, create_tenant_admin_user_resource_path])
        logger.info(url)
        response = requests.post(url, data=json.dumps(tenant_details), auth=auth, headers=headers) 
        response_json = response.json()
    except Exception as e:
        logger.error('Error occured while calling the create tenant admin user service')
        raise Exception('Error occured while calling the create tenant admin user service', e)
    else:
        return response_json


def __create_or_update_tenant(tenant_details, headers, auth, host, stage_name):
    try:
        url = ''.join(['https://', host, '/', stage_name, create_tenant_resource_path])
        response = requests.post(url, data=json.dumps(tenant_details), auth=auth, headers=headers) 
        response_json = response.json()
    except Exception as e:
        logger.error('Error occured while creating the tenant record in table')
        raise Exception('Error occured while creating the tenant record in table', e) 
    else:
        return response_json


def __provision_tenant(tenant_details, headers, auth, host, stage_name):
    try:
        url = ''.join(['https://', host, '/', stage_name, provision_tenant_resource_path])
        logger.info(url)
        response = requests.post(url, data=json.dumps(tenant_details), auth=auth, headers=headers) 
        response_json = response.json()['message']
    except Exception as e:
        logger.error('Error occured while provisioning the tenant')
        raise Exception('Error occured while creating the tenant record in table', e) 
    else:
        return response_json

              
def __getApiKey(tenant_tier):
    if (tenant_tier.upper() == utils.TenantTier.PLATINUM.value.upper()):
        return os.environ['PLATINUM_TIER_API_KEY']
    elif (tenant_tier.upper() == utils.TenantTier.PREMIUM.value.upper()):
        return os.environ['PREMIUM_TIER_API_KEY']
    elif (tenant_tier.upper() == utils.TenantTier.STANDARD.value.upper()):
        return os.environ['STANDARD_TIER_API_KEY']
    elif (tenant_tier.upper() == utils.TenantTier.BASIC.value.upper()):
        return os.environ['BASIC_TIER_API_KEY']