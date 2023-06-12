#!/bin/bash

echo "server code is getting deployed"


export $(grep -v '^#' .env | xargs)

stackname=$STACK_NAME

if [[ -z "$stackname" ]]; then
    echo "Please provide a stack name by supplying a value for STACK_NAME in the .env file" 
    echo "Note: Invoke script without parameters to know the list of script parameters"
    exit 1  
fi

cd ../server
REGION=$(aws configure get region)

echo "Validating server code using pylint"
python3 -m pylint -E -d E0401 $(find . -iname "*.py" -not -path "./.aws-sam/*" -not -path "./TenantPipeline/node_modules/*")
if [[ $? -ne 0 ]]; then
  echo "****ERROR: Please fix above code errors and then rerun script!!****"
  exit 1
fi

sam build -t shared-template.yaml --use-container
sam deploy --config-file shared-samconfig.toml \
  --region=$REGION \
  --stack-name=$stackname \
  --parameter-overrides StackName=$stackname

echo "Pooled tenant server code is getting deployed"
sam build -t tenant-template.yaml --use-container
sam deploy --config-file tenant-samconfig.toml \
  --region=$REGION \
  --stack-name=stack-$stackname-pooled \
  --parameter-overrides StackName=$stackname

cd ../scripts

APP_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSite'].OutputValue" --output text)

echo "App site URL: https://$APP_SITE_URL"






