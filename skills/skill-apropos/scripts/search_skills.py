#!/usr/bin/env python3
"""
Search installed artifacts (skills, commands, etc.) by keyword.

Usage:
    python search_skills.py <query>          # Search all artifacts
    python search_skills.py --list           # List all artifacts
    python search_skills.py --type skill     # Filter by type
    python search_skills.py --rebuild        # Force rebuild index
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "are", "were", "been", "be",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "this", "that", "these", "those", "it",
    "its", "when", "claude", "needs", "use", "using", "used", "can", "any",
    "other", "you", "your", "they", "them", "their", "which", "what", "who",
}


def get_agent_dir() -> Path:
    return Path.home() / ".claude"


def get_project_agent_dir() -> Optional[Path]:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        project_dir = parent / ".claude"
        if project_dir.exists() and project_dir != get_agent_dir():
            return project_dir
        if (parent / ".git").exists():
            break
    return None


def get_index_path() -> Path:
    return get_agent_dir() / ".apropos.json"


def parse_skill_frontmatter(skill_md: Path) -> Optional[dict]:
    try:
        content = skill_md.read_text()
        if not content.startswith("---"):
            return None
        end = content.find("---", 3)
        if end == -1:
            return None
        yaml_content = content[3:end].strip()
        result = {}
        for line in yaml_content.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key in ("name", "description"):
                    result[key] = value
        return result if "name" in result else None
    except Exception:
        return None


def parse_command(cmd_path: Path) -> Optional[dict]:
    try:
        content = cmd_path.read_text()
        lines = content.split("\n")
        name = cmd_path.stem
        description = ""
        for i, line in enumerate(lines):
            if line.startswith("# "):
                for j in range(i + 1, min(i + 10, len(lines))):
                    para = lines[j].strip()
                    if para and not para.startswith("#") and not para.startswith("```"):
                        description = para
                        break
                break
        return {"name": name, "description": description}
    except Exception:
        return None


def extract_keywords(description: str) -> list[str]:
    normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", description.lower())
    words = normalized.split()
    seen = set()
    keywords = []
    for word in words:
        if len(word) < 3 or word in STOPWORDS or word in seen:
            continue
        seen.add(word)
        keywords.append(word)
    return keywords


def scan_skills(agent_dir: Path) -> list[dict]:
    skills = []
    skills_dir = agent_dir / "skills"
    if not skills_dir.exists():
        return skills
    for entry in skills_dir.iterdir():
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_skill_frontmatter(skill_md)
        if not fm:
            continue
        skills.append({
            "name": fm.get("name", entry.name),
            "type": "skill",
            "path": str(entry),
            "description": fm.get("description", ""),
            "keywords": extract_keywords(fm.get("description", "")),
            "mod_time": int(skill_md.stat().st_mtime),
        })
    return skills


def scan_commands(agent_dir: Path) -> list[dict]:
    commands = []
    commands_dir = agent_dir / "commands"
    if not commands_dir.exists():
        return commands
    for entry in commands_dir.iterdir():
        if not entry.is_file() or not entry.name.endswith(".md") or entry.name.startswith("."):
            continue
        parsed = parse_command(entry)
        if not parsed:
            continue
        commands.append({
            "name": parsed["name"],
            "type": "command",
            "path": str(entry),
            "description": parsed["description"],
            "keywords": extract_keywords(parsed["description"]),
            "mod_time": int(entry.stat().st_mtime),
        })
    return commands


def scan_all_artifacts(agent_dirs: list[Path]) -> list[dict]:
    artifacts = []
    seen = set()
    for agent_dir in agent_dirs:
        if not agent_dir.exists():
            continue
        for skill in scan_skills(agent_dir):
            key = (skill["name"], skill["type"])
            if key not in seen:
                seen.add(key)
                artifacts.append(skill)
        for cmd in scan_commands(agent_dir):
            key = (cmd["name"], cmd["type"])
            if key not in seen:
                seen.add(key)
                artifacts.append(cmd)
    return artifacts


def load_index() -> Optional[dict]:
    index_path = get_index_path()
    if not index_path.exists():
        return None
    try:
        return json.loads(index_path.read_text())
    except Exception:
        return None


def save_index(index: dict) -> None:
    index_path = get_index_path()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2))


def is_stale(index: dict, agent_dirs: list[Path]) -> bool:
    if not index or "artifacts" not in index:
        return True
    indexed = {a["path"]: a["mod_time"] for a in index["artifacts"]}
    for agent_dir in agent_dirs:
        if not agent_dir.exists():
            continue
        skills_dir = agent_dir / "skills"
        if skills_dir.exists():
            for entry in skills_dir.iterdir():
                if not entry.is_dir() or entry.name.startswith("."):
                    continue
                skill_md = entry / "SKILL.md"
                if not skill_md.exists():
                    continue
                path = str(entry)
                if path not in indexed or indexed[path] != int(skill_md.stat().st_mtime):
                    return True
                del indexed[path]
        commands_dir = agent_dir / "commands"
        if commands_dir.exists():
            for entry in commands_dir.iterdir():
                if not entry.is_file() or not entry.name.endswith(".md"):
                    continue
                path = str(entry)
                if path not in indexed or indexed[path] != int(entry.stat().st_mtime):
                    return True
                if path in indexed:
                    del indexed[path]
    return len(indexed) > 0


def build_index(agent_dirs: list[Path], force: bool = False) -> dict:
    if not force:
        index = load_index()
        if index and not is_stale(index, agent_dirs):
            return index
    artifacts = scan_all_artifacts(agent_dirs)
    index = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "artifacts": artifacts,
    }
    save_index(index)
    return index


def score_match(artifact: dict, query_words: list[str]) -> int:
    score = 0
    name_lower = artifact["name"].lower()
    desc_lower = artifact["description"].lower()
    for qw in query_words:
        if name_lower == qw:
            score += 100
        elif qw in name_lower:
            score += 50
        if qw in desc_lower:
            score += 10
        for kw in artifact.get("keywords", []):
            if kw == qw:
                score += 20
            elif qw in kw:
                score += 5
    return score


def search(index: dict, query: str, type_filter: Optional[str] = None) -> list[dict]:
    if not index or not index.get("artifacts"):
        return []
    query_words = query.lower().split()
    results = []
    for artifact in index["artifacts"]:
        if type_filter and artifact["type"] != type_filter:
            continue
        score = score_match(artifact, query_words)
        if score > 0:
            invoke = f"Skill: {artifact['name']}" if artifact["type"] == "skill" else f"/{artifact['name']}"
            results.append({
                "name": artifact["name"],
                "type": artifact["type"],
                "description": artifact["description"],
                "score": score,
                "invoke": invoke,
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Find artifacts (skills, commands) by keyword")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--list", action="store_true", help="List all artifacts")
    parser.add_argument("--type", choices=["skill", "command"], help="Filter by type")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild index")

    args = parser.parse_args()
    agent_dirs = [get_agent_dir()]
    project_dir = get_project_agent_dir()
    if project_dir:
        agent_dirs.append(project_dir)

    if args.rebuild:
        index = build_index(agent_dirs, force=True)
        print(json.dumps({"action": "rebuild", "count": len(index.get("artifacts", []))}, indent=2))
        return

    if args.list:
        index = build_index(agent_dirs)
        artifacts = [
            {"name": a["name"], "type": a["type"], "description": a["description"]}
            for a in index.get("artifacts", [])
            if not args.type or a["type"] == args.type
        ]
        print(json.dumps({"action": "list", "count": len(artifacts), "artifacts": artifacts}, indent=2))
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    query = " ".join(args.query)
    index = build_index(agent_dirs)
    results = search(index, query, args.type)
    print(json.dumps({"query": query, "count": len(results), "results": results}, indent=2))


if __name__ == "__main__":
    main()
