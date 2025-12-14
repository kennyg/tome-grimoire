#!/usr/bin/env python3
"""
Search installed skills by keyword to find the right one for a task.

Usage:
    python search_skills.py <query>     # Search skills
    python search_skills.py --list      # List all skills
    python search_skills.py --rebuild   # Force rebuild index
"""

import argparse
import json
import os
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


def get_skills_dirs() -> list[Path]:
    """Get all skill directories to scan."""
    dirs = []

    # User skills: ~/.claude/skills
    user_skills = Path.home() / ".claude" / "skills"
    if user_skills.exists():
        dirs.append(user_skills)

    # Project skills: .claude/skills (from cwd up to git root)
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        project_skills = parent / ".claude" / "skills"
        if project_skills.exists() and project_skills not in dirs:
            dirs.append(project_skills)
            break
        if (parent / ".git").exists():
            break

    return dirs


def get_index_path() -> Path:
    return Path.home() / ".claude" / "skills" / ".apropos.json"


def parse_frontmatter(skill_md: Path) -> Optional[dict]:
    """Parse YAML frontmatter from SKILL.md."""
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


def extract_keywords(description: str) -> list[str]:
    """Extract searchable keywords from description."""
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


def scan_skills(skills_dirs: list[Path]) -> list[dict]:
    """Scan directories and extract skill metadata."""
    skills = []
    seen_names = set()

    for skills_dir in skills_dirs:
        if not skills_dir.exists():
            continue

        for entry in skills_dir.iterdir():
            if not entry.is_dir() or entry.name.startswith("."):
                continue

            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue

            fm = parse_frontmatter(skill_md)
            if not fm:
                continue

            name = fm.get("name", entry.name)
            if name in seen_names:
                continue
            seen_names.add(name)

            description = fm.get("description", "")
            skills.append({
                "name": name,
                "path": str(entry),
                "description": description,
                "keywords": extract_keywords(description),
                "mod_time": int(skill_md.stat().st_mtime),
            })

    return skills


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


def is_stale(index: dict, skills_dirs: list[Path]) -> bool:
    if not index or "skills" not in index:
        return True

    indexed = {s["path"]: s["mod_time"] for s in index["skills"]}

    for skills_dir in skills_dirs:
        if not skills_dir.exists():
            continue
        for entry in skills_dir.iterdir():
            if not entry.is_dir() or entry.name.startswith("."):
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            path = str(entry)
            mod_time = int(skill_md.stat().st_mtime)
            if path not in indexed or indexed[path] != mod_time:
                return True
            del indexed[path]

    return len(indexed) > 0


def build_index(skills_dirs: list[Path], force: bool = False) -> dict:
    if not force:
        index = load_index()
        if index and not is_stale(index, skills_dirs):
            return index

    skills = scan_skills(skills_dirs)
    index = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "skills": skills,
    }
    save_index(index)
    return index


def score_match(skill: dict, query_words: list[str]) -> int:
    score = 0
    name_lower = skill["name"].lower()
    desc_lower = skill["description"].lower()

    for qw in query_words:
        if name_lower == qw:
            score += 100
        elif qw in name_lower:
            score += 50
        if qw in desc_lower:
            score += 10
        for kw in skill.get("keywords", []):
            if kw == qw:
                score += 20
            elif qw in kw:
                score += 5

    return score


def search(index: dict, query: str) -> list[dict]:
    if not index or not index.get("skills"):
        return []

    query_words = query.lower().split()
    results = []

    for skill in index["skills"]:
        score = score_match(skill, query_words)
        if score > 0:
            results.append({
                "name": skill["name"],
                "description": skill["description"],
                "score": score,
                "invoke": f"Skill: {skill['name']}",
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Find the right skill for a task")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--list", action="store_true", help="List all skills")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild index")

    args = parser.parse_args()
    skills_dirs = get_skills_dirs()

    if args.rebuild:
        index = build_index(skills_dirs, force=True)
        print(json.dumps({"action": "rebuild", "count": len(index.get("skills", []))}, indent=2))
        return

    if args.list:
        index = build_index(skills_dirs)
        skills = [{"name": s["name"], "description": s["description"]} for s in index.get("skills", [])]
        print(json.dumps({"action": "list", "count": len(skills), "skills": skills}, indent=2))
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    query = " ".join(args.query)
    index = build_index(skills_dirs)
    results = search(index, query)

    print(json.dumps({"query": query, "count": len(results), "results": results}, indent=2))


if __name__ == "__main__":
    main()
