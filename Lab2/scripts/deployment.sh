#!/bin/bash

if [[ "$#" -eq 0 ]]; then
  echo "Invalid parameters"
  echo "Command to deploy client code: deployment.sh -c --email <email address>"
  echo "Command to deploy server code: deployment.sh -s --email <email address>" 
  echo "Command to deploy server & client code: deployment.sh -s -c --email <email address>"
  exit 1      
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s) server=1 ;;
        -c) client=1 ;;
        --email) email=$2
          shift ;;  
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

export $(grep -v '^#' .env | xargs)

stackname=$STACK_NAME
faunaApiKey=$FAUNA_API_KEY

if [[ -z "$stackname" ]]; then
    echo "Please provide a stack name by supplying a value for STACK_NAME in the .env file" 
    echo "Note: Invoke script without parameters to know the list of script parameters"
    exit 1  
fi

if [[ -z "$faunaApiKey" ]]; then
    echo "Please provide a value for FAUNA_API_KEY in the .env file" 
    echo "Note: Invoke script without parameters to know the list of script parameters"
    exit 1  
fi

if [[ $server -eq 1 ]]; then
  echo "Migrate Fauna database resources"
  cd ../server/fauna_adminApp_resources
  npm install
  node index.js $faunaApiKey
  cd ../../scripts

  echo "copying env to labs"
  cp .env ../../Lab3/scripts/
  # cp .env ../../Lab4/scripts/
  # cp .env ../../Lab5/scripts/
  # cp .env ../../Lab6/scripts/
fi

if [[ $server -eq 1 ]]; then
  echo "Server code is getting deployed"
  cd ../server

  REGION=$(aws configure get region)
  DEFAULT_SAM_S3_BUCKET=$(grep s3_bucket samconfig.toml|cut -d'=' -f2 | cut -d \" -f2)
  echo "aws s3 ls s3://$DEFAULT_SAM_S3_BUCKET"
  aws s3 ls s3://$DEFAULT_SAM_S3_BUCKET
  if [ $? -ne 0 ]; then
      echo "S3 Bucket: $DEFAULT_SAM_S3_BUCKET specified in samconfig.toml is not readable.
      So creating a new S3 bucket and will update samconfig.toml with new bucket name."
    
      UUID=$(uuidgen | awk '{print tolower($0)}')
      SAM_S3_BUCKET=sam-bootstrap-bucket-$UUID
      aws s3 mb s3://$SAM_S3_BUCKET --region $REGION
      if [[ $? -ne 0 ]]; then
        exit 1
      fi
      # Updating all labs samconfig.toml with new bucket name
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab3/server/shared-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab3/server/tenant-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab4/server/shared-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab4/server/tenant-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab5/server/shared-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab5/server/tenant-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab6/server/shared-samconfig.toml
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' ../../Lab6/server/tenant-samconfig.toml
  fi

  echo "Validating server code using pylint"
  python3 -m pylint -E -d E0401 $(find . -iname "*.py" -not -path "./.aws-sam/*")
  if [[ $? -ne 0 ]]; then
    echo "****ERROR: Please fix above code errors and then rerun script!!****"
    exit 1
  fi

  sam build -t template.yaml --use-container
  sam deploy --config-file samconfig.toml \
    --region=$REGION \
    --stack-name=$stackname \
    --parameter-overrides StackName=$stackname

  cd ../scripts
fi  


if [[ $client -eq 1 ]]; then
  if [[ -z "$email" ]]; then
    echo "Please provide email address to setup an admin user" 
    echo "Note: Invoke script without parameters to know the list of script parameters"
    exit 1  
  fi
  echo "Client code is getting deployed"
  APP_SITE_BUCKET=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSiteBucket'].OutputValue" --output text)
  APP_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSite'].OutputValue" --output text)

  ADMIN_APIGATEWAYURL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='AdminApi'].OutputValue" --output text)
  ADMIN_APPCLIENTID=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoOperationUsersUserPoolClientId'].OutputValue" --output text)
  ADMIN_USERPOOL_ID=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoOperationUsersUserPoolId'].OutputValue" --output text)
  ADMIN_USER_GROUP_NAME=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoAdminUserGroupName'].OutputValue" --output text)

  # Create admin-user in OperationUsers userpool with given input email address
  CREATE_ADMIN_USER=$(aws cognito-idp admin-create-user \
  --user-pool-id $ADMIN_USERPOOL_ID \
  --username admin-user \
  --user-attributes Name=email,Value=$email Name=phone_number,Value="+11234567890" Name="custom:userRole",Value="SystemAdmin" Name="custom:tenantId",Value="system_admins" \
  --desired-delivery-mediums EMAIL)
  
  echo "$CREATE_ADMIN_USER"

  # Add admin-user to admin user group
  ADD_ADMIN_USER_TO_GROUP=$(aws cognito-idp admin-add-user-to-group \
  --user-pool-id $ADMIN_USERPOOL_ID \
  --username admin-user \
  --group-name $ADMIN_USER_GROUP_NAME)

  echo "$ADD_ADMIN_USER_TO_GROUP"

  # Configuring admin UI 

  echo "aws s3 ls s3://$APP_SITE_BUCKET"
  aws s3 ls s3://$APP_SITE_BUCKET 
  if [ $? -ne 0 ]; then
      echo "Error! S3 Bucket: $APP_SITE_BUCKET not readable"
      exit 1
  fi

  cd ../client/App

  echo "Configuring environment for Admin Client"

  cat << EoF > .env
  VITE_ADMIN_API_GATEWAY_URL='$ADMIN_APIGATEWAYURL'
  VITE_ADMIN_APPCLIENTID='$ADMIN_APPCLIENTID'
  VITE_ADMIN_USERPOOL_ID='$ADMIN_USERPOOL_ID'
EoF

  echo no | npm install --legacy-peer-deps && npm run build

  echo "aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET"
  aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET 

  if [[ $? -ne 0 ]]; then
      exit 1
  fi

  echo "Completed configuring environment for Admin Client"
  echo "Successfully completed deploying Admin UI"
fi  
echo "Admin site URL: https://$APP_SITE_URL"