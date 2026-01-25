---
title: Team Knowledge Base
id: e2bccb38-c788-460e-bb64-d76cb2cb7e7f
tags:
  - test
  - other
  - python
created: 2026-01-14
modified: 2026-01-14
owner: tre
---


This repository is intended to serve as a **single source of truth for team knowledge**, combining Obsidian for note-taking and Docusaurus for documentation deployment. The goal is to create a workflow where engineers can write Markdown notes, and the team can query and browse the knowledge base efficiently. [[welcome]]



## Current Setup

- **Obsidian Vault**: `vault/` folder contains Markdown notes.  
- **Obsidian Local REST API**: Installed and configured with:
  - HTTP port: `27123` (insecure)
  - HTTPS port: `27124` (self-signed certificate)
  - API Key set
  - Insecure server enabled to allow local curl testing

### Tested Features

- Listing all files in the vault via the API:

```bash
curl -X GET http://127.0.0.1:27123/vault/ \
  -H "Authorization: Bearer <API_KEY>"
```

Searching notes via simple search endpoint:

```
curl -X POST http://127.0.0.1:27123/search/simple \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  --data-raw '{"query":"Test"}'
```

### Issues Encountered

- **POST `/search` endpoint failure**  
  Attempts to use the full `/search` endpoint returned `400 Bad Request` or connection reset errors. For now, only `/search/simple` is functional.

- **HTTPS connection issues**  
  Using the secure port (`27124`) requires bypassing the self-signed certificate with `-k` in curl.

- **Content-Type sensitivity**  
  The API rejects some `Content-Type` headers, e.g., `application/json;charset=UTF-8` caused connection resets in some tests.

- **Headless configuration nuances**  
  Running Obsidian headless in Docker requires careful port and API key setup. Insecure server must be enabled for local testing.

- **Complex search not stable**  
  Advanced search queries (`contextLength` + query payload) consistently fail, limiting initial search functionality to simple queries.

