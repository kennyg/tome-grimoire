# Complex Pipeline Example

A complete example showing parallel tests, Docker builds, multi-environment deployments, and notifications.

## Input Jenkinsfile

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

## Converted GitHub Actions Workflow

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

## Conversion Summary

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

## Setup Required

1. **GitHub Environments** - Create `dev`, `staging`, `production` with reviewers
2. **Secrets:**
   - `SONAR_TOKEN` - SonarQube authentication
   - `AWS_ECR_ROLE_ARN` - OIDC role for ECR push
   - `SLACK_BOT_TOKEN` - Slack notifications
3. **Environment Variables (per environment):**
   - `AWS_DEPLOY_ROLE_ARN` - OIDC role for kubectl
4. **AWS OIDC** - Configure trust policy for GitHub Actions in each account
