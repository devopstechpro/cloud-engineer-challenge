#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { EntrixStack } from '../lib/entrix-stack';
import { PipelineStack } from '../lib/pipeline-stack';

const app = new cdk.App();
new EntrixStack(app, 'EntrixStack', {
  /* If you don't specify 'env', this stack will be environment-agnostic.
   * Account/Region-dependent features and context lookups will not work,
   * but a single synthesized template can be deployed anywhere. */

  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  // env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },

  /* Uncomment the next line if you know exactly what Account and Region you
   * want to deploy the stack to. */
  // env: { account: '123456789012', region: 'us-east-1' },

  /* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
});

new PipelineStack(app, 'PipelineStack', {
  env: { region: 'eu-west-1' },
  /*
   * Make sure to update githubOwner, githubRepo, and connectionArn in pipeline-stack.ts
   * to match your actual GitHub repository and CodeStar Connection ARN.
   */
});