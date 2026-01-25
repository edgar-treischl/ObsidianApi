#!/usr/bin/env python3
import os
import re
import sqlite3
import yaml
import uuid

VAULT_DIR = "./vault"
DB_FILE = "./store/vault.db"

WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")  # matches [[Note]]

# -----------------------------
# Helpers
# -----------------------------
def find_markdown_files(root):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)

def parse_frontmatter_and_content(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines or lines[0] != "---":
        return None, None
    try:
        end_idx = lines[1:].index("---") + 1
    except ValueError:
        return None, None
    yaml_str = "\n".join(lines[1:end_idx])
    content = "\n".join(lines[end_idx+1:])
    try:
        fm = yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        return None, None
    return fm or {}, content

def write_frontmatter(path, fm, body):
    yaml_str = yaml.safe_dump(fm, sort_keys=False)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\n{yaml_str}---\n{body}")

def extract_wikilinks(content):
    return WIKILINK_PATTERN.findall(content)

# -----------------------------
# Main build
# -----------------------------
def main():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # clean slate

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # --- Tables ---
    cur.execute("""
    CREATE TABLE notes (
        id TEXT PRIMARY KEY,
        path TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE links (
        from_note_id TEXT NOT NULL,
        to_note_id TEXT,
        to_path TEXT NOT NULL,
        FOREIGN KEY (from_note_id) REFERENCES notes(id)
    )""")

    cur.execute("""
    CREATE TABLE tags (
        note_id TEXT NOT NULL,
        tag TEXT NOT NULL,
        FOREIGN KEY (note_id) REFERENCES notes(id)
    )""")

    # --- FTS5 full-text search table ---
    cur.execute("""
    CREATE VIRTUAL TABLE notes_fts USING fts5(
        id UNINDEXED,
        title,
        content,
        content='notes',
        tokenize='porter'
    )
    """)

    # --- First pass: notes ---
    title_to_id = {}
    notes_data = []
    generated_uuids = []
    seen_ids = set()
    duplicate_ids = []

    for path in find_markdown_files(VAULT_DIR):
        fm, content = parse_frontmatter_and_content(path)
        if not fm or "title" not in fm:
            print(f"Skipping {path}: missing title")
            continue

        # Auto-generate UUID if missing or empty
        if "id" not in fm or not fm["id"]:
            fm["id"] = str(uuid.uuid4())
            write_frontmatter(path, fm, content)
            generated_uuids.append((path, fm["id"]))

        note_id = fm["id"]

        # Check for duplicate UUIDs
        if note_id in seen_ids:
            duplicate_ids.append((path, note_id))
        else:
            seen_ids.add(note_id)

        title = fm["title"]
        rel_path = os.path.relpath(path, VAULT_DIR)
        notes_data.append((note_id, rel_path, title, content))
        title_to_id[title] = note_id

    # Stop build if duplicates exist
    if duplicate_ids:
        print("\n❌ Duplicate UUIDs detected! Fix before building DB:")
        for path, nid in duplicate_ids:
            print(f" - {path}: {nid}")
        exit(1)

    cur.executemany(
        "INSERT INTO notes (id, path, title, content) VALUES (?, ?, ?, ?)",
        notes_data
    )

    # populate FTS5
    for note_id, _, title, content in notes_data:
        cur.execute(
            "INSERT INTO notes_fts (id, title, content) VALUES (?, ?, ?)",
            (note_id, title, content)
        )

    # --- Second pass: tags and links ---
    tags_data = []
    links_data = []

    for note_id, path, title, content in notes_data:
        fm, _ = parse_frontmatter_and_content(os.path.join(VAULT_DIR, path))

        # tags
        if fm and "tags" in fm and isinstance(fm["tags"], list):
            for tag in fm["tags"]:
                tags_data.append((note_id, tag))

        # wikilinks
        for target_title in extract_wikilinks(content):
            to_note_id = title_to_id.get(target_title)  # None if unresolved
            links_data.append((note_id, to_note_id, target_title))

    if tags_data:
        cur.executemany("INSERT INTO tags (note_id, tag) VALUES (?, ?)", tags_data)
    if links_data:
        cur.executemany(
            "INSERT INTO links (from_note_id, to_note_id, to_path) VALUES (?, ?, ?)",
            links_data
        )

    conn.commit()
    conn.close()

    print(f"✅ SQLite database built cleanly at {DB_FILE}")
    print(f"Notes: {len(notes_data)}, Tags: {len(tags_data)}, Links: {len(links_data)}")

    if generated_uuids:
        print("\n🆕 Generated UUIDs for new notes:")
        for path, nid in generated_uuids:
            print(f" - {path}: {nid}")

if __name__ == "__main__":
    main()
