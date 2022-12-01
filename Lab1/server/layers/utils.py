# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import jsonpickle
import simplejson

import boto3
from enum import Enum

import os, configparser, traceback
from faunadb.client import FaunaClient
from faunadb.errors import Unauthorized, NotFound


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
    err_type = type(err)
    if err_type == Unauthorized:
        code = 401
    elif err_type == NotFound:
        code = 404        
    else:
        code = 400

    response = {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type, Origin, X-Requested-With, Accept, Authorization, Access-Control-Allow-Methods, Access-Control-Allow-Headers, Access-Control-Allow-Origin",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        }
    }
    if code == 400:
      response['body'] = err.args[0]

    return response  
    

def  encode_to_json_object(inputObject):
    jsonpickle.set_encoder_options('simplejson', use_decimal=True, sort_keys=True)
    jsonpickle.set_preferred_backend('simplejson')
    return jsonpickle.encode(inputObject, unpicklable=False, use_decimal=True)


class Fauna(FaunaClient):
    @classmethod
    def from_config(cls, config):
        print("Loading config and creating new db...")
        return cls(
            secret=config['FAUNA']['secret']
        )

# https://aws.amazon.com/blogs/compute/sharing-secrets-with-aws-lambda-using-aws-systems-manager-parameter-store/
def load_config():
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
        print("Encountered an error loading config from SSM.")
        traceback.print_exc()
    finally:
        configuration['FAUNA'] = config_dict
        return configuration

