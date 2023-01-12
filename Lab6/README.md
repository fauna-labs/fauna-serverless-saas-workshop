# About

Lab6 extends Lab5 by introducing a capability in AWS Gateway to set usage-plans. This allows different tiers
of customers to have custom rate-limits, throttling and quotas. 

## Deploying Lab6

### Fauna Setup
> Note: If you completed Lab2, Lab3, Lab4 or Lab5, skip this entire Fauna setup.

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