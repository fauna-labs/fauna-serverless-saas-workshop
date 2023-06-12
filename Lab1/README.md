# About

Lab1 is a basic e-commerce application that introduces the core components of a "serverless web application": 
* AWS Serverless Services:
  * API Gateway and Lambda for the e-commerce microservices
  * S3 and CloudFront for hosting the front-end Single Page Application (SPA)
* Introducing [Fauna](https://fauna.com)
  * An ACID-compliant, globally distributed, replicated (with active-active writes) database delivered as an API 

![Lab 1 Architecture](/images/ServerlessSaas-Lab1.png)

## Deploying Lab1

### Prerequisites
* Node 16 or greater
* Python 3.9 or greater
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
* [jq](https://pypi.org/project/jq/)
* [pylint](https://pypi.org/project/pylint/)

### AWS Setup
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
  STACK_NAME="serverless-saas-fauna-workshop-lab1"
  FAUNA_API_KEY="<The API Key>"
  AWS_PROFILE="serverless-workshop"
  ```

### Deploy the AWS resources using the provided script:
```
cd /scripts/
./deployment.sh -s -c
```