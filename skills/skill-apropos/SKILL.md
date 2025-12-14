---
name: skill-apropos
description: Find the right artifact (skill, command, etc.) for a task. Use when user asks "what should I use for X", "is there a skill/command for Y", "find me something for Z", or when unsure which artifact to invoke. Searches all installed artifacts by keyword.
---

# Artifact Discovery

Search installed artifacts (skills, commands, etc.) to find the right one for a task.

## Search

```bash
python ~/.claude/skills/skill-apropos/scripts/search_skills.py <query>
```

Examples:
```bash
python ~/.claude/skills/skill-apropos/scripts/search_skills.py "edit pdf"
python ~/.claude/skills/skill-apropos/scripts/search_skills.py "community health"
python ~/.claude/skills/skill-apropos/scripts/search_skills.py --type skill spreadsheet
```

Output:
```json
{
  "query": "edit pdf",
  "count": 2,
  "results": [
    {"name": "pdf", "type": "skill", "score": 135, "invoke": "Skill: pdf"},
    {"name": "setup-community-health", "type": "command", "score": 30, "invoke": "/setup-community-health"}
  ]
}
```

## List All

```bash
python ~/.claude/skills/skill-apropos/scripts/search_skills.py --list
python ~/.claude/skills/skill-apropos/scripts/search_skills.py --list --type command
```

## Workflow

1. Run search with user's task as query
2. Review results (sorted by relevance)
3. Invoke using the `invoke` field:
   - Skills: `Skill: <name>`
   - Commands: `/<name>`
4. If no match: help with built-in capabilities
