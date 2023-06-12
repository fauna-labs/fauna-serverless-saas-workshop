# Copyright Fauna, Inc.
# SPDX-License-Identifier: MIT-0

import json
import jsonpickle
import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth
from enum import Enum
import os, configparser, traceback
import logger

from fauna.client import Client as FaunaClient
from fauna.errors import FaunaException, FaunaError, AuthenticationError, AuthorizationError, QueryRuntimeError


FAUNA_CONFIG_PATH = os.environ['FAUNA_CONFIG_PATH']
boto_client = boto3.client('ssm')


class Fauna(FaunaClient):    
    @classmethod
    def from_config(cls, tenant_id=None):
        config = _load_config()
        if tenant_id is None:
            logger.info("Loading config and creating new db.")
            return cls(secret=config['FAUNA']['secret'])
        else:
            logger.info("Loading config and creating new db. tenant_id={}".format(tenant_id))
            return cls(secret="{}:tenant_{}:server".format(config['FAUNA']['secret'], tenant_id))


def _load_config():
    configuration = configparser.ConfigParser()
    config_dict = {}
    try: 
        param_details = boto_client.get_parameters_by_path(
            Path=FAUNA_CONFIG_PATH,
            Recursive=False,
            WithDecryption=True
        )
        if 'Parameters' in param_details and len(param_details.get('Parameters')) > 0:
            for param in param_details.get('Parameters'):
                config_dict.update(json.loads(param.get('Value')))
    except:
        logger.error("Encountered an error loading config from SSM.")
        traceback.print_exc()
    finally:
        configuration['FAUNA'] = config_dict
        return configuration


class StatusCodes(Enum):
    SUCCESS    = 200
    UN_AUTHORIZED  = 401
    NOT_FOUND = 404
    
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


def generate_error_response(err):
    errorType = type(err)
    if errorType in (FaunaException, FaunaError, AuthenticationError, AuthorizationError):
        code = err.args[0]
        responseBody = err.args[1]
    elif errorType == QueryRuntimeError:
        code = err.args[0]
        responseBody = err.query_info.summary
    else:
        code = 400
        responseBody = err.args[0]

    response = {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type, Origin, X-Requested-With, Accept, Authorization, Access-Control-Allow-Methods, Access-Control-Allow-Headers, Access-Control-Allow-Origin",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
        "body": responseBody
    }

    return response

    
def encode_to_json_object(inputObject):
    jsonpickle.set_encoder_options('simplejson', use_decimal=True, sort_keys=True)
    jsonpickle.set_preferred_backend('simplejson')
    return jsonpickle.encode(inputObject, unpicklable=False, use_decimal=True)


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
