import json
import logger
from crhelper import CfnResource
helper = CfnResource()
    
@helper.create
@helper.update
def do_action(event, _):
    logger.info("Getting Tenant Details...")

    tenant_id = event['ResourceProperties']['TenantId']
                   
    helper.Data.update({"UpdateTenantAPIGatewayURLData": tenant_id})

@helper.delete
def do_nothing(_, __):
    pass

def handler(event, context):   
    helper(event, context)
        
    