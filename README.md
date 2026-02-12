# Team Knowledge Base

# Obsidian + Own API + SQLite — Brainstorming Summary

## Core Idea
Use **Obsidian purely as a Markdown editor** and treat the vault as **source code**.  
On each change (via CI/CD), **compile the vault into a derived store** (SQLite), which a **read-only API** queries.  
No Obsidian plugins, no runtime parsing, no filesystem watching.

---

## Architecture

```
Obsidian Vault (Markdown, Git repo)
↓ commit
↓ CI/CD build step
SQLite Store (indexed artifact)
↓
Read-only API
```


- Obsidian edits files only
- CI parses markdown once
- API never touches markdown, only the store
- Latest build only (no history/time-travel)

---

## “Knowledge Graph” (demystified)
- **Nodes** = notes
- **Edges** = wikilinks (`[[Note]]`)
- Implemented as simple tables (e.g. `notes`, `links`)
- Enables backlinks, outgoing links, neighborhoods
- No semantics, no AI, no Neo4j — just relationships

---

## Store
- **SQLite + FTS5** is the right choice
- Read-heavy, single-writer (CI), static snapshot
- Tables typically include:
  - notes (id, path, title, content)
  - links (from_note_id, to_note_id)
  - tags
  - headings / blocks (optional)
- Store is a **build artifact**, not source
- API must be **read-only**

---

## Repository Setup (v1)
Single repo recommended:

```
/vault → Obsidian markdown
/indexer → build script
/store → generated SQLite (gitignored locally)
/api → API code
```


Deployment:
- CI rebuilds SQLite
- SQLite baked into Docker image with API

---

## API Design Principles
- Read-only, deterministic
- Versioned (`/v1`)
- Stable note IDs (prefer UUID in frontmatter)
- Clean API shape ≠ internal DB schema
- Explicit handling of broken/unresolved links
- Pagination + limits on all list endpoints
- Shallow graph queries only (1-hop links)
- Clear search semantics (FTS-backed)

---

## What This Is (and Isn’t)
**Is**
- A compiled, queryable representation of notes
- Like a static site generator, but serving JSON

**Is Not**
- Obsidian as a service
- A real-time system
- A semantic/AI knowledge graph
- A writable note backend

---

## Key Framing Sentence
> “Markdown is the source, CI compiles it into indices, and the API queries those indices.”

Use this summary as a prompt to continue brainstorming, refining schema, API endpoints, or CI details.


# Further ado

```bash
python3 -m venv .venv 
source .venv/bin/activate        

#Win
python -m venv .venv 
.\.venv\Scripts\Activate.ps1


python validate_vault.py
python scripts/build_sqlite.py

#sqlite3 is a CLI Tool shipped with unix/maybe installed with homebrew
sqlite3 store/vault.db "SELECT id, title FROM notes;"
sqlite3 store/vault.db "SELECT * FROM tags;" 
sqlite3 .store/vault.db "SELECT * FROM links;"

````


```py
# scripts/query_db.py
import sqlite3
import sys

table = sys.argv[1] if len(sys.argv) > 1 else "links"

conn = sqlite3.connect("store/vault.db")
cur = conn.cursor()

cur.execute(f"SELECT * FROM {table};")
rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()
```



## API

´´´bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```


## Endpoints

````
# List notes
curl http://localhost:8000/v1/notes

# Fetch a single note
curl http://localhost:8000/v1/notes/<note-id>

# Outgoing links
curl http://localhost:8000/v1/notes/<note-id>/links

# Backlinks
curl http://localhost:8000/v1/notes/<note-id>/backlinks

# Tags
curl http://localhost:8000/v1/notes/<note-id>/tags

# Search
curl "http://localhost:8000/v1/search?q=knowledge"

curl http://localhost:8000/v1/notes/e2bccb38-c788-460e-bb64-d76cb2cb7e7f

curl http://localhost:8000/v1/notes/e9429f09-d3ed-4db5-a8bf-73ab9e5b5418/links



````




````
# Step 1: build DB, build Docker, run API
make start

# Now you can test API manually:
curl http://localhost:8000/v1/notes
curl "http://localhost:8000/v1/search?q=knowledge"

# Step 3: stop + remove DB
make clean
````


