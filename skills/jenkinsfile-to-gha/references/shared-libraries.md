# Shared Libraries → Reusable Workflows

Jenkins shared libraries are a common pattern for standardizing pipelines across teams. The GitHub Actions equivalent is **reusable workflows**.

## Identifying Shared Library Usage

Look for these patterns in Jenkinsfiles:

```groovy
// Library import
@Library(['my-pipeline-lib@v2.0']) _

// Initialization
Jenkinsfile.init(this)

// Plugin initialization
SomePlugin.init()
AnotherPlugin.init()

// Stage builders (fluent API pattern)
def validate = new ValidateStage()
def deployQa = new DeployStage('qa')
def deployProd = new DeployStage('prod')

validate.then(deployQa)
        .then(deployProd)
        .build()
```

## Interactive Questions

When you detect a shared library, ask:

1. **Equivalent workflow exists?**
   - "I see you're using `my-pipeline-lib`. Do you have an equivalent reusable workflow in GitHub Actions?"
   - "If yes, what's the reference? (e.g., `org/workflows/.github/workflows/deploy.yml@v1`)"

2. **If no equivalent exists:**
   - "Should I generate a standalone workflow that replicates this behavior?"
   - "Or create a reusable workflow you can centralize later?"

3. **Plugin mapping:**
   - "The library uses these plugins: `CredentialsPlugin`, `WithAwsPlugin`. How should I handle these?"
   - Common mappings: AWS plugin → OIDC auth, Credentials → GitHub Secrets

4. **Stage chaining:**
   - "The pipeline chains environments: qa → uat → prod. Should each be a separate job with `needs:` dependencies?"
   - "Which environments require manual approval?"

## Conversion Patterns

### Option A: Call Existing Reusable Workflow

**Jenkins:**
```groovy
@Library(['deploy-pipeline@v3']) _

Jenkinsfile.init(this)
AwsPlugin.init()
ApprovalPlugin.init()

def validate = new ValidateStage()
def deployDev = new DeployStage('dev')
def deployStaging = new DeployStage('staging')
def deployProd = new DeployStage('prod')

validate.then(deployDev)
        .then(deployStaging)
        .then(deployProd)
        .build()
```

**GitHub Actions:**
```yaml
name: Deploy Pipeline

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    uses: org/platform-workflows/.github/workflows/validate.yml@v3
    with:
      working-directory: ./infra

  deploy-dev:
    needs: validate
    if: github.ref == 'refs/heads/main'
    uses: org/platform-workflows/.github/workflows/deploy.yml@v3
    with:
      environment: dev
    secrets: inherit

  deploy-staging:
    needs: deploy-dev
    uses: org/platform-workflows/.github/workflows/deploy.yml@v3
    with:
      environment: staging
    secrets: inherit

  deploy-prod:
    needs: deploy-staging
    environment: production  # Requires approval
    uses: org/platform-workflows/.github/workflows/deploy.yml@v3
    with:
      environment: prod
    secrets: inherit
```

### Option B: Generate Standalone Workflow

If no reusable workflow exists, expand the library's behavior inline:

```yaml
name: Deploy Pipeline

on:
  push:
    branches: [main]
  pull_request:

env:
  AWS_REGION: us-east-1

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate
        run: ./scripts/validate.sh

  deploy-dev:
    needs: validate
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: dev
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy
        run: ./scripts/deploy.sh dev
        env:
          ENVIRONMENT: dev

  # ... repeat for staging, prod with appropriate approvals
```

## Feature Mapping

| Library Feature | GitHub Actions Equivalent |
|-----------------|---------------------------|
| Sequential stages (`.then()`) | Jobs with `needs:` |
| Manual approval gates | `environment:` with required reviewers |
| Credentials injection | `secrets: inherit` or explicit secrets |
| AWS role assumption | OIDC + `aws-actions/configure-aws-credentials` |
| Environment variables | `env:` or `vars.*` context |
| Branch-based behavior | `if: github.ref == 'refs/heads/main'` |
| Plugin initialization | Action setup steps or reusable workflow inputs |
| Parameter Store | AWS SSM action or workflow inputs |

## Team Configuration File

For teams with internal reusable workflows, suggest creating a mapping file:

```yaml
# .github/workflow-mappings.yml (for documentation/tooling)
shared_libraries:
  deploy-pipeline:
    github_workflow: org/platform-workflows/.github/workflows/deploy.yml@v3
    stage_mappings:
      ValidateStage: validate.yml
      DeployStage: deploy.yml
    plugin_mappings:
      AwsPlugin: uses OIDC authentication
      ApprovalPlugin: uses GitHub Environments
    environments:
      dev: { approval: false }
      staging: { approval: false }
      prod: { approval: true, reviewers: ["platform-team"] }
```

This helps maintain consistency when converting multiple Jenkinsfiles that use the same library.
