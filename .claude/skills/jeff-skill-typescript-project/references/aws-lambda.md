# AWS Lambda Development

When building AWS Lambda functions with TypeScript, use **AWS Lambda Powertools for TypeScript**:

- **Logger** for structured JSON logging with the Lambda context injected (`logger.addContext(context)`); never `console.log`.
- **Tracer** (X-Ray) only when explicitly requested.
- **Parameters** for SSM Parameter Store and Secrets Manager; **Idempotency** where retries could double-apply.
- Type events with `@types/aws-lambda`, preferring `APIGatewayProxyEventV2` / `APIGatewayProxyResultV2`.
- Cold starts: minimal dependencies, static imports at the top, no lazy loading.
- ARM64 (Graviton); explicit memory and timeout; configuration from environment variables.

## Handling Multiple Routes

**Recommended: Manual Path Checking (Cold Start Optimized)**

For 2-5 routes, use simple path checking - no extra dependencies, faster cold starts:

```typescript
import type { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { Logger } from '@aws-lambda-powertools/logger';

const logger = new Logger();

export const handler = async (event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> => {
  const path = event.rawPath || event.requestContext.http.path;
  const method = event.requestContext.http.method;

  logger.info('Request received', { path, method });

  // Parse body once
  let body: unknown;
  try {
    body = event.body ? JSON.parse(event.body) : {};
  } catch {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  // Route handling
  if (method === 'GET' && path === '/users') {
    return handleGetUsers();
  } else if (method === 'POST' && path === '/users') {
    return handleCreateUser(body);
  } else if (method === 'GET' && path.startsWith('/users/')) {
    const id = path.split('/')[2];
    return handleGetUser(id);
  }

  return { statusCode: 404, body: JSON.stringify({ error: 'Not found' }) };
};

async function handleGetUsers(): Promise<APIGatewayProxyResultV2> {
  // Implementation
  return { statusCode: 200, body: JSON.stringify({ users: [] }) };
}

async function handleCreateUser(body: unknown): Promise<APIGatewayProxyResultV2> {
  // Implementation
  return { statusCode: 201, body: JSON.stringify({ user: body }) };
}

async function handleGetUser(id: string): Promise<APIGatewayProxyResultV2> {
  // Implementation
  return { statusCode: 200, body: JSON.stringify({ user: { id } }) };
}
```

**Last Resort: Event Handler (Only for 10+ routes)**

If a single Lambda needs 10+ routes, that usually means it should be split into focused functions, or API Gateway should route to separate Lambdas. Only when splitting isn't an option, use `@aws-lambda-powertools/event-handler` — check its current docs for the router API rather than writing it from memory.

## Installing Powertools

```bash
# Core (always)
npm install @aws-lambda-powertools/logger
npm install -D @types/aws-lambda

# Tracer (only when X-Ray is explicitly requested)
# npm install @aws-lambda-powertools/tracer

# Event Handler (only if you have 10+ routes - see routing section above)
# npm install @aws-lambda-powertools/event-handler
```
