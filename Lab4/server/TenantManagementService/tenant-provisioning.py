# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import utils
from aws_lambda_powertools import Tracer
tracer = Tracer()

codepipeline = boto3.client('codepipeline')

@tracer.capture_lambda_handler
def provision_tenant(event, context):    
    try:
        response_codepipeline = codepipeline.start_pipeline_execution(
            name='fauna-migration-stack-pipeline'
        )
    except Exception as e:
        raise
    else:
        return utils.create_success_response("Tenant Provisioning Started")

