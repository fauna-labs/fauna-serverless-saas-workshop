# About

Lab5 fully leverages the use of AWS Code Pipeline (first introduced in Lab4) to provision an entire stack of 
resources dedicated to a single tenant. This capability allows the multi-tenant app to provide an elevated "tier"
of service, where the tenant is provided dedicated AWS resources for higher levels of assurance and support.

## Deploying Lab5

### Prerequisites
* Node 16 or greater
* Python 3.9 or greater
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
* [AWS CDK Toolkit](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)
* [jq](https://pypi.org/project/jq/)
* [pylint](https://pypi.org/project/pylint/)
* [git-remote-codecommit](https://pypi.org/project/git-remote-codecommit/)

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
> Note: If you completed Lab2, Lab3 or Lab4, skip this entire Fauna setup.

* Login to the Fauna [dashboard](https://dashboard.fauna.com)
* Create a new database
* Generate an API Key for the database above:
  * Naviate to __Security__ > __Keys__
  * Click **New Key**
  * Role = **Admin**
  * Provide a name for the key
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

### Create a Parameter Store parameter
> Note: If you've already done this in previous labs, you may skip this step.
> 
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