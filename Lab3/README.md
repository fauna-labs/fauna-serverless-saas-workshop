# About

Lab3 builds-out Lab2's basline architecture by combining-in the e-commerce app first introduced in Lab1. 
The web application now allows the user to toggle between the "admin" app and the e-commerce app (aka "tenant" app). 
Tenant services that power the e-commerce application are now "tenant aware" and handles authorization of
tenant-users, ensuring that only resources belonging to the users' tenant can be accessed. The authorization
construct extends all the way to the data layer, where logic routes requests to the proper child-database 
corresponding to the tenant.

## Deploying Lab3

### Fauna Setup
> Note: If you completed Lab2, skip this entire Fauna setup.

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