---
name: jenkinsfile-to-gha
description: Convert Jenkins pipelines (Jenkinsfiles) to GitHub Actions workflows. Use when migrating CI/CD from Jenkins to GitHub Actions, or when user provides a Jenkinsfile and wants a GHA workflow.
license: MIT
compatibility: Works with Claude Code and similar agents. No external tools required.
metadata:
  author: kenny
  version: "1.0"
---

# Jenkinsfile to GitHub Actions Converter

Convert Jenkins Declarative and Scripted Pipelines to GitHub Actions workflows.

## When to Use This Skill

- User provides a Jenkinsfile and wants GitHub Actions equivalent
- User asks to migrate from Jenkins to GitHub Actions
- User mentions Jenkins pipeline conversion
- User has CI/CD in Jenkins and wants to move to GHA

## Conversion Workflow

### 1. Analyze the Jenkinsfile

Identify:
- Pipeline type (Declarative vs Scripted)
- Stages and their purposes
- Build tools used (Maven, Gradle, npm, etc.)
- Jenkins plugins referenced
- Environment variables and credentials
- Triggers (cron, webhooks, SCM polling)
- Post-build actions

### 2. Map Core Concepts

| Jenkins | GitHub Actions | Notes |
|---------|----------------|-------|
| `pipeline {}` | Workflow file | `.github/workflows/*.yml` |
| `agent any` | `runs-on: ubuntu-latest` | Or specific runner |
| `agent { docker { image 'x' } }` | `container: x` | Under job |
| `stages {}` | `jobs:` | Each stage → job (or steps) |
| `stage('X') { steps {} }` | `jobs.X.steps:` | Or single job with step groups |
| `steps {}` | `steps:` | List of actions/run commands |
| `environment {}` | `env:` | At workflow, job, or step level |
| `parameters {}` | `workflow_dispatch.inputs:` | Manual trigger inputs |
| `triggers { cron('...') }` | `on: schedule:` | Cron syntax slightly different |
| `triggers { pollSCM('...') }` | `on: push/pull_request` | Event-based instead |
| `when { branch 'main' }` | `if: github.ref == 'refs/heads/main'` | Conditional execution |
| `post { always {} }` | Step with `if: always()` | Or job-level |
| `post { success {} }` | Step with `if: success()` | Default behavior |
| `post { failure {} }` | Step with `if: failure()` | On failure only |
| `parallel {}` | Multiple jobs or `matrix` | Jobs run in parallel by default |
| `options { timeout(...) }` | `timeout-minutes:` | At job level |
| `options { retry(N) }` | `continue-on-error` + custom logic | No direct equivalent |

### 3. Map Environment Variables

| Jenkins Variable | GitHub Actions Equivalent |
|------------------|---------------------------|
| `BUILD_NUMBER` | `${{ github.run_number }}` |
| `BUILD_ID` | `${{ github.run_id }}` |
| `JOB_NAME` | `${{ github.job }}` |
| `BRANCH_NAME` | `${{ github.ref_name }}` |
| `GIT_COMMIT` | `${{ github.sha }}` |
| `GIT_BRANCH` | `${{ github.ref }}` |
| `WORKSPACE` | `${{ github.workspace }}` |
| `JENKINS_URL` | `${{ github.server_url }}` |
| `BUILD_URL` | `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}` |
| `JOB_URL` | N/A |
| `NODE_NAME` | `${{ runner.name }}` |
| `EXECUTOR_NUMBER` | N/A |

### 4. Map Common Plugins

| Jenkins Plugin | GitHub Actions Equivalent |
|----------------|---------------------------|
| Git SCM | `actions/checkout@v4` |
| Maven | `run: mvn ...` or custom action |
| Gradle | `gradle/gradle-build-action@v2` |
| NodeJS | `actions/setup-node@v4` |
| Docker | `docker/build-push-action@v5` |
| JUnit | `dorny/test-reporter@v1` or `actions/upload-artifact@v4` |
| Slack Notification | `slackapi/slack-github-action@v1` |
| Email | GitHub notifications or custom |
| SonarQube | `sonarsource/sonarqube-scan-action@v2` |
| Artifactory | `jfrog/setup-jfrog-cli@v3` |
| AWS Steps | `aws-actions/configure-aws-credentials@v4` |
| Kubernetes | `azure/k8s-deploy@v4` or kubectl in run |
| SSH Agent | `webfactory/ssh-agent@v0.8.0` |
| Credentials Binding | `${{ secrets.NAME }}` |
| Timestamper | Built-in (logs have timestamps) |
| AnsiColor | Built-in (ANSI supported) |
| Pipeline Utility Steps | Native shell commands |
| HTTP Request | `run: curl ...` or custom action |

### 5. Map Triggers

**Jenkins:**
```groovy
triggers {
    cron('H 4 * * 1-5')
    pollSCM('H/15 * * * *')
    upstream(upstreamProjects: 'job1,job2', threshold: hudson.model.Result.SUCCESS)
}
```

**GitHub Actions:**
```yaml
on:
  schedule:
    - cron: '0 4 * * 1-5'  # Note: GHA uses standard cron, no 'H'
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_run:
    workflows: ["Job1", "Job2"]
    types: [completed]
```

