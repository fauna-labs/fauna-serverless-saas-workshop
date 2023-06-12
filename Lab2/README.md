# About

Lab2 introduces "shared services" - services that allow you to onboard, authenticate and manage a multi-tenant environment.

The web application in Lab2:
* Allows end-users to self-register for a tenant
* Provides a SaaS admin-console that a "super admin" uses to manage tenants
* Adds a notion of multi-tenancy by introducing shared services that are needed to register, authenticate, and manage
  tenants. 
* Introduces Fauna parent-child database features that allows for siloed segregation of tenant data

![Lab 2 Architecture](/images/ServerlessSaas-Lab2.png)

## Deploying Lab2

### Prerequisites
* Node 16 or greater
* Python 3.9 or greater
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
* [jq](https://pypi.org/project/jq/)
* [pylint](https://pypi.org/project/pylint/)

### AWS Setup
> Ignore this step if you've already completed it in previous lab(s)
* Navigate to the IAM services dashboard and create a new user with Administrator access (as we'll need it to provision lots
  of AWS resources).
* Create an "access key" and when done copy its **Access Key** and **Secret Access Key** for the next step, below.
* Create a "named profile" in your AWS CLI's credentials file:
  * Your AWS **config** and **credentials** files are normally in the **~/.aws** folder (Linux/macOS) 
    or **C:&#92;Users&#92; USERNAME &#92;.aws&#92;** (Windows). For more information about config and credentials
    file settings see [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html#cli-configure-files-using-profiles)
  * Edit the `credentials` file by adding the following entry: 
  ```
  [serverless-workshop]
  aws_access_key_id=<<"Access Key" from the previous step>>
  aws_secret_access_key=<<"Secret Access Key" from the previous step>>
  ```

### Fauna Setup
> Note: You may have noticed these same steps from Lab1. Please continue and create a new Fauna database as we won't be using Lab1's database.

* Login to the Fauna [dashboard](https://dashboard.fauna.com)
* Create a new database
* Generate an API Key for the database above:
  * Naviate to __Security__ > __Keys__
  * Click **New Key**
  * Role = **Admin**
  * Provide a name for the key
  * Copy the value, you will not be able to see it again.
* Save API Key from previous step into a new file `/scripts/.env`
  > A template file [/scripts/.env.template](./scripts/.env.template) has been provided for you. Make a copy of it and rename it `.env`, and edit in the values
* Update the `AWS_PROFILE` variable to match the profile name you set in the AWS `credentials` file above

  e.g. 
  ```
  STACK_NAME="serverless-saas-fauna"
  FAUNA_API_KEY="<The API Key>"
  AWS_PROFILE="serverless-workshop"
  ```




### Deploy the AWS resources using the provided script:
```
cd /scripts/
./deployment.sh -s -c --email <provide your email to receive the Admin login credentials>
```

### Create a Parameter Store parameter
The previous script utlilized CloudFormation to create AWS resources, among which is a KMS Key that we'll
now use to create an encrypted parameter to store the previously obtained Fauna API Key. 
The Lambdas that need to access Fauna have permission to use this KMS Key to decrypt the parameter, 
retrieving the API Key that will be used to authorize Fauna requests.

From the AWS Dashboard, navigate to **Systems Manager > Parameter Store**. (*Notice there is a sample (unencrypted) parameter
named **/serverless-saas-fauna/faunadb/config/appConfig** created already*). 

**Create a new (encrypted) parameter:**

* Name = **/serverless-saas-fauna/faunadb/config/appSecrets**
* Type = **SecureString**
* KMS Key Source = **My current account**
* KMS Key ID = **alias/ServerlessSaasFaunaWorkshopParameterStoreKey**
* Value = `{"secret": "<key from Fauna setup>"}`
  > **Note:** Be sure to include the double quotes (`"`)
  >
  > e.g. `{"secret": "thefAUNageNERateDSecReTVAlueFORapiKEy"}`