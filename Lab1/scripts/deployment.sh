#!/bin/bash

if [[ "$#" -eq 0 ]]; then
  echo "Invalid parameters"
  echo "Command to deploy client code: deployment.sh -c"
  echo "Command to deploy server code: deployment.sh -s" 
  echo "Command to deploy server & client code: deployment.sh -s -c"
  exit 1      
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s) server=1 ;;
        -c) client=1 ;;
        -t) test=1 ;;
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

if [[ $test -eq 1 ]]; then
  echo "Testing"
  echo "stackname = $stackname"
  echo "faunaApiKey = $faunaApiKey"
fi

if [[ $server -eq 1 ]]; then
  echo "Migrate Fauna database resources"
  cd ../server/fauna_resources
  npm install
  node index.js $faunaApiKey
  cd ../../scripts

  echo "copying profile to labs"
  if ! test -f ../../Lab2/scripts/.env; then
    cp ../../Lab2/scripts/.env.template ../../Lab2/scripts/.env
  fi
  if ! test -f ../../Lab3/scripts/.env; then
    cp ../../Lab3/scripts/.env.template ../../Lab3/scripts/.env

  fi
  if ! test -f ../../Lab4/scripts/.env; then
    cp ../../Lab4/scripts/.env.template ../../Lab4/scripts/.env
  fi
  if ! test -f ../../Lab5/scripts/.env; then
    cp ../../Lab5/scripts/.env.template ../../Lab5/scripts/.env
  fi
  if ! test -f ../../Lab6/scripts/.env; then
    cp ../../Lab6/scripts/.env.template ../../Lab6/scripts/.env
  fi
  ex -sc '%s/AWS_PROFILE=.*/AWS_PROFILE=\"'$AWS_PROFILE'\"/|x' ../../Lab2/scripts/.env
  ex -sc '%s/AWS_PROFILE=.*/AWS_PROFILE=\"'$AWS_PROFILE'\"/|x' ../../Lab3/scripts/.env
  ex -sc '%s/AWS_PROFILE=.*/AWS_PROFILE=\"'$AWS_PROFILE'\"/|x' ../../Lab4/scripts/.env
  ex -sc '%s/AWS_PROFILE=.*/AWS_PROFILE=\"'$AWS_PROFILE'\"/|x' ../../Lab5/scripts/.env
  ex -sc '%s/AWS_PROFILE=.*/AWS_PROFILE=\"'$AWS_PROFILE'\"/|x' ../../Lab6/scripts/.env
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
      # Updating samconfig.toml with new bucket name
      ex -sc '%s/s3_bucket = .*/s3_bucket = \"'$SAM_S3_BUCKET'\"/|x' samconfig.toml
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
    --parameter-overrides FaunadbApiKey=$faunaApiKey StackName=$stackname

  cd ../scripts
fi

if [[ $client -eq 1 ]]; then
  echo "Client code is getting deployed"
  APP_SITE_BUCKET=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='AppBucket'].OutputValue" --output text)
  APP_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSite'].OutputValue" --output text)
  APP_APIGATEWAYURL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='APIGatewayURL'].OutputValue" --output text)

  # Configuring application UI 

  echo "aws s3 ls s3://$APP_SITE_BUCKET"
  aws s3 ls s3://$APP_SITE_BUCKET 
  if [ $? -ne 0 ]; then
      echo "Error! S3 Bucket: $APP_SITE_BUCKET not readable"
      exit 1
  fi

 cd ../client/App

 echo "Configuring environment for App Client"

  cat << EoF > .env
  VITE_APP_APIGATEWAYURL='$APP_APIGATEWAYURL'
EoF

 echo no | npm install --legacy-peer-deps && npm run build

 echo "aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET"
 aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET 

 if [[ $? -ne 0 ]]; then
     exit 1
 fi

 echo "Completed configuring environment for App Client"

 echo "Application site URL: https://$APP_SITE_URL"
fi



