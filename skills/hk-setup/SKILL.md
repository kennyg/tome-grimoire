---
name: hk-setup
description: Set up hk (git hook manager) with pre-commit hooks for any project. Detects project type (Python, JS/TS, Go, Rust, etc.) and configures appropriate linters/formatters. Use when user wants to add pre-commit hooks, set up hk, or configure linting for a project.
license: MIT
compatibility: Requires hk to be installed (brew install hk or mise use hk). Works with Claude Code and similar agents.
metadata:
  author: kenny
  version: "1.0"
---

# hk Setup

Configure [hk](https://hk.jdx.dev) git hooks with appropriate linters for any project.

## When to Use This Skill

- User asks to set up pre-commit hooks
- User wants to add linting/formatting to a project
- User mentions hk, git hooks, or pre-commit
- User wants to enforce code quality on commits

## Prerequisites

```bash
# Install hk (one of these)
brew install hk
mise use -g hk
```

## Workflow

### 1. Detect Project Type

Look for these files to identify the project:

| File | Project Type | Linters |
|------|--------------|---------|
| `pyproject.toml`, `setup.py`, `*.py` | Python | ruff, ruff-format, ty/mypy |
| `package.json`, `*.ts`, `*.tsx` | JavaScript/TypeScript | eslint, prettier |
| `go.mod`, `*.go` | Go | gofmt, golangci-lint |
| `Cargo.toml`, `*.rs` | Rust | rustfmt, clippy |
| `*.pkl` | Pkl configs | pkl eval |

### 2. Check Available Tools

```bash
# List built-in linters
hk builtins

# Common builtins:
# Python: ruff, ruff_format, mypy, black, isort
# JS/TS: eslint, prettier, biome
# Go: gofmt, goimports, golangci_lint
# Rust: rustfmt, clippy
# General: prettier, pkl
```

### 3. Generate hk.pkl

Create `hk.pkl` in project root. Always use version-pinned imports:

```pkl
amends "package://github.com/jdx/hk/releases/download/v1.28.0/hk@1.28.0#/Config.pkl"
import "package://github.com/jdx/hk/releases/download/v1.28.0/hk@1.28.0#/Builtins.pkl"

local linters = new Mapping<String, Step> {
    // Add linters here based on project type
}

hooks {
    ["pre-commit"] {
        fix = true
        stash = "git"
        steps = linters
    }
    ["pre-push"] {
        steps = linters
    }
    ["fix"] {
        fix = true
        steps = linters
    }
    ["check"] {
        steps = linters
    }
}
```

### 4. Install & Test

```bash
hk validate       # Check config syntax
hk install        # Install git hooks
hk check --all    # Run all checks
hk fix --all      # Auto-fix issues
```

## Project Templates

### Python (ruff + ty)

```pkl
local linters = new Mapping<String, Step> {
    ["ruff"] = Builtins.ruff
    ["ruff-format"] = Builtins.ruff_format
    ["ty"] {
        glob = "**/*.py"
        check = "ty check"
    }
    ["pkl"] {
        glob = "*.pkl"
        check = "pkl eval {{files}} >/dev/null"
    }
}
```

### JavaScript/TypeScript (eslint + prettier)

```pkl
local linters = new Mapping<String, Step> {
    ["eslint"] = Builtins.eslint
    ["prettier"] = Builtins.prettier
    ["pkl"] {
        glob = "*.pkl"
        check = "pkl eval {{files}} >/dev/null"
    }
}
```

### Go

```pkl
local linters = new Mapping<String, Step> {
    ["gofmt"] = Builtins.gofmt
    ["goimports"] = Builtins.goimports
    ["golangci-lint"] = Builtins.golangci_lint
    ["pkl"] {
        glob = "*.pkl"
        check = "pkl eval {{files}} >/dev/null"
    }
}
```

### Rust

```pkl
local linters = new Mapping<String, Step> {
    ["rustfmt"] = Builtins.rustfmt
    ["clippy"] = Builtins.clippy
    ["pkl"] {
        glob = "*.pkl"
        check = "pkl eval {{files}} >/dev/null"
    }
}
```

## Custom Steps

For tools without builtins, define custom steps:

```pkl
["my-linter"] {
    glob = "**/*.ext"           // Files to match
    check = "my-tool check {{files}}"  // Check command
    fix = "my-tool fix {{files}}"      // Optional fix command
}
```

### Step Options

| Option | Description |
|--------|-------------|
| `glob` | File patterns to match |
| `check` | Command to run for checking |
| `fix` | Command to run for fixing (optional) |
| `exclusive` | Run in isolation (no parallel) |
| `batch` | Process files in batches |
| `stomp` | Allow file modifications during check |

## Environment Variables

If tools are in a venv or non-standard location:

```pkl
env {
    ["PATH"] = ".venv/bin:\(read("env:PATH"))"
}
```

Or better: install tools globally via brew/mise.

## Troubleshooting

### Tool not found

```bash
# Check if tool is in PATH
which ruff

# Install globally
brew install ruff
# or
mise use -g ruff
```

### Config validation failed

```bash
hk validate
# Check Pkl syntax errors in output
```

### Hooks not running

```bash
# Reinstall hooks
hk install

# Check hook files exist
ls -la .git/hooks/pre-commit
```

## Examples

### User asks to add pre-commit hooks

1. Check project type (look for pyproject.toml, package.json, etc.)
2. Check what tools are available (`hk builtins`, `which ruff`)
3. Create appropriate hk.pkl
4. Run `hk validate && hk install`
5. Test with `hk check --all`
6. Fix issues with `hk fix --all`

### User has existing linter config

1. Read existing config (ruff.toml, .eslintrc, etc.)
2. Use matching hk builtins
3. Add any custom tools as custom steps
