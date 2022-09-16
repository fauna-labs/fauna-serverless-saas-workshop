# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import jsonpickle
import simplejson

import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth
from enum import Enum

import os, configparser, traceback
from faunadb.client import FaunaClient
from faunadb import query as q

FAUNA_CONFIG_PATH = os.environ['FAUNA_CONFIG_PATH']
boto_client = boto3.client('ssm')

class FaunaFromConfig(FaunaClient):
    def __init__(self):
        config = load_config()
        print("Loading config and creating new Fauna client...")
        print("Fauna domain = {}".format(config['FAUNA']['domain']))
        
        self.domain = config['FAUNA']['domain']
        self.secret = config['FAUNA']['secret']

        FaunaClient.__init__(self,
            domain=self.domain,
            secret=self.secret
        )
        
    def get_domain(self):
        return self.domain

    def get_secret(self):
        return self.secret

def FaunaClients(clients, tenant_id=None):
    if tenant_id is None:
        tenant_id = 'admin'

    if tenant_id in clients:
        print("Client for tenant_id {} found".format(tenant_id))
        return clients[tenant_id]
    else:
        if 'admin' in clients:
            admin_client = clients['admin']
        else:
            admin_client = FaunaFromConfig()
            clients['admin'] = admin_client

        if tenant_id == 'admin':
            client = admin_client
        else:
          try:
            # create_key = admin_client.query(
            #   q.create_key({
            #     "role": "admin",
            #     "database": q.database("tenant_{}".format(tenant_id))
            #   })
            # )
            # print("create_key: {}".format(create_key))
            print("creating client for tenant {}".format(tenant_id))
            client = FaunaClient(
                domain=admin_client.get_domain(),
                # secret=create_key['secret']
                secret="{}:tenant_{}:server".format(admin_client.get_secret(), tenant_id)
            )
            clients[tenant_id] = client
          except Exception as e:
            print("EXCEPTION {}".format(e))
 
        return client

# https://aws.amazon.com/blogs/compute/sharing-secrets-with-aws-lambda-using-aws-systems-manager-parameter-store/
def load_config():
    configuration = configparser.ConfigParser()
    config_dict = {}
    try: 
        print("get_parameters_by_path {}".format(FAUNA_CONFIG_PATH))
        param_details = boto_client.get_parameters_by_path(
            Path=FAUNA_CONFIG_PATH,
            Recursive=False,
            WithDecryption=True
        )
        if 'Parameters' in param_details and len(param_details.get('Parameters')) > 0:
            for param in param_details.get('Parameters'):
                config_dict.update(json.loads(param.get('Value')))
    except:
        print("Encountered an error loading config from SSM.")
        traceback.print_exc()
    finally:
        configuration['FAUNA'] = config_dict
        return configuration

class TenantTier(Enum):
    PLATINUM    = "Platinum"
    PREMIUM     = "Premium"
    STANDARD    = "Standard"
    BASIC       = "Basic"


class StatusCodes(Enum):
    SUCCESS    = 200
    UN_AUTHORIZED  = 401
    NOT_FOUND = 404
    
class Service_Identifier(Enum):
    SHARED_SERVICES     = "SharedServices"
    BUSINESS_SERVICES    = "BusinessServices"

def create_success_response(message):
    return {
        "statusCode": StatusCodes.SUCCESS.value,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type, Origin, X-Requested-With, Accept, Authorization, Access-Control-Allow-Methods, Access-Control-Allow-Headers, Access-Control-Allow-Origin",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
        "body": json.dumps({
            "message": message
        }),
    }

def create_unauthorized_response():
    return {
        "statusCode": StatusCodes.UN_AUTHORIZED.value,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
        "body": json.dumps({
            "message": "User not authorized to perform this action"
        }),
    }

def create_notfound_response(message):
    return {
        "statusCode": StatusCodes.NOT_FOUND.value,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
        "body": json.dumps({
            "message": message
        }),
    }

def get_auth(host, region):
    session = boto3.Session()
    credentials = session.get_credentials()
    auth = AWSRequestsAuth(aws_access_key=credentials.access_key,
                       aws_secret_access_key=credentials.secret_key,
                       aws_token=credentials.token,
                       aws_host=host,
                       aws_region=region,
                       aws_service='execute-api')
    return auth                   

def get_headers(event):
    return event['headers']


def generate_response(inputObject):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type, Origin, X-Requested-With, Accept, Authorization, Access-Control-Allow-Methods, Access-Control-Allow-Headers, Access-Control-Allow-Origin",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
        "body": encode_to_json_object(inputObject),
    }

def  encode_to_json_object(inputObject):
    jsonpickle.set_encoder_options('simplejson', use_decimal=True, sort_keys=True)
    jsonpickle.set_preferred_backend('simplejson')
    return jsonpickle.encode(inputObject, unpicklable=False, use_decimal=True)





