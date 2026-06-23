---
name: jeff-skill-aws-cdk-project
description: Configure or update AWS CDK TypeScript projects with an opinionated layout, required dependencies, scripts, and .env usage. Use when a repo should contain a CDK project. CDK app code should live in a `cdk/` folder off the root of the project with strict dependency and file structure conventions.
---

This is an opinionated view for how AWS CDK projects should be configured and maintained.

## Prerequisites

Before proceeding:

1. Ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.
2. Ensure prettier is installed using the `jeff-skill-install-prettier` skill.
3. Use WebSearch to verify current versions:
   - "AWS CDK latest version [current-year]"
   - "TypeScript latest version [current-year]"
   - "vitest latest version [current-year]"
   - "constructs library latest version [current-year]"
   - Visit https://nodejs.org/en to find the current Node.js LTS major version (look for the "LTS" badge)
   - Update all version numbers in examples below with verified versions
   - DO NOT skip this step. DO NOT guess at version numbers.

## Goals

- Enforce a single CDK app under `cdk/` at repository root
- Keep dependencies minimal and deliberate
- Require environment configuration via `.env`
- Encourage single-stack layout with construct-per-file structure
- Make build/test/deploy repeatable and auditable

## Required Layout

### Repo Structure

- CDK app must live at `cdk/` in the project root
- `cdk/bin/` contains only a single app entrypoint (e.g., `app.ts`)
- `cdk/lib/` typically contains a single stack file (e.g., `stack.ts`) (if you're explicitly asked to do something different, get confirmation about it first)
- Each construct lives in its own file under `cdk/lib/` (or `cdk/lib/constructs` if the project is huge with 30+ constructs and has multiple stacks)

### Environment Files

- `cdk/.env`
- `cdk/.env.example`

These must be used for common build/deploy arguments instead of hardcoding in the code (e.g., API Gateway rate limits, AWS account, alarm periods, allowed Cognito origins, etc.).

**Never hardcode AWS ARNs or account IDs in source.** Always load them from environment variables via `.env` or from Secrets Manager/SSM.

### Unit tests requirements

- Use vitest for unit tests
- Use `vitest.config.ts` for test configurations (like coverage thresholds, test environment, etc...)
- Unit tests must exist for all code. Include coverage reports and ensure coverage is at least 80%
- Tests must assert configuration expectations, such as:
  - Alarms configured for all infrastructure
  - API Gateway always has a rate limit enforced
  - CloudWatch log LogGroups always have retention set to exactly 5 days (`RetentionDays.FIVE_DAYS`)
  - Lambdas always have memory and timeout explicitly set
  - DynamoDB tables always have point-in-time recovery enabled
  - All resources have `removalPolicy: RemovalPolicy.DESTROY`
  - No hardcoded AWS ARNs or account IDs anywhere in source
  - IAM roles have least-privilege permissions and no \* references to refer to actions or resources (unless that's the best practice way for a specific service or permission)
  - etc...

- Use a dedicated test folder to scale cleanly:
  - `cdk/test/` for unit tests
  - `cdk/test/constructs/` for construct tests
  - `cdk/test/stack/` for stack-level assertions

- Example `stack.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { App } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { MyAppStack } from '../../lib/stack';

describe('MyAppStack', () => {
  it('applies API Gateway rate limits', () => {
    const app = new App();
    const stack = new MyAppStack(app, 'TestStack');
    const template = Template.fromStack(stack);

    template.hasResourceProperties('AWS::ApiGateway::Stage', {
      MethodSettings: [
        {
          ThrottlingRateLimit: 10,
          ThrottlingBurstLimit: 20
        }
      ]
    });
  });
});
```

- Best‑Practice Notes
  - Keep tests close to what you assert (e.g., API Gateway throttling, alarms, IAM policies)
  - Use `Template.fromStack` for deterministic assertions of CFN config
  - Keep coverage focused on `lib/` and `bin/` to avoid noise
  - Prefer vitest run --coverage in CI for reproducible results

## Package.json

### Dependencies

Only these are required by default. Any additional pinned dependency must be scrutinized or confirmed with the user.

Use a WebSearch to replace `<latest stable>` below with the actual latest version numbers. Do not skip or guess at version numbers, always use the WebSearch to verify.

```json
"dependencies": {
  "aws-cdk-lib": "<latest stable>",
  "constructs": "<latest stable>",
  "dotenv": "<latest stable>"
},
```

### Dev dependencies

This is less strict but still be deliberate and do not introduce unnecessary dependencies.

Also always include `source-map-support` as a `devDependencies` for better error stack traces in CDK apps, it's only used for test/dev situations and won't be part of the production build so it should be a dev dependency:

```json
"devDependencies": {
  ...
  "source-map-support": "<latest stable>"
  ...
}
```

### Node Version Enforcement

Create `.nvmrc` at the repo root with the current Node LTS major version (visit https://nodejs.org/en and look for the "LTS" badge):

```
<NODE_LTS>
```

Create `.npmrc` in `cdk/` to enforce the Node version:

```
engine-strict=true
```

Add an `engines` field to `cdk/package.json` (replacing `<NODE_LTS>` with the current LTS major version):

```json
"engines": {
  "node": ">= <NODE_LTS>.0.0"
}
```

With `engine-strict=true`, any `npm` command on the wrong Node version will error immediately instead of silently corrupting the lock file.

Configure the session-start hook using the `session-start-hook` skill so that Claude Code web sessions automatically install the current Node LTS version at container startup.

### npm ci vs npm install

- **Use `npm ci`** in CI pipelines, fresh checkouts, and Claude Code web sessions. It installs exactly what is in `package-lock.json`, never modifies the lock file, and fails fast if the lock file is missing or inconsistent.
- **Use `npm install <package>`** only when intentionally adding or updating a dependency.
- **Never run bare `npm install`** (no arguments) in CI or fresh environments — it re-resolves versions and may silently rewrite the lock file, which defeats reproducibility and can break CI.

### Scripts

Prefer npx cdk or local cdk scripts; do not rely on global install.

The `scripts` section in `package.json` should include helpful commands like the following (always include a command that will build + deploy in one step, and a command that will clean + build + deploy in one step):

```json
"scripts": {
  "build": "tsc",
  "watch": "tsc -w",
  "deploy": "npm run build && cdk deploy",
  "diff": "cdk diff",
  "synth": "cdk synth",
  "destroy": "cdk destroy",
  "clean": "rm -rf dist",
  "clean:all": "rm -rf dist node_modules",
  "test": "vitest",
  "test:run": "vitest run",
  "test:coverage": "vitest run --coverage"
}
```

## CDK App Code

### Entrypoint

App Entrypoint (`cdk/bin/app.ts`)

Only one app entrypoint is allowed. It should follow this pattern:

```
import * as cdk from 'aws-cdk-lib';
import * as dotenv from 'dotenv';
import * as path from 'path';
import { MyAppStack } from '../lib/stack';

// This works whether you run from repo root or cdk/.
dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

const app = new cdk.App();

new MyAppStack(app, 'MyAppStack', {
  env: {
    account: process.env.AWS_ACCOUNT,
    region: process.env.AWS_REGION,
    // ...other args too
  }
});
```

### Stack file

Only one stack file is typical, but leave room for more if needed or requested (but always double check if really necessary as that is non-standard).

```
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class MyAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    // refer to constructs part of the stack
  }
}
```

### Constructs

Each construct should be in its own file.

Example lambda construct:

```
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

interface Lambda1ConstructProps {
  myTable: dynamodb.Table;
}

export class Lambda1Construct extends Construct {
  constructor(scope: Construct, id: string, props: Lambda1ConstructProps) {
    super(scope, id);
  }
}
```

Example DynamoDB construct:

```
import { Construct } from 'constructs';

export class DynamoDBConstruct extends Construct {
  constructor(scope: Construct, id: string) {
    super(scope, id);
    // tables, indexes, etc...
  }
}
```

It's ok to combine multiple Lambda functions in the same Lambda construct file if they are closely related in business purpose. Same idea applies to other resources (multiple DynamoDB tables can all live in the same construct file if they are closely related in business purpose). But typically do not mix resources in a single construct file (like mixing Lambda and DynamoDB resources in the same construct file).

## Naming Conventions

All CDK infrastructure identifiers (construct IDs, resource logical IDs) must use PascalCase.

```typescript
// GOOD
new dynamodb.Table(this, 'UsersTable', { ... });
new logs.LogGroup(this, 'ApiLogGroup', { ... });
new lambda.Function(this, 'ProcessOrderFunction', { ... });
new MyAppStack(app, 'MyAppStack', { ... });

// BAD — lowercase, kebab-case, snake_case
new dynamodb.Table(this, 'users-table', { ... });
new logs.LogGroup(this, 'apiLogGroup', { ... });
new lambda.Function(this, 'process_order_function', { ... });
```

This applies to:

- Stack IDs passed to `new MyStack(app, 'StackId', ...)`
- Construct IDs passed to `super(scope, 'ConstructId')` and `new SomeConstruct(this, 'ConstructId', ...)`
- All logical resource IDs passed to AWS CDK resource constructors

## Required CDK Defaults

Every CDK construct must follow these non-negotiable defaults:

### Removal Policy

Always set `removalPolicy: cdk.RemovalPolicy.DESTROY` on all resources. This prevents orphaned resources in dev/test environments:

```typescript
const table = new dynamodb.Table(this, 'MyTable', {
  partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
  removalPolicy: cdk.RemovalPolicy.DESTROY
});
```

### CloudWatch Log Retention

Always set log retention to 5 days. Never leave it unlimited:

```typescript
import * as logs from 'aws-cdk-lib/aws-logs';

const logGroup = new logs.LogGroup(this, 'MyLogGroup', {
  retention: logs.RetentionDays.FIVE_DAYS,
  removalPolicy: cdk.RemovalPolicy.DESTROY
});
```

### No Hardcoded ARNs, Account IDs, or External Resource Names

Never hardcode AWS ARNs, account IDs, region-specific identifiers, or names of resources defined outside this stack. Load them from `.env` via `process.env`:

```typescript
// BAD — never do this
const roleArn = 'arn:aws:iam::123456789012:role/MyRole';
const unsubUrl = 'https://abc123.execute-api.us-east-1.amazonaws.com/unsubscribe';

// GOOD — load from environment
const roleArn = process.env.MY_ROLE_ARN!;
const unsubUrl = process.env.UNSUBSCRIBE_BASE_URL!;
```

Resource names defined within the same stack (e.g., `'WordBank'` for a DynamoDB table created in this stack) may be hardcoded as constants — no env var needed.

### IAM: Always Use addToPrincipalPolicy with Exact Actions

Always use `addToPrincipalPolicy` with the minimum exact actions required. Never use CDK L2 grant methods — they grant broader permissions than needed and violate least-privilege:

```typescript
// BAD — attachInlinePolicy creates an extra CloudFormation AWS::IAM::Policy resource
// and bypasses CDK dependency tracking
role.attachInlinePolicy(new iam.Policy(this, 'MyPolicy', { ... }));

// BAD — L2 grant methods grant overly broad action sets
myTable.grantReadData(myLambda);           // grants GetItem, BatchGetItem, Query, Scan, ConditionCheckItem
myTable.grantReadWriteData(myLambda);      // grants all of the above + PutItem, UpdateItem, DeleteItem, BatchWriteItem
myQueue.grantSendMessages(myLambda);       // grants SendMessage + GetQueueAttributes + GetQueueUrl
myQueue.grantConsumeMessages(myLambda);    // grants more than just ReceiveMessage + DeleteMessage

// GOOD — exact actions only, using CDK construct properties for ARNs
myLambda.role!.addToPrincipalPolicy(new iam.PolicyStatement({
  sid: 'MyTableQuery',
  effect: iam.Effect.ALLOW,
  actions: ['dynamodb:Query'],             // only what's needed
  resources: [myTable.tableArn]            // use construct property, not a hand-crafted ARN string
}));

myLambda.role!.addToPrincipalPolicy(new iam.PolicyStatement({
  sid: 'MyQueueSend',
  effect: iam.Effect.ALLOW,
  actions: ['sqs:SendMessage'],            // only what's needed
  resources: [myQueue.queueArn]
}));

// GOOD — for external resources not defined in this stack, import first to get the ARN
const externalTable = dynamodb.Table.fromTableName(this, 'ExternalTable', 'KnownTableName');
myLambda.role!.addToPrincipalPolicy(new iam.PolicyStatement({
  sid: 'ExternalTableRead',
  effect: iam.Effect.ALLOW,
  actions: ['dynamodb:GetItem'],
  resources: [externalTable.tableArn]
}));
```

## GitHub Actions

- Create a GitHub action workflow for the CDK that does a clean build + deploy (so run a build, the tests, assert coverage requirements met, synth, build, deploy, etc.) and ensure it runs on every push to main.
- The GitHub action should run the unit tests and enforce code coverage requirements on every PR push.

## Integration with Other Skills

## Additional resources
