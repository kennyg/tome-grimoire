# Best Practices

## General

1. **Use caching** - Add `actions/cache` or setup action's built-in cache for dependencies
2. **Set timeouts** - Always add `timeout-minutes` to prevent runaway jobs
3. **Use concurrency** - Prevent duplicate runs with `concurrency` groups
4. **Artifact between jobs** - Use `actions/upload-artifact` and `actions/download-artifact`
5. **Secret management** - Store credentials in GitHub Secrets, use OIDC where possible
6. **Reusable workflows** - Extract common patterns to reusable workflows
7. **Least privilege** - Only request permissions jobs actually need

## Action Version Pinning

### Why Pin to SHA?

- **Security** - Tags can be moved to point to malicious code; SHAs are immutable
- **Reproducibility** - Builds are identical every time
- **Supply chain protection** - Mitigates risk of compromised action maintainer accounts

### Pinning Strategies

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| Floating tag | `@v4` | Auto-updates, less maintenance | May break unexpectedly |
| Exact tag | `@v4.1.1` | Predictable | Still mutable |
| SHA | `@b4ffde65f46336ab88eb53be808477a3936bae11` | Immutable, secure | Hard to read, manual updates |
| SHA + comment | See below | Best of both worlds | Slightly verbose |

### Recommended: SHA with Version Comment

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

### Finding SHAs

```bash
# Get SHA for a specific tag
git ls-remote --tags https://github.com/actions/checkout | grep v4.1.1

# Or visit: https://github.com/actions/checkout/releases
# Click on tag → commit SHA is in the URL
```

### Automated SHA Updates

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

### Enterprise Recommendation

For maximum security in enterprise environments:

1. Pin all actions to SHA
2. Use Dependabot/Renovate for updates
3. Mirror actions to internal registry
4. Review action updates before merging

```yaml
# Enterprise-grade action reference
- uses: ghes.company.com/actions-mirror/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

## Caching

### Node.js
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
```

### Python
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

### Custom Cache
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/my-tool
    key: ${{ runner.os }}-my-tool-${{ hashFiles('**/lockfile') }}
    restore-keys: |
      ${{ runner.os }}-my-tool-
```

## Concurrency

Prevent duplicate runs and resource conflicts:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel older runs when new commit pushed
```

For deployments (don't cancel):
```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false
```

## Permissions

Request only what's needed:

```yaml
permissions:
  contents: read      # Checkout code
  id-token: write     # OIDC auth
  packages: write     # Push to GHCR
  pull-requests: write # Comment on PRs
```

## Timeouts

Always set timeouts to prevent stuck jobs:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      # ...
```

## Artifacts

### Upload
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7
```

### Download (in another job)
```yaml
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/
```
