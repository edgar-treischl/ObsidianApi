# Team Knowledge Base — Current State & Next Steps

## Current State (POC)

- **Obsidian Vault as source**: Markdown files stored in `./vault`, Git-managed.  
- **Python-based build**: `build_sqlite.py` parses frontmatter, content, tags, and wikilinks.  
- **SQLite store**:  
  - Tables: `notes`, `tags`, `links`  
  - FTS5: full-text search via `notes_fts`  
- **UUIDs for notes**:  
  - Automatically generated if missing  
  - Duplicate UUIDs detected and build stops  
- **Read-only API**: `api.py` exposes endpoints for notes, links, tags, and full-text search.  
- **Prototype flow**: Vault → `build_sqlite.py` → SQLite → API → JSON queries.  
- **Dockerized**: API can run in container, tested via `curl`.  

## Key Principles

- Vault = source, SQLite = compiled artifact.  
- API is read-only, deterministic, versioned (`/v1`).  
- Links are shallow (1-hop), FTS-backed search available.  
- No runtime Obsidian parsing, no plugins required.  

## Next Steps

1. **Enhance validation**:  
2. **Refine schema**:  
   - Optional: headings, block IDs for granular linking.  
   - Optional: track creation/modification timestamps.  
3. **Improve API**:  
   - Pagination, limit & offset on all endpoints.  
   - Add search filters (tags, title, content).  
4. **Team workflow**:  
   - Standardize frontmatter template.  
   - CI/CD integration: auto-build SQLite on commit.  
5. **Documentation & onboarding**:  
   - Usage guide for adding notes, running builds, querying API.  

> Prompt for AI: “Markdown notes are compiled into a SQLite-based knowledge graph with read-only API; generate a roadmap for further schema, API features, validation, and team workflow improvements.”
