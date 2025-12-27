# Simple Pipeline Examples

## Basic Build & Test

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

## Multi-Stage with Dependencies

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

## Matrix Builds

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

## Docker Build & Push

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

## Post-Build Actions

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
