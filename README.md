# Cloud Engineer Challenge / Entrix AWS Infrastructure using CDK

This project defines the infrastructure for the Entrix energy market auction service using AWS CDK (TypeScript). The solution is fully serverless, secure, and designed for easy extensibility and robust automation.

## Task completed
- ✅ There should be a validation of the Lambda A output checking the results field. If the results are false, Lambda A should be re-triggered until the results are true. 
- ✅ If Lambda B raises an error, there should be a notification sent to a Slack Channel or similar app (don't have to link the actual messaging app).
- ✅ Data in the database should expire after 24 hours.
- ✅ Create AWS deployment Pipeline that deploys the app from our GitHub repo to our AWS account using CodePipeline.
- ✅ All merges to master should automatically deploy the code to Dev environment.
- ✅ Create a simple GitHub Actions workflow to run on merge to master.


## List of services used
- Lambda Functions (API, A, B, authorizer)
- API Gateway REST API (with JWT authorizer)
- Lambda Layer (PyJWT)
- DynamoDB Table (with TTL)
- S3 Bucket (for order results)
- Step Functions State Machine
- SNS Topic (for notifications)
- EventBridge Rule (for scheduling)
- Secrets Manager (Storing API Tokens)
- Codepipelne (Build and deploy app changes)
- Github Actions (Build and test app changes)

---
## Architecture Overview

- **Lambda A**: Randomly generates results and orders.
- **Lambda B**: Processes each order, saves accepted results to S3, raises error for rejected orders.
- **API Gateway**: Exposes a POST endpoint `/orders` for submitting orders, protected by a request-based Lambda JWT authorizer.
- **API Lambda (post_lambda)**: Handles POST requests, validates and stores orders in DynamoDB with 24h TTL.
  - Create Request based Authorizer Lambda function.
  - Create Auth Lambda Layer to provide custom PyJWT package for the authorizer Lambda function.
  - Generate a token an store in Secrets Manager attach ARN as env var on Authorizer Lambda function.
  - Create Authentication Bearer Token to connect to API Gateway
- **DynamoDB Table**: Stores incoming orders, automatically expiring them after 24 hours.
- **S3 Bucket**: Stores processed order results.
- **Step Functions State Machine**: Orchestrates the data pipeline:
  - Invokes Lambda A until results are ready.
  - For each order, invokes Lambda B.
  - On Lambda B error, sends notification to SNS.
- **SNS Topic**: Simulates Slack notifications for errors.
- **EventBridge Rule**: Triggers the Step Function pipeline every 5 minutes.
- **CodePipeline**: Builds and deploys app code as per environment upon every push to main/master.
- **Github Actions**: Builds and tests app code on every push to main/master.

---
## Deployment

**Steps to deploy app using default AWS credentials.**

**Automated deployment steps:**

1. **Set your JWT secret token:**
   ```sh
   export SECRET_TOKEN='your-jwt-secret-value-here'
   ```

2. **Run the deployment script:**
   ```sh
   chmod +x deploy.sh
   ./deploy.sh
   ```

**Manual deployment steps:**

1. **Create JWT Secret in AWS Secrets Manager:**
   ```sh
   cd util/create_api_token
   python3 create_secret.py
   ```

2. **Change directory**
   ```sh
   cd entrix/
   npm install
   ```
3. **Install dependencies:**
   ```sh
   cd entrix/
   npm install
   ```
4. **Build the CDK app:**
   ```sh
   npm run build
   ```
5. **Install PyJWT as a Lambda Layer:**
   ```sh
   mkdir -p ../src/auth_lambda_layer/python
   pip3 install pyjwt -t ../src/auth_lambda_layer/python
   ```
6. **Deploy the stack:**
   ```sh
   npx cdk deploy
   ```

**Other CDK commands to run project locally**

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template

---
## CI/CD Pipelines

This project uses two separate pipelines to automatically build, test and deploy app code:

- **1. GitHub Actions** (`.github/workflows/pipeline.yaml`): Runs on every push or pull request to `main`. It builds and tests the CDK app, but does not deploy to AWS. This ensures code quality and correctness before deployment.
- **2. AWS CodePipeline (CDK Pipelines)**: Defined in `entrix/lib/pipeline-stack.ts` using the modern `@aws-cdk/pipelines` module. This pipeline is self-mutating and deploys the CDK app to AWS automatically on merges to `main`. It updates itself if you change the pipeline definition.

**Usage Summary:**
- GitHub Actions = Build & Test (CI)
- CodePipeline (CDK Pipelines) = Deploy (CD)
- 
**Note:** You will have to create **codestar/codebuild** connection manually for it to referenced in Codepipeline code.

---
## Post Lambda API Usage

- **Endpoint:** `POST /orders`
- **Authorization:** Requires a valid JWT Request Token in the `Authorization` header.
- **Request Body Example:**
  ```json
  [
    { "record_id": "unique_id_1", "parameter_1": "abc", "parameter_2": 4 },
    { "record_id": "unique_id_2", "parameter_1": "def", "parameter_2": 2.1 }
  ]
  ```
- **Effect:** Records are stored in DynamoDB and will expire after 24 hours.
- **Limitations:** Dynamodb does support float values hence the Lambda B has functionality to covert it to int.

## API Gateway Authentication & Testing

### Generating a JWT Token for API Authentication

You can use the provided utility in `util/create_api_token` to generate a valid JWT token for testing the API Gateway Lambda authorizer.

  **Steps:**

  1. **Install dependencies:**
     ```sh
     cd util/create_api_token
     pip3 install -r util/create_api_token/requirements-secret.txt
     ```
  2. **Generate a JWT token:**
     ```sh
      python3 util/create_api_token/generate_auth_token_ssm.py # if you already know the token

      OR

     python3 util/create_api_token/generate_auth_token_local.py # if you already know the token
     ```
     These scripts will print a valid JWT token to the console.

  3. **Use the token in your API requests:**
     - Add the following header to your requests:
       ```
       Authorization: Bearer <your-jwt-token>
       ```

  4. **Testing API Access**

     **Option 1. Testing with Curl**

     ```sh
     curl -X POST \
       https://<api-id>.execute-api.eu-west-1.amazonaws.com/prod/orders \
       -H "Authorization: Bearer <your-jwt-token>" \
       -H "Content-Type: application/json" \
       -d '[{"record_id": "unique_id_1", "parameter_1": "abc", "parameter_2": 4}]'
     ```

     **Option 2. Testing with Postman**

     1. Create a new `POST` request to your API endpoint.
     2. In the "Headers" tab, add:
        - Key: `Authorization`
        - Value: `Bearer <your-jwt-token>`
     3. In the "Body" tab, select "raw" and "JSON", and enter your order array.
     4. Send the request.

  For troubleshooting, check CloudWatch logs for the authorizer Lambda for error details.

---
