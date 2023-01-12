# About

Lab5 fully leverages the use of AWS Code Pipeline (first introduced in Lab4) to provision an entire stack of 
resources dedicated to a single tenant. This capability allows the multi-tenant app to provide an elevated "tier"
of service, where the tenant is provided dedicated AWS resources for higher levels of assurance and support.

## Deploying Lab5

### Fauna Setup
> Note: If you completed Lab2, Lab3 or Lab4, skip this entire Fauna setup.

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
./deployment.sh -s -c
```