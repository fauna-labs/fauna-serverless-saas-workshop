# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import jsonpickle
import boto3
from enum import Enum
import os, configparser, traceback
import logger

from fauna.client import Client as FaunaClient
from fauna.errors import FaunaException, FaunaError, AuthenticationError, AuthorizationError, QueryRuntimeError, AbortError


FAUNA_CONFIG_PATH = os.environ['FAUNA_CONFIG_PATH']
boto_client = boto3.client('ssm')

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
    if errorType == AbortError:
        code = 400
        responseBody = err.abort
    elif errorType in (FaunaException, FaunaError, AuthenticationError, AuthorizationError):
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
    

def  encode_to_json_object(inputObject):
    jsonpickle.set_encoder_options('simplejson', use_decimal=True, sort_keys=True)
    jsonpickle.set_preferred_backend('simplejson')
    return jsonpickle.encode(inputObject, unpicklable=False, use_decimal=True)


class Fauna(FaunaClient):    
    @classmethod
    def from_config(cls):
        logger.info("Loading config and creating new db...")
        config = _load_config()
        return cls(secret=config['FAUNA']['secret'])


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


