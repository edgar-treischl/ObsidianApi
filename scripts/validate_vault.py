#!/usr/bin/env python3
import os
import sys
import yaml
import uuid

VAULT_DIR = "./vault"  # adjust if your vault is elsewhere

def find_markdown_files(root):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)

def parse_frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    if lines[0] != "---":
        return None
    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        return None
    yaml_str = "\n".join(lines[1:end_idx])
    try:
        return yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        return None

def validate_uuid(id_str):
    try:
        uuid_obj = uuid.UUID(id_str)
        return True
    except:
        return False

def main():
    errors = []
    seen_ids = set()
    for path in find_markdown_files(VAULT_DIR):
        fm = parse_frontmatter(path)
        if fm is None:
            errors.append(f"{path}: missing or invalid frontmatter")
            continue
        note_id = fm.get("id")
        if not note_id:
            errors.append(f"{path}: missing id in frontmatter")
            continue
        if not validate_uuid(note_id):
            errors.append(f"{path}: invalid UUID '{note_id}'")
            continue
        if note_id in seen_ids:
            errors.append(f"{path}: duplicate id '{note_id}'")
            continue
        seen_ids.add(note_id)

    if errors:
        print("Vault validation failed:\n")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print(f"Vault validation succeeded: {len(seen_ids)} notes found.")

if __name__ == "__main__":
    main()
