import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CodePipeline, CodePipelineSource, ShellStep } from 'aws-cdk-lib/pipelines';
import { EntrixStack } from './entrix-stack';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the pipeline using CDK Pipelines (self-mutating)
    const pipeline = new CodePipeline(this, 'Pipeline', {
      synth: new ShellStep('Synth', {
        input: CodePipelineSource.connection('devopstechpro/cloud-engineer-challenge', 'main', {
          connectionArn: 'arn:aws:codeconnections:eu-west-1:054522428175:connection/3428c934-b62b-47d5-b7e2-32d3445058f9',
        }),
        commands: [
          'pwd',
          'ls -al',
          'cd entrix',
          'npm install',
          'npm run build',
          'npx cdk synth'
        ],
        primaryOutputDirectory: 'entrix/cdk.out',
        env: {
          NODE_VERSION: '23'
        }
      }),
    });

    // Add application stage (EntrixStack)
    pipeline.addStage(new EntrixAppStage(this, 'Dev', {
      env: { region: 'eu-west-1' },
    }));
  }
}

// Define EntrixAppStage for deploying EntrixStack
class EntrixAppStage extends cdk.Stage {
  constructor(scope: Construct, id: string, props?: cdk.StageProps) {
    super(scope, id, props);
    new EntrixStack(this, 'EntrixStack', {
      env: props?.env,
    });
  }
} 