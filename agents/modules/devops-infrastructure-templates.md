# DevOps Infrastructure — Templates Module

Load this module when you need a complete, ready-to-adapt template for a Dockerfile, CI/CD pipeline, or Terraform configuration. These are starting points — always adapt to the project's actual structure and requirements.

---

## Multi-Stage Dockerfile (Node.js)

```dockerfile
# Multi-stage build: builder produces artifacts, runner is the minimal production image.
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

# Non-root user (required — never run as root in production)
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 appuser

COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER appuser
EXPOSE 3000

# Health check so orchestrators know when the container is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "dist/index.js"]
```

**Key decisions to adapt:**
- Replace `npm run build` output path (`dist/`) with the actual build output directory
- Set `EXPOSE` to the actual application port
- Adjust `HEALTHCHECK` path to the actual health endpoint
- For Next.js apps, copy `.next/` instead of `dist/` and use `npm start`

---

## GitHub Actions: CI + Deploy to AWS ECS

```yaml
name: Deploy Production

on:
  push:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app          # replace with actual ECR repo name
  ECS_CLUSTER: production         # replace with actual ECS cluster name
  ECS_SERVICE: my-app             # replace with actual ECS service name

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    environment: production        # requires approval if configured
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          # Also tag as latest for reference (never deploy using latest tag)
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG \
            $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Deploy to ECS (force new deployment)
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE }} \
            --force-new-deployment

      - name: Wait for deployment to stabilize
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE }}
```

**Pipeline best practices embodied here:**
- Tests run before any deployment step (fail fast)
- Node dependency cache speeds CI
- Image tagged with commit SHA for traceability (not `latest`)
- Deployment waits for ECS service to stabilize before marking success
- Secrets via GitHub Secrets — never in the YAML file

---

## Terraform with Remote State (AWS ECS + ALB)

```hcl
# terraform/main.tf

terraform {
  required_version = ">= 1.0"

  # Remote state — never store state in git
  backend "s3" {
    bucket         = "my-app-terraform-state"   # replace with actual bucket
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"     # enables state locking
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ECS Cluster with Container Insights enabled
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true   # prevents accidental destroy in production

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

**Companion variables file (terraform/variables.tf):**

```hcl
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used as prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "environment must be dev, staging, or production"
  }
}
```

**IaC principles:**
- State stored remotely with locking (DynamoDB prevents concurrent applies)
- All resources tagged with environment and `ManagedBy = "terraform"`
- Variables file separates config from logic
- `deletion_protection = true` on production resources
- Always run `terraform plan` and review the diff before `terraform apply`

---

## Health Check Endpoint (Express / Node.js)

```typescript
// src/routes/health.ts
import { Router } from 'express';
import { db } from '../services/database';

const router = Router();

router.get('/health', async (req, res) => {
  const checks: Record<string, 'ok' | 'error'> = {};

  try {
    await db.$queryRaw`SELECT 1`;
    checks.database = 'ok';
  } catch {
    checks.database = 'error';
  }

  const healthy = Object.values(checks).every(v => v === 'ok');

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    checks,
  });
});

export default router;
```

**Register before auth middleware** so load balancers and orchestrators can reach it without credentials.

---

## Structured Logging (Winston)

```typescript
// src/services/logger.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()   // structured JSON — parseable by CloudWatch, DataDog, etc.
  ),
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'api',
    environment: process.env.NODE_ENV,
  },
  transports: [
    new winston.transports.Console(),
    ...(process.env.NODE_ENV === 'production'
      ? [new winston.transports.File({ filename: 'logs/error.log', level: 'error' })]
      : []),
  ],
});

// Usage examples
// logger.info('User authenticated', { userId, ip: req.ip });
// logger.error('Payment failed', { orderId, error: err.message });
// NEVER log: passwords, tokens, full credit card numbers, SSNs
```

---

## Environment Variables Template (.env.example)

```bash
# .env.example — commit this file; NEVER commit .env
# Copy to .env and fill in values for local development.
# Production values come from secrets manager or platform secrets.

# Application
NODE_ENV=development
PORT=4000
LOG_LEVEL=info
SERVICE_NAME=api

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=20

# AWS
AWS_REGION=us-east-1
AWS_S3_BUCKET=my-app-uploads

# Auth (use secrets manager in production — never commit real values)
JWT_SECRET=<local-dev-secret-only>
JWT_REFRESH_SECRET=<local-dev-secret-only>

# Monitoring (optional in dev)
SENTRY_DSN=
DATADOG_API_KEY=
```
