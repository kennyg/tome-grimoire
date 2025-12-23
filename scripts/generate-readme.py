#!/usr/bin/env python3
"""Generate README.md tables from skills and commands."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
README = ROOT / "README.md"
SKILLS_DIR = ROOT / "skills"
COMMANDS_DIR = ROOT / "commands"


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Handle multi-line descriptions (take first line only for table)
            if not value and key == "description":
                continue
            frontmatter[key] = value
    return frontmatter


def get_skills() -> list[dict]:
    """Get all skills from skills directory."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text()
        meta = parse_frontmatter(content)

        name = meta.get("name", skill_dir.name)
        description = meta.get("description", "")
        # Truncate long descriptions for table (break at word boundary)
        if len(description) > 80:
            description = description[:80].rsplit(" ", 1)[0] + "..."

        skills.append({
            "name": name,
            "description": description,
            "path": f"skills/{skill_dir.name}/",
        })

    return skills


def get_commands() -> list[dict]:
    """Get all commands from commands directory."""
    commands = []
    if not COMMANDS_DIR.exists():
        return commands

    for cmd_file in sorted(COMMANDS_DIR.glob("*.md")):
        content = cmd_file.read_text()

        # Try frontmatter first
        meta = parse_frontmatter(content)
        if meta:
            name = meta.get("name", cmd_file.stem)
            description = meta.get("description", "")
        else:
            # Fall back to parsing heading
            name = cmd_file.stem
            heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            description = heading_match.group(1) if heading_match else ""

        if len(description) > 80:
            description = description[:80].rsplit(" ", 1)[0] + "..."

        commands.append({
            "name": name,
            "description": description,
            "path": f"commands/{cmd_file.name}",
        })

    return commands


def generate_table(items: list[dict], type_name: str) -> str:
    """Generate a markdown table from items."""
    if not items:
        return "*Coming soon*"

    lines = [
        "| Name | Description |",
        "|------|-------------|",
    ]
    for item in items:
        name_link = f"[{item['name']}]({item['path']})"
        lines.append(f"| {name_link} | {item['description']} |")

    return "\n".join(lines)


def update_readme(skills: list[dict], commands: list[dict]) -> bool:
    """Update README.md with generated tables. Returns True if changed."""
    content = README.read_text()
    original = content

    # Update skills section
    skills_table = generate_table(skills, "Skills")
    content = re.sub(
        r"(### Skills\n\n).*?(?=\n\n### |\n\n## |\Z)",
        rf"\1{skills_table}",
        content,
        flags=re.DOTALL,
    )

    # Update commands section
    commands_table = generate_table(commands, "Commands")
    content = re.sub(
        r"(### Commands\n\n).*?(?=\n\n### |\n\n## |\Z)",
        rf"\1{commands_table}",
        content,
        flags=re.DOTALL,
    )

    if content != original:
        README.write_text(content)
        return True
    return False


def main():
    skills = get_skills()
    commands = get_commands()

    changed = update_readme(skills, commands)

    print(f"Skills: {len(skills)}")
    for s in skills:
        print(f"  - {s['name']}")

    print(f"Commands: {len(commands)}")
    for c in commands:
        print(f"  - {c['name']}")

    if changed:
        print("\nREADME.md updated!")
    else:
        print("\nREADME.md already up to date.")


if __name__ == "__main__":
    main()
