#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
import sqlite3
import os

DB_FILE = "./store/vault.db"

app = FastAPI(title="ObsidianHeadless API", version="v1")

def get_conn():
    if not os.path.exists(DB_FILE):
        raise RuntimeError(f"Database not found at {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
# Notes endpoints
# -----------------------------

@app.get("/v1/notes")
def list_notes(limit: int = 50, offset: int = 0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, path FROM notes ORDER BY title LIMIT ? OFFSET ?",
        (limit, offset)
    )
    notes = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"notes": notes, "limit": limit, "offset": offset, "count": len(notes)}

@app.get("/v1/notes/{note_id}")
def get_note(note_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return dict(row)

@app.get("/v1/notes/{note_id}/links")
def get_links(note_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT to_note_id, to_path FROM links WHERE from_note_id = ?", (note_id,))
    links = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"from_note_id": note_id, "links": links}

@app.get("/v1/notes/{note_id}/tags")
def get_tags(note_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT tag FROM tags WHERE note_id = ?", (note_id,))
    tags = [row["tag"] for row in cur.fetchall()]
    conn.close()
    return {"note_id": note_id, "tags": tags}

# -----------------------------
# Search endpoint (FTS5)
# -----------------------------

@app.get("/v1/search")
def search_notes(q: str, limit: int = 20, offset: int = 0):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title FROM notes_fts
        WHERE notes_fts MATCH ?
        LIMIT ? OFFSET ?
    """, (q, limit, offset))
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"query": q, "results": results, "count": len(results), "limit": limit, "offset": offset}

# -----------------------------
# Backlinks endpoint
# -----------------------------

@app.get("/v1/notes/{note_id}/backlinks")
def get_backlinks(note_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT from_note_id, n.title AS from_title 
        FROM links l
        JOIN notes n ON l.from_note_id = n.id
        WHERE l.to_note_id = ?
    """, (note_id,))
    backlinks = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"note_id": note_id, "backlinks": backlinks}
