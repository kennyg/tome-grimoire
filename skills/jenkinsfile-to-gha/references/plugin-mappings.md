# Jenkins Plugin → GitHub Actions Mappings

## Common Plugins

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

## Build Tools

### Maven
```yaml
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
    cache: 'maven'
- run: mvn package
```

### Gradle
```yaml
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
- uses: gradle/gradle-build-action@v2
  with:
    arguments: build
```

### Node.js
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
- run: npm ci
- run: npm run build
```

### Python
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
- run: pip install -r requirements.txt
```

## Cloud Providers

### AWS (OIDC - Recommended)
```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
      aws-region: us-east-1
```

### AWS (Access Keys)
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

### Google Cloud (OIDC)
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.SA_EMAIL }}
```

### Azure
```yaml
- uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
```

## Container Registries

### Docker Hub
```yaml
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### AWS ECR
```yaml
- uses: aws-actions/amazon-ecr-login@v2
```

### Google Container Registry
```yaml
- uses: docker/login-action@v3
  with:
    registry: gcr.io
    username: _json_key
    password: ${{ secrets.GCR_JSON_KEY }}
```

## Testing & Quality

### JUnit Results
```yaml
- uses: dorny/test-reporter@v1
  if: always()
  with:
    name: Tests
    path: '**/target/surefire-reports/*.xml'
    reporter: java-junit
```

### Code Coverage
```yaml
- uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

### SonarQube
```yaml
- uses: sonarsource/sonarqube-scan-action@v2
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}
```

## Notifications

### Slack
```yaml
- uses: slackapi/slack-github-action@v1
  with:
    channel-id: '#builds'
    slack-message: 'Build ${{ job.status }}'
  env:
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

### Microsoft Teams
```yaml
- uses: jdcargile/ms-teams-notification@v1.4
  with:
    github-token: ${{ github.token }}
    ms-teams-webhook-uri: ${{ secrets.TEAMS_WEBHOOK }}
    notification-summary: 'Build completed'
```