### 6. Handle Credentials

**Jenkins:**
```groovy
withCredentials([usernamePassword(credentialsId: 'my-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
    sh 'curl -u $USER:$PASS ...'
}
```

**GitHub Actions:**
```yaml
env:
  USER: ${{ secrets.MY_USER }}
  PASS: ${{ secrets.MY_PASS }}
run: curl -u $USER:$PASS ...
```

## Conversion Patterns

### Simple Pipeline

**Jenkins:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'npm install'
                sh 'npm run build'
            }
        }
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
}
```

**GitHub Actions:**
```yaml
name: CI
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install
      - run: npm run build
      - run: npm test
```

### Multi-Stage with Dependencies

**Jenkins:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh './deploy.sh'
            }
        }
    }
}
```

**GitHub Actions:**
```yaml
name: CI/CD
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - run: mvn package

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - run: mvn test

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
```

### Matrix Builds

**Jenkins:**
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            matrix {
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'linux', 'mac', 'windows'
                    }
                    axis {
                        name 'NODE'
                        values '18', '20'
                    }
                }
                stages {
                    stage('Test Platform') {
                        steps {
                            sh "echo Testing on ${PLATFORM} with Node ${NODE}"
                        }
                    }
                }
            }
        }
    }
}
```

**GitHub Actions:**
```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: echo "Testing on ${{ matrix.os }} with Node ${{ matrix.node }}"
```

### Docker Build & Push

**Jenkins:**
```groovy
pipeline {
    agent any
    environment {
        DOCKER_REGISTRY = 'docker.io'
        IMAGE_NAME = 'myorg/myapp'
    }
    stages {
        stage('Build & Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        docker login -u $DOCKER_USER -p $DOCKER_PASS $DOCKER_REGISTRY
                        docker build -t $IMAGE_NAME:$BUILD_NUMBER .
                        docker push $IMAGE_NAME:$BUILD_NUMBER
                    '''
                }
            }
        }
    }
}
```

**GitHub Actions:**
```yaml
name: Docker Build
on:
  push:
    branches: [main]

env:
  REGISTRY: docker.io
  IMAGE_NAME: myorg/myapp

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.DOCKER_USER }}
          password: ${{ secrets.DOCKER_PASS }}

      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ env.IMAGE_NAME }}:${{ github.run_number }}
```

### Post-Build Actions

**Jenkins:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'dist/**/*'
            junit 'reports/*.xml'
        }
        success {
            slackSend channel: '#builds', message: 'Build succeeded!'
        }
        failure {
            slackSend channel: '#builds', message: 'Build failed!'
        }
    }
}
```

**GitHub Actions:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make build

      # Always run (like post.always)
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: dist
          path: dist/

      - name: Publish Test Results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Tests
          path: reports/*.xml
          reporter: java-junit

      # On success
      - uses: slackapi/slack-github-action@v1
        if: success()
        with:
          channel-id: '#builds'
          slack-message: 'Build succeeded!'
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_TOKEN }}

      # On failure
      - uses: slackapi/slack-github-action@v1
        if: failure()
        with:
          channel-id: '#builds'
          slack-message: 'Build failed!'
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_TOKEN }}
```

## Unsupported Features

These Jenkins features have no direct GHA equivalent:

| Feature | Workaround |
|---------|------------|
| `input` (manual approval) | `environment` with required reviewers |
| Shared Libraries | Composite actions or reusable workflows |
| `lock` (resource locking) | `concurrency` groups (limited) |
| Flyweight executors | N/A - runners are consistent |
| Build distributed across agents | Matrix or separate jobs |
| Fingerprinting | Artifact metadata |
| Email-ext | Use Slack/Discord or third-party |

## Shared Libraries → Reusable Workflows

Jenkins shared libraries are a common pattern for standardizing pipelines across teams. The GitHub Actions equivalent is **reusable workflows**.

### Identifying Shared Library Usage

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

### Interactive Questions for Shared Libraries

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

### Conversion Pattern

**Jenkins Shared Library Pattern:**
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

**Option A: Call Existing Reusable Workflow**
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

**Option B: Generate Standalone Workflow**

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
        run: |
          # Validation logic from library
          ./scripts/validate.sh

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

### Common Library Features → GHA Equivalents

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

### Team Configuration File

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

## Best Practices

1. **Use caching** - Add `actions/cache` for dependencies
2. **Set timeouts** - Always add `timeout-minutes` to prevent runaway jobs
3. **Use concurrency** - Prevent duplicate runs with `concurrency` groups
4. **Artifact between jobs** - Use `actions/upload-artifact` and `actions/download-artifact`
5. **Secret management** - Store credentials in GitHub Secrets
6. **Reusable workflows** - Extract common patterns to `.github/workflows/` reusable workflows
7. **Use specific action versions** - Pin to `@v4` not `@main`

## Action Mirrors & Enterprise Configuration

Many enterprises use internal mirrors of GitHub Actions for security, compliance, or air-gapped environments.

### Interactive Configuration

**Before generating output, ask the user:**

1. **Action source preference:**
   - "Do you use GitHub.com actions directly, or do you have an internal mirror/proxy?"
   - Options: Public GitHub, GitHub Enterprise Server, Artifactory, custom registry

2. **Mirror URL pattern:**
   - "What's your internal action mirror URL pattern?"
   - Example: `ghes.company.com/actions-mirror/` or `artifactory.company.com/github-actions/`

3. **Specific action overrides:**
   - "Are there any actions that should use different sources?"
   - Example: Internal `company/deploy-action` instead of community action

### Rule-Based Action Mapping

Define replacement rules that transform action references:

```yaml
# Example configuration (can be stored in .github/action-mirrors.yml)
action_mirrors:
  # Default prefix for all actions
  default_prefix: "ghes.company.com/actions-mirror/"

  # Rules applied in order (first match wins)
  rules:
    # Mirror all official GitHub actions
    - match: "^actions/"
      replace_prefix: "ghes.company.com/github-actions/"

    # Mirror Docker actions
    - match: "^docker/"
      replace_prefix: "ghes.company.com/docker-actions/"

    # Use internal Slack action
    - match: "^slackapi/slack-github-action"
      replace_with: "company/internal-slack-notify@v2"

    # Keep some actions as-is (allowlist)
    - match: "^company/"
      replace_prefix: ""  # No change

    # Catch-all for third-party actions
    - match: ".*"
      replace_prefix: "ghes.company.com/third-party/"
```

### Applying Mirror Rules

When converting, apply rules to each action reference:

**Input (public):**
```yaml
- uses: actions/checkout@v4
- uses: docker/build-push-action@v5
- uses: slackapi/slack-github-action@v1
```

**Output (with enterprise rules):**
```yaml
- uses: ghes.company.com/github-actions/checkout@v4
- uses: ghes.company.com/docker-actions/build-push-action@v5
- uses: company/internal-slack-notify@v2
```

### Common Enterprise Patterns

| Source | Mirror Pattern | Notes |
|--------|----------------|-------|
| GitHub.com → GHES | `ghes.corp.com/org/repo` | GitHub Enterprise Server |
| GitHub.com → Artifactory | `artifactory.corp.com/github-actions-remote/org/repo` | JFrog Artifactory |
| GitHub.com → Nexus | `nexus.corp.com/repository/github-actions/org/repo` | Sonatype Nexus |
| GitHub.com → GitLab | `gitlab.corp.com/mirrors/github/org/repo` | GitLab mirroring |

### Version Pinning Strategy

Ask about version strategy:

1. **Tag-based** (default): `@v4` - Allows minor updates
2. **SHA-pinned**: `@a]5ac7e51b41094c92402da3b24376905380afc29` - Maximum reproducibility
3. **Floating**: `@main` - Always latest (not recommended for prod)

**For enterprise migrations, recommend SHA pinning:**
```yaml
# Instead of:
- uses: ghes.company.com/github-actions/checkout@v4

# Use:
- uses: ghes.company.com/github-actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
  # v4.1.1 - pinned for reproducibility
```

### Self-Hosted Runners

Enterprise environments often use self-hosted runners:

```yaml
# Instead of:
runs-on: ubuntu-latest

# Use:
runs-on: [self-hosted, linux, x64]
# or
runs-on: company-runner-pool
```

**Ask the user:**
- "Do you use GitHub-hosted runners or self-hosted?"
- "What are your runner labels?"

### Air-Gapped Environments

For fully air-gapped environments:

1. All actions must be pre-synced to internal registry
2. Container images need internal mirrors
3. No external network calls in workflows

```yaml
# Air-gapped example
jobs:
  build:
    runs-on: [self-hosted, air-gapped]
    container:
      image: internal-registry.company.com/node:20
    steps:
      - uses: internal-ghes.company.com/actions/checkout@v4
      - run: npm ci --registry https://npm.company.com
```

## Interactive Conversion

When converting complex pipelines:

1. **Ask about plugins** - "I see you're using the SonarQube plugin. Do you want me to include SonarQube scanning?"
2. **Clarify credentials** - "This pipeline uses credentials 'deploy-key'. What secrets should I reference?"
3. **Confirm trigger behavior** - "Jenkins uses pollSCM every 15 min. Should I convert to push-based triggers instead?"
4. **Check for manual steps** - "There's an `input` step for approval. Do you want to use GitHub Environments with required reviewers?"
5. **Action mirrors** - "Do you need to use internal action mirrors? If so, what's your mirror URL pattern?"
6. **Runner configuration** - "Do you use GitHub-hosted runners or self-hosted? What labels should I use?"

## Example Session

```
User: Convert this Jenkinsfile to GitHub Actions
[pastes Jenkinsfile]

Agent:
1. Analyzes pipeline structure
2. Identifies: Maven build, JUnit tests, Docker deployment, Slack notifications
3. Notes credentials used: docker-hub, slack-token
4. Generates equivalent GHA workflow
5. Lists any manual steps needed (adding secrets)
6. Offers to optimize (add caching, matrix builds, etc.)
```
