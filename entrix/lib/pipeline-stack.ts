import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const githubOwner = 'devopstechpro';
    const githubRepo = 'cloud-engineer-challenge';
    const githubBranch = 'main'; // or 'master'

    const connectionArn = 'arn:aws:codeconnections:eu-west-1:054522428175:connection/3428c934-b62b-47d5-b7e2-32d3445058f9';

    const sourceOutput = new codepipeline.Artifact();
    const synthOutput = new codepipeline.Artifact();

    // CodeBuild project for CDK synth
    const synthProject = new codebuild.PipelineProject(this, 'CdkSynthProject', {
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          install: {
            'runtime-versions': { nodejs: 18 },
            commands: [
              'npm install -g aws-cdk',
              'cd entrix && npm install',
            ],
          },
          build: {
            commands: [
              'pwd',
              'ls -al',
              'cd entrix && npm run build',
              'cd entrix && npx cdk synth',
            ],
          },
        },
        artifacts: {
          'base-directory': 'entrix/cdk.out',
          files: ['**/*'],
        },
      }),
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
      },
    });

    new codepipeline.Pipeline(this, 'EntrixCICDPipeline', {
      pipelineName: 'EntrixCICDPipeline',
      stages: [
        {
          stageName: 'Source',
          actions: [
            new codepipeline_actions.CodeStarConnectionsSourceAction({
              actionName: 'GitHub_Source',
              owner: githubOwner,
              repo: githubRepo,
              branch: githubBranch,
              output: sourceOutput,
              connectionArn: connectionArn,
            }),
          ],
        },
        {
          stageName: 'Build',
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: 'CDK_Build_and_Synth',
              project: synthProject,
              input: sourceOutput,
              outputs: [synthOutput],
            }),
          ],
        },
        {
          stageName: 'Deploy',
          actions: [
            new codepipeline_actions.CloudFormationCreateUpdateStackAction({
              actionName: 'CFN_Deploy',
              templatePath: synthOutput.atPath('EntrixStack.template.json'),
              stackName: 'EntrixStack',
              adminPermissions: true,
            }),
          ],
        },
      ],
    });
  }
} 