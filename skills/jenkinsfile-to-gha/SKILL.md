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

### General

1. **Use caching** - Add `actions/cache` or setup action's built-in cache for dependencies
2. **Set timeouts** - Always add `timeout-minutes` to prevent runaway jobs
3. **Use concurrency** - Prevent duplicate runs with `concurrency` groups
4. **Artifact between jobs** - Use `actions/upload-artifact` and `actions/download-artifact`
5. **Secret management** - Store credentials in GitHub Secrets, use OIDC where possible
6. **Reusable workflows** - Extract common patterns to reusable workflows
7. **Least privilege** - Only request permissions jobs actually need

### Action Version Pinning

**Why pin to SHA?**
- **Security** - Tags can be moved to point to malicious code; SHAs are immutable
- **Reproducibility** - Builds are identical every time
- **Supply chain protection** - Mitigates risk of compromised action maintainer accounts

**Pinning strategies:**

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| Floating tag | `@v4` | Auto-updates, less maintenance | May break unexpectedly |
| Exact tag | `@v4.1.1` | Predictable | Still mutable |
| SHA | `@b4ffde65f46336ab88eb53be808477a3936bae11` | Immutable, secure | Hard to read, manual updates |
| SHA + comment | See below | Best of both worlds | Slightly verbose |

**Recommended: SHA with version comment**

```yaml
steps:
  - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
  - uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8 # v4.0.2
    with:
      node-version: '20'
  - uses: docker/build-push-action@4a13e500e55cf31b7a5d59a38ab2040ab0f42f56 # v5.1.0
    with:
      push: true
      tags: myapp:latest
```

**Finding SHAs:**

```bash
# Get SHA for a specific tag
git ls-remote --tags https://github.com/actions/checkout | grep v4.1.1

# Or visit: https://github.com/actions/checkout/releases
# Click on tag → commit SHA is in the URL
```

**Automated SHA updates:**

Use tools to keep SHAs updated while maintaining security:

- **Dependabot** - Native GitHub, updates action SHAs automatically
- **Renovate** - More configurable, supports grouping updates
- **pinact** - CLI tool specifically for pinning actions

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "ci"
```

**Enterprise recommendation:**

For maximum security in enterprise environments:
1. Pin all actions to SHA
2. Use Dependabot/Renovate for updates
3. Mirror actions to internal registry
4. Review action updates before merging

```yaml
# Enterprise-grade action reference
- uses: ghes.company.com/actions-mirror/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

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

## Complete Example: Complex Pipeline Conversion

### Input Jenkinsfile

```groovy
@Library(['ci-shared-lib@v2.1']) _

pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME = 'order-service'
        DOCKER_REGISTRY = 'ecr.aws/mycompany'
        SONAR_HOST = 'https://sonar.internal.company.com'
    }

    triggers {
        cron('H 2 * * 1-5')
        pollSCM('H/5 * * * *')
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Deploy target')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip test execution')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                }
            }
        }

        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        stage('Test') {
            when {
                expression { return !params.SKIP_TESTS }
            }
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:unit -- --coverage'
                    }
                    post {
                        always {
                            junit 'reports/junit/*.xml'
                            publishHTML([reportName: 'Coverage', reportDir: 'coverage/lcov-report', reportFiles: 'index.html'])
                        }
                    }
                }
                stage('Integration Tests') {
                    agent {
                        docker {
                            image 'node:20'
                            args '-v /var/run/docker.sock:/var/run/docker.sock'
                        }
                    }
                    steps {
                        sh 'npm run test:integration'
                    }
                }
                stage('Lint & Security') {
                    steps {
                        sh 'npm run lint'
                        sh 'npm audit --audit-level=high'
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh 'sonar-scanner -Dsonar.projectKey=${APP_NAME} -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONAR_TOKEN}'
                }
            }
        }

        stage('Docker Build & Push') {
            when { branch 'main' }
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-ecr-creds']]) {
                    sh '''
                        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${DOCKER_REGISTRY}
                        docker build -t ${DOCKER_REGISTRY}/${APP_NAME}:${GIT_SHORT_COMMIT} .
                        docker push ${DOCKER_REGISTRY}/${APP_NAME}:${GIT_SHORT_COMMIT}
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                allOf {
                    branch 'main'
                    expression { return params.ENVIRONMENT != '' }
                }
            }
            stages {
                stage('Deploy to Dev') {
                    steps { deployToEnvironment('dev') }
                }
                stage('Deploy to Staging') {
                    when { expression { return params.ENVIRONMENT in ['staging', 'prod'] } }
                    steps {
                        input message: 'Deploy to Staging?', ok: 'Deploy'
                        deployToEnvironment('staging')
                    }
                }
                stage('Deploy to Prod') {
                    when { expression { return params.ENVIRONMENT == 'prod' } }
                    steps {
                        input message: 'Deploy to Production?', submitter: 'release-managers', ok: 'Deploy'
                        deployToEnvironment('prod')
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
            archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
        }
        success {
            slackSend channel: '#deployments', color: 'good', message: "Build succeeded: ${env.BUILD_URL}"
        }
        failure {
            slackSend channel: '#deployments', color: 'danger', message: "Build failed: ${env.BUILD_URL}"
        }
    }
}

def deployToEnvironment(String env) {
    withCredentials([file(credentialsId: "kubeconfig-${env}", variable: 'KUBECONFIG')]) {
        sh "kubectl set image deployment/${APP_NAME} ${APP_NAME}=${DOCKER_REGISTRY}/${APP_NAME}:${GIT_SHORT_COMMIT} -n ${env}"
        sh "kubectl rollout status deployment/${APP_NAME} -n ${env} --timeout=5m"
    }
}
```

