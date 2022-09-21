import json
import boto3
import os, configparser, traceback
import logger
from crhelper import CfnResource
from faunadb.client import FaunaClient
from faunadb import query as q

helper = CfnResource()

try:
    ssm_client = boto3.client('ssm')
except Exception as e:
    helper.init_failure(e)

@helper.create
@helper.update
def do_action(event, _):
    logger.info("Getting Tenant Details...")

    fauna_config_path = event['ResourceProperties']['ParameterStoreFaunaConfig']
    tenant_id = event['ResourceProperties']['TenantId']
    if tenant_id == 'pooled':
        helper.Data.update({"userPoolId": event['ResourceProperties']['TenantUserPoolPooled']})
        helper.Data.update({"appClientId": event['ResourceProperties']['TenantAppClientPooled']})
        helper.Data.update({"apiGatewayUrl": event['ResourceProperties']['TenantApiGatewayUrlPooled']})
    else:
        configuration = configparser.ConfigParser()
        config_dict = {}
        try: 
            param_details = ssm_client.get_parameters_by_path(
                Path=fauna_config_path,
                Recursive=False,
                WithDecryption=True
            )
            if 'Parameters' in param_details and len(param_details.get('Parameters')) > 0:
                for param in param_details.get('Parameters'):
                    config_dict.update(json.loads(param.get('Value')))

            configuration['FAUNA'] = config_dict

            client = FaunaClient(
              secret=configuration['FAUNA']['secret'],
              domain=configuration['FAUNA']['domain'],
            )
            
            tenant_data = client.query(
              q.select(['data'], q.get(q.ref(q.collection('tenant'), tenant_id)))
            )
                          
            helper.Data.update({"userPoolId": tenant_data['userPoolId']})
            helper.Data.update({"appClientId": tenant_data['appClientId']})
            helper.Data.update({"apiGatewayUrl": tenant_data['apiGatewayUrl']})
        except:
            print("Encountered an error loading config from SSM.")
            traceback.print_exc()
    
    return "ZZ_pyhysical_id_tenant_{}".format(tenant_id)

@helper.delete
def do_nothing(_, __):
    pass

def handler(event, context):   
    helper(event, context)
        
    