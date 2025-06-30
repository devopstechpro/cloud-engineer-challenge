# Cloud Engineer Challenge / Entrix AWS Infrastructure using CDK

This project defines the infrastructure for the Entrix energy market auction service using AWS CDK (TypeScript). The solution is fully serverless, secure, and designed for easy extensibility and robust automation.

---

## Architecture Overview

- **API Gateway**: Exposes a POST endpoint `/orders` for submitting orders, protected by a request-based Lambda JWT authorizer.
- **API Lambda (post_lambda)**: Handles POST requests, validates and stores orders in DynamoDB with 24h TTL.
- **DynamoDB Table**: Stores incoming orders, automatically expiring them after 24 hours.
- **S3 Bucket**: Stores processed order results.
- **Step Functions State Machine**: Orchestrates the data pipeline:
  - Invokes Lambda A until results are ready.
  - For each order, invokes Lambda B.
  - On Lambda B error, sends notification to SNS.
- **Lambda A**: Randomly generates results and orders.
- **Lambda B**: Processes each order, saves accepted results to S3, raises error for rejected orders.
- **SNS Topic**: Simulates Slack notifications for errors.
- **EventBridge Rule**: Triggers the Step Function pipeline every 5 minutes.
- **Auth Lambda Layer**: Provides PyJWT package for the authorizer Lambda function.
- **CodePipeline**: Builds and deploys app code as per environment upon every push to main/master.
- **Github Actions**: Builds and tests app code on every push to main/master.

---

## Deployment 

*Build test and deploy from local system.*

1. **Change directory**
   ```sh
   cd entrix/
   npm install
   ```
2. **Install dependencies:**
   ```sh
   cd entrix/
   npm install
   ```
3. **Build the CDK app:**
   ```sh
   npm run build
   ```
4. **Install PyJWT as a Lambda Layer:**
   ```sh
   mkdir -p ../src/auth_lambda_layer/python
   pip3 install pyjwt -t ../src/auth_lambda_layer/python
   ```
5. **Deploy the stack:**
   ```sh
   npx cdk deploy
   ```

## CI/CD Pipelines

This project uses two separate pipelines to automatically deploy app code:

- **GitHub Actions** (`.github/workflows/pipeline.yaml`): Runs on every push or pull request to `main`. It builds and tests the CDK app, but does not deploy to AWS. This ensures code quality and correctness before deployment.
- **AWS CodePipeline (CDK Pipelines)**: Defined in `entrix/lib/pipeline-stack.ts` using the modern `@aws-cdk/pipelines` module. This pipeline is self-mutating and deploys the CDK app to AWS automatically on merges to `main`. It updates itself if you change the pipeline definition.

**Summary:**
- GitHub Actions = Build & Test (CI)
- CodePipeline (CDK Pipelines) = Deploy (CD)

*Note:* You will have to create codestar/codebuild connection manually for it to referenced in Codepipeline code.

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


## API Authentication & Testing

### Generating a JWT Token for API Authentication

You can use the provided utility in `src/create_auth_lambda_token` to generate a valid JWT token for testing the API Gateway Lambda authorizer.

#### Steps:

1. **Install dependencies:**
   ```sh
   cd src/create_auth_lambda_token
   pip install -r requirements.txt
   ```
2. **Generate a JWT token:**
   ```sh
   python3 token.py
   ```
   The script will print a valid JWT token to the console.

3. **Use the token in your API requests:**
   - Add the following header to your requests:
     ```
     Authorization: Bearer <your-jwt-token>
     ```

Return to the project root to continue with deployment or other tasks.


### Testing with curl

```sh
curl -X POST \
  https://<api-id>.execute-api.eu-west-1.amazonaws.com/prod/orders \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '[{"record_id": "unique_id_1", "parameter_1": "abc", "parameter_2": 4}]'
```

### Testing with Postman

1. Create a new `POST` request to your API endpoint.
2. In the "Headers" tab, add:
   - Key: `Authorization`
   - Value: `Bearer <your-jwt-token>`
3. In the "Body" tab, select "raw" and "JSON", and enter your order array.
4. Send the request.

For troubleshooting, check CloudWatch logs for the authorizer Lambda for error details.

---

## Data Pipeline (Step Function)

- **Triggered:** Every 5 minutes by EventBridge.
- **Process:**
  1. Lambda A is invoked. If `results: false`, it is retried until `results: true`.
  2. For each order in Lambda A's output, Lambda B is invoked.
  3. If Lambda B raises an error (order is rejected), a notification is sent to SNS (simulated Slack).
  4. Accepted orders are saved to S3.

---

## List of services used

- API Gateway REST API (with JWT authorizer)
- Lambda Functions (API, A, B, authorizer)
- Lambda Layer (PyJWT)
- DynamoDB Table (with TTL)
- S3 Bucket (for order results)
- Step Functions State Machine
- SNS Topic (for notifications)
- EventBridge Rule (for scheduling)

---

## NPM/CDK commands to run project locally

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
---