### Converted GitHub Actions Workflow

```yaml
name: Order Service CI/CD

on:
  push:
    branches: [main, develop, 'feature/**']
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1-5'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deploy target'
        required: false
        type: choice
        options: [dev, staging, prod]
      skip_tests:
        description: 'Skip test execution'
        required: false
        type: boolean
        default: false

env:
  APP_NAME: order-service
  DOCKER_REGISTRY: ecr.aws/mycompany
  SONAR_HOST: https://sonar.internal.company.com
  AWS_REGION: us-east-1

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    outputs:
      git_short_commit: ${{ steps.vars.outputs.sha_short }}
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

      - name: Set variables
        id: vars
        run: echo "sha_short=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

      - uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8 # v4.0.2
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      - uses: actions/upload-artifact@5d5d22a31266ced268874388b861e4b58bb5c2f3 # v4.3.1
        with:
          name: dist
          path: dist/
          retention-days: 7

  test-unit:
    needs: build
    if: ${{ !inputs.skip_tests }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8 # v4.0.2
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:unit -- --coverage

      - name: Upload test results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Unit Tests
          path: reports/junit/*.xml
          reporter: java-junit

      - name: Upload coverage
        uses: actions/upload-artifact@5d5d22a31266ced268874388b861e4b58bb5c2f3 # v4.3.1
        if: always()
        with:
          name: coverage-report
          path: coverage/lcov-report/

  test-integration:
    needs: build
    if: ${{ !inputs.skip_tests }}
    runs-on: ubuntu-latest
    container:
      image: node:20
    services:
      docker:
        image: docker:dind
        options: --privileged
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - run: npm ci
      - run: npm run test:integration

  lint-security:
    needs: build
    if: ${{ !inputs.skip_tests }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
      - uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8 # v4.0.2
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm audit --audit-level=high

  sonarqube:
    needs: [test-unit, test-integration, lint-security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
        with:
          fetch-depth: 0

      - uses: sonarsource/sonarqube-scan-action@v2
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ env.SONAR_HOST }}
        with:
          args: >
            -Dsonar.projectKey=${{ env.APP_NAME }}

  docker-build-push:
    needs: [build, sonarqube]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ECR_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: aws-actions/amazon-ecr-login@v2

      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@4a13e500e55cf31b7a5d59a38ab2040ab0f42f56 # v5.1.0
        with:
          context: .
          push: true
          tags: |
            ${{ env.DOCKER_REGISTRY }}/${{ env.APP_NAME }}:${{ needs.build.outputs.git_short_commit }}
            ${{ env.DOCKER_REGISTRY }}/${{ env.APP_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-dev:
    needs: docker-build-push
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: azure/setup-kubectl@v3

      - name: Deploy to dev
        run: |
          aws eks update-kubeconfig --name dev-cluster --region ${{ env.AWS_REGION }}
          kubectl set image deployment/${{ env.APP_NAME }} \
            ${{ env.APP_NAME }}=${{ env.DOCKER_REGISTRY }}/${{ env.APP_NAME }}:${{ needs.build.outputs.git_short_commit }} \
            -n dev
          kubectl rollout status deployment/${{ env.APP_NAME }} -n dev --timeout=5m

  deploy-staging:
    needs: deploy-dev
    if: inputs.environment == 'staging' || inputs.environment == 'prod'
    runs-on: ubuntu-latest
    environment: staging  # Requires approval in GitHub Environment settings
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: azure/setup-kubectl@v3

      - name: Deploy to staging
        run: |
          aws eks update-kubeconfig --name staging-cluster --region ${{ env.AWS_REGION }}
          kubectl set image deployment/${{ env.APP_NAME }} \
            ${{ env.APP_NAME }}=${{ env.DOCKER_REGISTRY }}/${{ env.APP_NAME }}:${{ needs.build.outputs.git_short_commit }} \
            -n staging
          kubectl rollout status deployment/${{ env.APP_NAME }} -n staging --timeout=5m

  deploy-prod:
    needs: deploy-staging
    if: inputs.environment == 'prod'
    runs-on: ubuntu-latest
    environment: production  # Requires approval from release-managers team
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: azure/setup-kubectl@v3

      - name: Deploy to production
        run: |
          aws eks update-kubeconfig --name prod-cluster --region ${{ env.AWS_REGION }}
          kubectl set image deployment/${{ env.APP_NAME }} \
            ${{ env.APP_NAME }}=${{ env.DOCKER_REGISTRY }}/${{ env.APP_NAME }}:${{ needs.build.outputs.git_short_commit }} \
            -n prod
          kubectl rollout status deployment/${{ env.APP_NAME }} -n prod --timeout=5m

  notify:
    needs: [build, test-unit, test-integration, lint-security, docker-build-push]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Notify success
        if: ${{ !contains(needs.*.result, 'failure') }}
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: '#deployments'
          slack-message: "✅ ${{ env.APP_NAME }} build succeeded: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}

      - name: Notify failure
        if: ${{ contains(needs.*.result, 'failure') }}
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: '#deployments'
          slack-message: "❌ ${{ env.APP_NAME }} build failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### Conversion Summary

| Jenkins | GitHub Actions |
|---------|----------------|
| `@Library(['ci-shared-lib@v2.1'])` | Inlined (or use reusable workflow) |
| `agent any` | `runs-on: ubuntu-latest` |
| `options { timeout(...) }` | `timeout-minutes: 60` |
| `disableConcurrentBuilds()` | `concurrency:` group |
| `parameters { choice(...) }` | `workflow_dispatch.inputs` |
| `triggers { cron(...) }` | `on: schedule:` |
| `pollSCM` | `on: push/pull_request` (event-based) |
| `parallel { }` | Separate jobs (run concurrently) |
| `when { branch 'main' }` | `if: github.ref == 'refs/heads/main'` |
| `input` (manual approval) | `environment:` with required reviewers |
| `withCredentials([AWS...])` | OIDC via `aws-actions/configure-aws-credentials` |
| `post { always/success/failure }` | Separate `notify` job with `if: always()` |
| `archiveArtifacts` | `actions/upload-artifact` |
| `junit` | `dorny/test-reporter` |
| `slackSend` | `slackapi/slack-github-action` |

### Setup Required

1. **GitHub Environments** - Create `dev`, `staging`, `production` with reviewers
2. **Secrets:**
   - `SONAR_TOKEN` - SonarQube authentication
   - `AWS_ECR_ROLE_ARN` - OIDC role for ECR push
   - `SLACK_BOT_TOKEN` - Slack notifications
3. **Environment Variables (per environment):**
   - `AWS_DEPLOY_ROLE_ARN` - OIDC role for kubectl
4. **AWS OIDC** - Configure trust policy for GitHub Actions in each account
