#!/bin/bash

if [[ "$#" -eq 0 ]]; then
  echo "Invalid parameters"
  echo "Command to deploy client code: deployment.sh -c"
  echo "Command to deploy bootstrap server code: deployment.sh -b"
  echo "Command to deploy CI/CD pipeline code: deployment.sh -p"
  echo "Command to deploy CI/CD pipeline, bootstrap & tenant server code: deployment.sh -s" 
  echo "Command to deploy server & client code: deployment.sh -s -c"
  exit 1      
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s) server=1 ;;
        -b) bootstrap=1 ;;        
        -p) pipeline=1 ;;
        -c) client=1 ;;
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

if [[ $server -eq 1 ]] || [[ $bootstrap -eq 1 ]]; then
  echo "Migrate Fauna database resources"
  cd ../server/fauna_adminApp_resources
  npm install
  node index.js $faunaApiKey
  cd ../../scripts
fi

if [[ $server -eq 1 ]] || [[ $bootstrap -eq 1 ]]; then
  echo "Server code is getting deployed"
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

  cd ../scripts

fi

if [[ $server -eq 1 ]] || [[ $pipeline -eq 1 ]]; then
  echo "CI/CD pipeline code is getting deployed"
  #Create CodeCommit repo
  REGION=$(aws configure get region)
  REPO=$(aws codecommit get-repository --repository-name $stackname-workshop)
  if [[ $? -ne 0 ]]; then
      echo "$stackname-workshop codecommit repo is not present, will create one now"
      CREATE_REPO=$(aws codecommit create-repository --repository-name $stackname-workshop --repository-description "$stackname repository")
      echo $CREATE_REPO
      REPO_URL="codecommit::${REGION}://$stackname-workshop"
      git remote add cc $REPO_URL
      if [[ $? -ne 0 ]]; then
           echo "Setting url to remote cc"
           git remote set-url cc $REPO_URL
      fi
      git push --set-upstream cc fauna
  fi

  #Deploying CI/CD pipeline
  cd ../server/TenantPipeline/
  npm install && npm run build 
  cdk bootstrap  
  cdk deploy svls-saas-wkshp-pipeline --require-approval never
  cdk deploy fauna-migrations-pipeline --require-approval never

  cd ../../scripts

fi

APP_SITE_URL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSite'].OutputValue" --output text)  

if [[ $client -eq 1 ]]; then
  echo "Client code is getting deployed"
  APP_SITE_BUCKET=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='ApplicationSiteBucket'].OutputValue" --output text)
  ADMIN_APIGATEWAYURL=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='AdminApi'].OutputValue" --output text)
  ADMIN_APPCLIENTID=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoOperationUsersUserPoolClientId'].OutputValue" --output text)
  ADMIN_USERPOOL_ID=$(aws cloudformation describe-stacks --stack-name $stackname --query "Stacks[0].Outputs[?OutputKey=='CognitoOperationUsersUserPoolId'].OutputValue" --output text)
  
  # Configuring app UI 
  echo "aws s3 ls s3://$APP_SITE_BUCKET"
  aws s3 ls s3://$APP_SITE_BUCKET 
  if [ $? -ne 0 ]; then
      echo "Error! S3 Bucket: $APP_SITE_BUCKET not readable"
      exit 1
  fi

  cd ../client/App

  echo "Configuring environment for App Client"

  cat << EoF > .env
  VITE_ADMIN_API_GATEWAY_URL='$ADMIN_APIGATEWAYURL'
  VITE_ADMIN_APPCLIENTID='$ADMIN_APPCLIENTID'
  VITE_ADMIN_USERPOOL_ID='$ADMIN_USERPOOL_ID'
EoF

  npm install --legacy-peer-deps && npm run build

  echo "aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET"
  aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET 

  if [[ $? -ne 0 ]]; then
      exit 1
  fi

  echo "Completed configuring environment for App Client"
  echo "Successfully completed redeploying Application UI"

fi

echo "App site URL: https://$APP_SITE_URL"
  
