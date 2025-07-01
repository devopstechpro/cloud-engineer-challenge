import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as stepfunctions from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

export class EntrixStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Reference existing JWT Secret in Secrets Manager
    const jwtSecret = secretsmanager.Secret.fromSecretNameV2(this, 'JwtSecret', 'entrix-jwt-secret');

    // DynamoDB Table with TTL for 24h expiry
    const table = new dynamodb.Table(this, 'OrdersTable', {
      partitionKey: { name: 'record_id', type: dynamodb.AttributeType.STRING },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      timeToLiveAttribute: 'expires_at', // TTL attribute
    });

    // S3 Bucket for order results
    const bucket = new s3.Bucket(this, 'OrderResultsBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });


    // Lambda Functions (API, A, B)
    const apiLambda = new lambda.Function(this, 'ApiLambda', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset('../src/post_lambda'),
      environment: {
        TABLE_NAME: table.tableName,
      },
    });
    table.grantWriteData(apiLambda);

    const lambdaA = new lambda.Function(this, 'LambdaA', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset('../src/lambda_a'),
    });

    const lambdaB = new lambda.Function(this, 'LambdaB', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset('../src/lambda_b'),
      environment: {
        LOG_BUCKET: bucket.bucketName,
      },
    });
    bucket.grantWrite(lambdaB);

    // SNS Topic for notifications (simulated Slack)
    const notificationTopic = new sns.Topic(this, 'NotificationTopic');

    // Step Function workflow
    // 1. Task: Invoke LambdaA
    const lambdaATask = new tasks.LambdaInvoke(this, 'Invoke LambdaA', {
      lambdaFunction: lambdaA,
      outputPath: '$.Payload',
    });

    // 2. Choice: Check if results:true
    const checkResults = new stepfunctions.Choice(this, 'Results Ready?');
    const isResultsTrue = stepfunctions.Condition.booleanEquals('$.results', true);

    // 3. Map: For each order, invoke LambdaB
    const lambdaBTask = new tasks.LambdaInvoke(this, 'Invoke LambdaB', {
      lambdaFunction: lambdaB,
      payloadResponseOnly: true,
      payload: stepfunctions.TaskInput.fromObject({
        'status.$': '$.status',
        'power.$': '$.power',
      }),
      resultPath: '$.lambdaBResult',
    })
      .addCatch(new tasks.SnsPublish(this, 'Notify on LambdaB Error', {
        topic: notificationTopic,
        message: stepfunctions.TaskInput.fromJsonPathAt('$.errorInfo.Cause'),
        resultPath: stepfunctions.JsonPath.DISCARD,
      }), {
        resultPath: '$.errorInfo',
      });

    const mapOrders = new stepfunctions.Map(this, 'Process Orders', {
      itemsPath: '$.orders',
      resultPath: stepfunctions.JsonPath.DISCARD,
    });
    mapOrders.iterator(lambdaBTask);

    // 4. Loop: If results:false, retry LambdaA
    const definition = lambdaATask
      .next(checkResults
        .when(isResultsTrue, mapOrders)
        .otherwise(lambdaATask));

    // 5. State Machine
    const stateMachine = new stepfunctions.StateMachine(this, 'PipelineStateMachine', {
      definition,
      timeout: cdk.Duration.minutes(5),
    });

    // Lambda Layer for PyJWT
    // 1. Package the layer: pip3 install pyjwt -t ../src/auth_lambda_layer/python
    // 2. The directory structure should be: ../src/auth_lambda_layer/python/jwt/... etc.
    const jwtLayer = new lambda.LayerVersion(this, 'JwtLayer', {
      code: lambda.Code.fromAsset('../src/auth_lambda_layer'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_13],
      description: 'Layer with PyJWT for JWT authorizer',
    });

    // Lambda Authorizer for JWT authentication (request-based)
    const authorizerLambda = new lambda.Function(this, 'JwtAuthorizerLambda', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset('../src/auth_lambda'),
      environment: {
        JWT_SECRET_ARN: jwtSecret.secretArn,
      },
      layers: [jwtLayer],
    });

    // Grant the Lambda function permission to read the secret
    jwtSecret.grantRead(authorizerLambda);

    // API Gateway to expose the API Lambda as a POST endpoint
    const api = new apigateway.LambdaRestApi(this, 'EntrixApi', {
      handler: apiLambda,
      proxy: false,
      restApiName: 'Entrix Orders API',
      deploy: true,
      deployOptions: {
        stageName: 'prod',
        description: 'Production stage for Entrix Orders API',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
    });

    const orders = api.root.addResource('orders');

    // Attach request-based Lambda authorizer to POST /orders
    const jwtAuthorizer = new apigateway.RequestAuthorizer(this, 'JwtRequestAuthorizer', {
      handler: authorizerLambda,
      identitySources: [apigateway.IdentitySource.header('Authorization')]
    });
    orders.addMethod('POST', undefined, {
      authorizer: jwtAuthorizer,
      authorizationType: apigateway.AuthorizationType.CUSTOM,
    });
  }
}
  