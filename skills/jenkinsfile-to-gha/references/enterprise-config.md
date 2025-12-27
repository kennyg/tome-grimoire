# Enterprise Configuration

Many enterprises use internal mirrors of GitHub Actions for security, compliance, or air-gapped environments.

## Interactive Configuration

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

## Rule-Based Action Mapping

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

## Applying Mirror Rules

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

## Common Enterprise Patterns

| Source | Mirror Pattern | Notes |
|--------|----------------|-------|
| GitHub.com → GHES | `ghes.corp.com/org/repo` | GitHub Enterprise Server |
| GitHub.com → Artifactory | `artifactory.corp.com/github-actions-remote/org/repo` | JFrog Artifactory |
| GitHub.com → Nexus | `nexus.corp.com/repository/github-actions/org/repo` | Sonatype Nexus |
| GitHub.com → GitLab | `gitlab.corp.com/mirrors/github/org/repo` | GitLab mirroring |

## Self-Hosted Runners

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

## Air-Gapped Environments

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

## Version Pinning Strategy

Ask about version strategy:

1. **Tag-based** (default): `@v4` - Allows minor updates
2. **SHA-pinned**: `@b4ffde65f46336ab88eb53be808477a3936bae11` - Maximum reproducibility
3. **Floating**: `@main` - Always latest (not recommended for prod)

**For enterprise migrations, recommend SHA pinning:**
```yaml
# Instead of:
- uses: ghes.company.com/github-actions/checkout@v4

# Use:
- uses: ghes.company.com/github-actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
  # v4.1.1 - pinned for reproducibility
```
