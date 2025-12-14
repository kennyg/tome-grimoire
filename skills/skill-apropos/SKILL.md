---
name: skill-apropos
description: Find the right skill for a task. Use when user asks "what skill should I use", "is there a skill for X", "which skill handles Y", "find me a skill", or when unsure which skill to invoke. Searches installed skills by keyword.
---

# Skill Discovery

Search installed skills to find the right one for a task.

## Search Skills

```bash
python ~/.claude/skills/skill-apropos/scripts/search_skills.py <query>
```

Example:
```bash
python ~/.claude/skills/skill-apropos/scripts/search_skills.py "edit pdf"
```

Output:
```json
{
  "query": "edit pdf",
  "count": 2,
  "results": [
    {"name": "pdf", "description": "...", "score": 135, "invoke": "Skill: pdf"},
    {"name": "canvas-design", "description": "...", "score": 30, "invoke": "Skill: canvas-design"}
  ]
}
```

## List All Skills

```bash
python ~/.claude/skills/skill-apropos/scripts/search_skills.py --list
```

## Workflow

1. Run `search_skills.py` with user's task as query
2. Review results (sorted by relevance score)
3. If match found: invoke using `Skill: <name>`
4. If no match: help with built-in capabilities

## When to Use

- User asks "what skill should I use for X?"
- User asks "is there a skill that can..."
- User asks "find me a skill for..."
- Unsure which skill fits the task
