# hk Builtins Reference

Complete list of built-in linters available via `Builtins.<name>` in hk.pkl.

Run `hk builtins` to see all available builtins for your hk version.

## Python

| Builtin | Tool | Description |
|---------|------|-------------|
| `ruff` | ruff | Fast Python linter (replaces flake8, isort, etc.) |
| `ruff_format` | ruff format | Fast Python formatter (replaces black) |
| `mypy` | mypy | Static type checker |
| `pylint` | pylint | Comprehensive linter |
| `flake8` | flake8 | Style guide enforcement |
| `black` | black | Opinionated formatter |
| `isort` | isort | Import sorter |
| `python_check_ast` | python | Syntax validation |
| `python_debug_statements` | - | Detect debug statements |

**Recommended:** `ruff` + `ruff_format` (fast, replaces most others)

## JavaScript/TypeScript

| Builtin | Tool | Description |
|---------|------|-------------|
| `biome` | biome | Fast all-in-one linter+formatter |
| `eslint` | eslint | Pluggable linter |
| `prettier` | prettier | Opinionated formatter |
| `tsc` | tsc | TypeScript compiler check |
| `tsserver` | tsserver | TypeScript language server |
| `deno` | deno fmt | Deno formatter |
| `deno_check` | deno check | Deno type checker |
| `ox_lint` | oxlint | Fast linter (Rust-based) |
| `standard_js` | standard | JavaScript Standard Style |

**Note:** `oxfmt` (oxc formatter) is not a builtin yet - use custom step. See SKILL.md.

**Recommended:** `biome` (new projects) or `eslint` + `prettier` (existing)

## Go

| Builtin | Tool | Description |
|---------|------|-------------|
| `go_fmt` | gofmt | Standard formatter |
| `go_fumpt` | gofumpt | Stricter gofmt |
| `go_imports` | goimports | Format + manage imports |
| `golangci_lint` | golangci-lint | Meta-linter (many linters) |
| `go_vet` | go vet | Suspicious constructs |
| `go_sec` | gosec | Security scanner |
| `go_vuln_check` | govulncheck | Vulnerability checker |
| `staticcheck` | staticcheck | Advanced static analysis |
| `revive` | revive | Fast, configurable linter |
| `gomod_tidy` | go mod tidy | Clean go.mod/go.sum |
| `go_lines` | golines | Line length formatter |
| `err_check` | errcheck | Unchecked error returns |

**Recommended:** `go_fmt` + `go_imports` + `golangci_lint`

## Rust

| Builtin | Tool | Description |
|---------|------|-------------|
| `rustfmt` | rustfmt | Official formatter |
| `cargo_fmt` | cargo fmt | Cargo wrapper for rustfmt |
| `cargo_clippy` | cargo clippy | Lint collection |
| `cargo_check` | cargo check | Type/borrow checking |

**Recommended:** `rustfmt` + `cargo_clippy`

## Swift

| Builtin | Tool | Description |
|---------|------|-------------|
| `swiftlint` | swiftlint | Style and conventions |

Note: `swiftformat` requires custom step (no builtin yet)

## Shell

| Builtin | Tool | Description |
|---------|------|-------------|
| `shellcheck` | shellcheck | Static analysis for shell |
| `shfmt` | shfmt | Shell formatter |

## Ruby

| Builtin | Tool | Description |
|---------|------|-------------|
| `rubocop` | rubocop | Style guide enforcement |
| `standard_rb` | standardrb | Ruby Standard Style |
| `reek` | reek | Code smell detector |
| `sorbet` | sorbet | Type checker |
| `erb` | erb | ERB template linter |
| `fasterer` | fasterer | Performance suggestions |
| `brakeman` | brakeman | Security scanner |
| `bundle_audit` | bundle-audit | Gem vulnerability check |

## PHP

| Builtin | Tool | Description |
|---------|------|-------------|
| `php_cs` | php-cs-fixer | Coding standards fixer |

## Kotlin

| Builtin | Tool | Description |
|---------|------|-------------|
| `ktlint` | ktlint | Linter and formatter |

## Lua

