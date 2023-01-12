# About

Lab4 introduces AWS Code Pipeline, which we first use to run a command-line tool to manage Fauna database resources as code.

## Deploying Lab4

### Fauna Setup
> Note: If you completed Lab2 or Lab3, skip this entire Fauna setup.

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
  STACK_NAME="serverless-saas-fauna"
  FAUNA_API_KEY=<The API Key>
  ```
  (For convenience, a `./scripts/.env.template` is provided):


### Deploy the AWS resources using the provided script:
```
cd /scripts/
./deployment.sh -s
```