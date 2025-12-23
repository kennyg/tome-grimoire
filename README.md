# tome-grimoire

> A curated collection of skills, commands, and prompts for AI agents — your spellbook of capabilities.

## Contents

- [About](#about)
- [Installation](#installation)
- [Skills](#skills)
- [Commands](#commands)
- [Prompts](#prompts)
- [Hooks](#hooks)
- [Agents](#agents)
- [Contributing](#contributing)
- [License](#license)

## About

**tome-grimoire** is a grimoire (spellbook) of reusable artifacts for AI coding agents like [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenCode](https://github.com/opencode-ai/opencode), and similar tools.

Each artifact extends what your agent can do:

| Artifact | Purpose |
|----------|---------|
| **Skills** | Teach agents new capabilities with instructions and context |
| **Commands** | User-invokable workflows triggered with `/command` |
| **Prompts** | Reusable prompt templates for common tasks |
| **Hooks** | Shell commands that run on agent events |
| **Agents** | Specialized sub-agent configurations |

## Installation

Artifacts are installed using [**tome**](https://github.com/kennyg/tome) — a package manager for AI agent artifacts.

> **Note:** tome is currently in development.

```bash
# Install everything from this grimoire
tome learn kennyg/tome-grimoire

# Or install specific artifacts
tome learn kennyg/tome-grimoire --skill skill-apropos
tome learn kennyg/tome-grimoire --command setup-community-health
```

## Skills

| Name | Description |
|------|-------------|
| [skill-apropos](skills/skill-apropos/) | Find the right artifact (skill, command, etc.) for a task. Use when user asks... |
| [slidev](skills/slidev/) | Create and edit markdown-based presentations using Slidev framework. Use when... |

## Commands

| Name | Description |
|------|-------------|
| [setup-community-health](commands/setup-community-health.md) | Setup Community Health Files |

## Prompts

*Coming soon*

## Hooks

*Coming soon*

## Agents

*Coming soon*

## Repository Structure

```
tome-grimoire/
├── skills/           # Skill definitions (SKILL.md + supporting files)
├── commands/         # Command definitions (markdown files)
├── prompts/          # Prompt templates
├── hooks/            # Hook configurations
├── agents/           # Agent configurations
├── scripts/          # Build and maintenance scripts
└── tome.yaml         # Grimoire metadata
```

## Contributing

Contributions welcome! Feel free to:

- **Add new artifacts** — Submit a PR with your skill, command, or prompt
- **Improve existing ones** — Better docs, bug fixes, enhancements
- **Report issues** — Found a problem? Open an issue

## License

MIT
