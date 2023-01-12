# About

Lab2 introduces "shared services" - services that allow you to onboard, authenticate and manage a multi-tenant environment.

The web application in Lab2:
* Allows end-users to self-register for a tenant
* Provides a SaaS admin-console that a "super admin" uses to manage tenants
* Adds a notion of multi-tenancy by introducing shared services that are needed to register, authenticate, and manage
  tenants. 
* Introduces Fauna parent-child database features that allows for siloed segregation of tenant data

## Deploying Lab2

### Fauna Setup
> You may have noticed these same steps from Lab1. Go ahead and create a new Fauna database 
> as we won't be using Lab1's database.

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
./deployment.sh -s -c --email <provide your email to receive the Admin login credentials>
```