| Builtin | Tool | Description |
|---------|------|-------------|
| `luacheck` | luacheck | Static analyzer |
| `stylua` | stylua | Formatter |

## Elixir

| Builtin | Tool | Description |
|---------|------|-------------|
| `mix_fmt` | mix format | Elixir formatter |
| `mix_compile` | mix compile | Compile check |
| `mix_test` | mix test | Run tests |

## Nix

| Builtin | Tool | Description |
|---------|------|-------------|
| `nix_fmt` | nixfmt | Nix formatter |
| `nixpkgs_format` | nixpkgs-fmt | Nixpkgs formatter |
| `alejandra` | alejandra | Opinionated Nix formatter |

## Configuration Files

| Builtin | Tool | Files | Description |
|---------|------|-------|-------------|
| `pkl` | pkl eval | *.pkl | Pkl config validation |
| `pkl_format` | pkl format | *.pkl | Pkl formatter |
| `prettier` | prettier | many | Multi-format (JSON, YAML, MD) |
| `yamllint` | yamllint | *.yaml | YAML linter |
| `yamlfmt` | yamlfmt | *.yaml | YAML formatter |
| `jq` | jq | *.json | JSON processor |
| `yq` | yq | *.yaml | YAML processor |
| `taplo` | taplo | *.toml | TOML linter |
| `taplo_format` | taplo fmt | *.toml | TOML formatter |
| `tombi` | tombi | *.toml | TOML formatter |
| `tombi_format` | tombi format | *.toml | TOML formatter |
| `xmllint` | xmllint | *.xml | XML validator |
| `sort_package_json` | sort-package-json | package.json | Sort keys |

## Infrastructure

| Builtin | Tool | Description |
|---------|------|-------------|
| `terraform` | terraform fmt | Terraform formatter |
| `tf_lint` | tflint | Terraform linter |
| `tofu` | tofu fmt | OpenTofu formatter |
| `hadolint` | hadolint | Dockerfile linter |
| `actionlint` | actionlint | GitHub Actions linter |
| `vacuum` | vacuum | OpenAPI linter |

## C/C++

| Builtin | Tool | Description |
|---------|------|-------------|
| `clang_format` | clang-format | C/C++ formatter |
| `cpp_lint` | cpplint | Google C++ style |

## Frontend

| Builtin | Tool | Description |
|---------|------|-------------|
| `stylelint` | stylelint | CSS/SCSS linter |
| `astro` | astro check | Astro component checker |

## SQL

| Builtin | Tool | Description |
|---------|------|-------------|
| `sql_fluff` | sqlfluff | SQL linter |

## Markdown

| Builtin | Tool | Description |
|---------|------|-------------|
| `markdown_lint` | markdownlint | Markdown linter |
| `lychee` | lychee | Link checker |

## Multi-Language Formatters

| Builtin | Tool | Description |
|---------|------|-------------|
| `dprint` | dprint | Fast pluggable formatter |
| `prettier` | prettier | Multi-format formatter |

## Universal / Git Hooks

| Builtin | Description |
|---------|-------------|
| `typos` | Spell checker (source code aware) |
| `trailing_whitespace` | Remove trailing whitespace |
| `newlines` | Ensure files end with newline |
| `mixed_line_ending` | Detect mixed line endings |
| `fix_byte_order_marker` | Remove BOM markers |
| `fix_smart_quotes` | Convert smart quotes to ASCII |
| `check_merge_conflict` | Detect merge conflict markers |
| `detect_private_key` | Detect committed private keys |
| `check_added_large_files` | Warn about large file additions |
| `check_byte_order_marker` | Detect BOM in files |
| `check_case_conflict` | Detect case-insensitive conflicts |
| `check_executables_have_shebangs` | Verify shebangs |
| `check_symlinks` | Validate symlinks |
| `check_conventional_commit` | Validate commit message format |
| `no_commit_to_branch` | Prevent commits to protected branches |

## Misc

| Builtin | Tool | Description |
|---------|------|-------------|
| `mise` | mise | Tool version manager tasks |
| `xo` | xo | JavaScript linter (ESLint preset) |
