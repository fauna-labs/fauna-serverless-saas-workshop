# About

Lab1 is a basic e-commerce application that introduces the core components of a "serverless web application": 
* AWS Serverless Services:
  * API Gateway and Lambda for the e-commerce microservices
  * S3 and CloudFront for hosting the front-end Single Page Application (SPA)
* Introducing [Fauna](https://fauna.com)
  * An ACID-compliant, globally distributed, replicated (with active-active writes) database delivered as an API 


## Deploying Lab1

### Fauna Setup
* Login to the Fauna [dashboard](https://dashboard.fauna.com)
* Create a new database
* Generate an API Key for the database above:
  * Naviate to __Security__ > __Keys__
  * Click **New Key**
  * Role = **Admin**
  * Provife a name for the key
  * Copy the value, you will not be able to see it again.
* Save API Key from previous step into [/scripts/.env](./scripts/.env) 

  e.g. 
  ```
  STACK_NAME=serverless-saas-fauna-workshop-lab1
  FAUNA_API_KEY=<The API Key>
  ```
  (For convenience, a `./scripts/.env.template` is provided):


### Deploy the AWS resources using the provided script:
```
cd /scripts/
./deployment.sh -s -c
```