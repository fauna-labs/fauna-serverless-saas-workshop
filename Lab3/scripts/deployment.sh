#!/bin/bash

if [[ "$#" -eq 0 ]]; then
  echo "Invalid parameters"
  echo "Command to deploy client code: deployment.sh -c"
  echo "Command to deploy bootstrap server code: deployment.sh -b"
  echo "Command to deploy tenant server code: deployment.sh -t"
  echo "Command to deploy bootstrap & tenant server code: deployment.sh -s" 
  echo "Command to deploy server & client code: deployment.sh -s -c"
  exit 1      
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s) server=1 ;;
        -b) bootstrap=1 ;;
        -t) tenant=1 ;;
        -c) client=1 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

stackname="serverless-saas-fauna"

if [[ $server -eq 1 ]] || [[ $bootstrap -eq 1 ]] || [[ $tenant -eq 1 ]]; then
  echo "Validating server code using pylint"
  cd ../server
  python3 -m pylint -E -d E0401,E1111 $(find . -iname "*.py" -not -path "./.aws-sam/*")
  if [[ $? -ne 0 ]]; then
    echo "****ERROR: Please fix above code errors and then rerun script!!****"
    exit 1
  fi
  cd ../scripts
fi

if [[ $server -eq 1 ]] || [[ $bootstrap -eq 1 ]]; then
  echo "Bootstrap server code is getting deployed"
  cd ../server
  REGION=$(aws configure get region)
  sam build -t shared-template.yaml --use-container
  sam deploy --config-file shared-samconfig.toml --region=$REGION
  cd ../scripts
fi  

if [[ $server -eq 1 ]] || [[ $tenant -eq 1 ]]; then
  echo "Tenant server code is getting deployed"
  cd ../server
  REGION=$(aws configure get region)
  sam build -t tenant-template.yaml --use-container
  sam deploy --config-file tenant-samconfig.toml --region=$REGION
  cd ../scripts
fi

ADMIN_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='AdminAppSite'].OutputValue" --output text)
LANDING_APP_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='LandingApplicationSite'].OutputValue" --output text)
APP_SITE_BUCKET=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSiteBucket'].OutputValue" --output text)
APP_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSite'].OutputValue" --output text)

if [[ $client -eq 1 ]]; then
  echo "Client code is getting deployed"
  ADMIN_APIGATEWAYURL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='AdminApi'].OutputValue" --output text)
  APP_APIGATEWAYURL=$(aws cloudformation describe-stacks --stack-name stack-pooled-fauna --query "Stacks[0].Outputs[?OutputKey=='TenantAPI'].OutputValue" --output text)
  APP_APPCLIENTID=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoTenantAppClientId'].OutputValue" --output text)
  APP_USERPOOLID=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoTenantUserPoolId'].OutputValue" --output text)


  # Admin UI and Landing UI are configured in Lab2 
  echo "Admin UI and Landing UI are configured in Lab2. Only App UI will be configured in this Lab3."
  # Configuring app UI 

  echo "aws s3 ls s3://$APP_SITE_BUCKET"
  aws s3 ls s3://$APP_SITE_BUCKET 
  if [ $? -ne 0 ]; then
      echo "Error! S3 Bucket: $APP_SITE_BUCKET not readable"
      exit 1
  fi

  cd ../client/Application

  echo "Configuring environment for App Client"

  cat << EoF > ./src/environments/environment.prod.ts
  export const environment = {
    production: true,
    regApiGatewayUrl: '$ADMIN_APIGATEWAYURL',
    apiGatewayUrl: '$APP_APIGATEWAYURL',
    userPoolId: '$APP_USERPOOLID',
    appClientId: '$APP_APPCLIENTID',
  };
EoF
  cat << EoF > ./src/environments/environment.ts
  export const environment = {
    production: true,
    regApiGatewayUrl: '$ADMIN_APIGATEWAYURL',
    apiGatewayUrl: '$APP_APIGATEWAYURL',
    userPoolId: '$APP_USERPOOLID',
    appClientId: '$APP_APPCLIENTID',
  };
EoF

  npm install --legacy-peer-deps && npm run build

  echo "aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET"
  aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET 

  if [[ $? -ne 0 ]]; then
      exit 1
  fi

  echo "Completed configuring environment for App Client"
  echo "Successfully completed deploying Application UI"
fi  

echo "Admin site URL: https://$ADMIN_SITE_URL"
echo "Landing site URL: https://$LANDING_APP_SITE_URL"
echo "App site URL: https://$APP_SITE_URL"
