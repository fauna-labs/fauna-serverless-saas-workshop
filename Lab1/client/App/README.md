# Sample App
This project was built with Vue 3 and Vite. Check out the [guide](https://vitejs.dev/guide/) 

## Setup
No setup is necessary as the [/scripts/deployment.sh](../../scripts/deployment.sh) script should create
a `.env` file with the necessary environment variables for you:

```
VITE_APP_APIGATEWAYURL=<API Gateway URL>
```

## Run locally

```
npm run dev
```

## Build
The [/scripts/deployment.sh](../../scripts/deployment.sh) script builds and deploys this app on CloudFront
but you can run manually as well:

```
npm install && run build

aws s3 sync --delete --cache-control no-store dist s3://$APP_SITE_BUCKET 
```