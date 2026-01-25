#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
import sqlite3
import os
from typing import List
from rapidfuzz import process, fuzz

DB_FILE = "./store/vault.db"

app = FastAPI(
    title="Obsidian API", 
    version="0.0.0.1",
    description="Read-only API over compiled knowledge base")

# -----------------------------
# Database helper
# -----------------------------
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

# -----------------------------
# Search endpoint (FTS5 + optional fuzzy fallback)
# -----------------------------
@app.get("/v1/search")
def search_notes(
    q: str, 
    limit: int = 20, 
    offset: int = 0, 
    fuzzy: bool = True
):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # --- Prepare FTS query: prefix match on all words ---
    fts_words = [word + "*" for word in query.split()]
    fts_query = " ".join(fts_words)

    conn = get_conn()
    cur = conn.cursor()

    # --- FTS5 search ---
    cur.execute("""
        SELECT id, title FROM notes_fts
        WHERE notes_fts MATCH ?
        LIMIT ? OFFSET ?
    """, (fts_query, limit, offset))
    results = [dict(row) for row in cur.fetchall()]

    # --- Fuzzy fallback if no results and enabled ---
    if not results and fuzzy:
        cur.execute("SELECT id, title FROM notes")
        all_notes = cur.fetchall()
        titles = {row["title"]: row["id"] for row in all_notes}

        matches = process.extract(
            query,
            titles.keys(),
            scorer=fuzz.WRatio,
            limit=5
        )

        results = [
            {"id": titles[title], "title": title, "score": score} 
            for title, score, _ in matches if score > 60
        ]

    conn.close()
    return {
        "query": q,
        "results": results,
        "count": len(results),
        "limit": limit,
        "offset": offset
    }
