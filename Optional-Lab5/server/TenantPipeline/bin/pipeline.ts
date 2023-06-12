#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { ServerlessSaaSStack, FaunaMigrationsStack } from '../lib/serverless-saas-stack';

const app = new cdk.App();

new ServerlessSaaSStack(app, 'svls-saas-wkshp-pipeline');

new FaunaMigrationsStack(app, 'fauna-migrations-pipeline');

app.synth();