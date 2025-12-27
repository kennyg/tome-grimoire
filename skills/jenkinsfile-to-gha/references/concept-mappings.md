# Jenkins → GitHub Actions Concept Mappings

## Core Concepts

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

## Environment Variables

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

## Triggers

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

## Credentials

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
