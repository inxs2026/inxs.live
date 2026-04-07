#!/usr/bin/env python3
"""
Holographic Memory — Flask Web Dashboard
Flask web app with browse, search, and graph visualization.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from memory_indexer import build_index, search, get_knowledge_graph, TOPIC_PATTERNS, MEMORY_ROOT
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__)
app.template_folder = "templates"
app.static_folder = "static"

CACHE = {}
CACHE_TTL = 60  # seconds

def get_index():
    """Get index with simple caching."""
    import time
    key = "index"
    if key not in CACHE or (time.time() - CACHE.get("_index_time", 0)) > CACHE_TTL:
        CACHE[key] = build_index()
        CACHE["_index_time"] = time.time()
    return CACHE[key]

@app.route("/")
def index():
    idx = get_index()
    topic_counts = [(t, len(e)) for t, e in idx["topics"].items() if len(e) > 0]
    topic_counts.sort(key=lambda x: -x[1])
    return render_template("index.html",
        file_count=len(idx["files"]),
        topic_counts=topic_counts[:15],
        recent_files=sorted(idx["files"], key=lambda x: x.get("modified","") or "", reverse=True)[:10],
    )

@app.route("/browse")
def browse():
    idx = get_index()
    topic = request.args.get("topic", "")
    date = request.args.get("date", "")
    entries = idx["files"]

    if topic:
        entries = [e for e in entries if topic in e["topics"]]
    if date:
        entries = [e for e in entries if date in (e.get("date") or "")]

    entries.sort(key=lambda x: x.get("date") or "", reverse=True)
    return render_template("browse.html",
        entries=entries,
        topic=topic,
        date=date,
        topics=sorted(idx["topics"].keys()),
        topic_counts=[(t, len(e)) for t, e in idx["topics"].items()],
    )

@app.route("/file/<path:filepath>")
def view_file(filepath):
    # Security: only allow files under memory dirs
    safe_prefixes = [MEMORY_ROOT]
    if not any(filepath.startswith(p) for p in safe_prefixes):
        abort(403)

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        abort(404)

    name = os.path.basename(filepath)
    return render_template("file.html", name=name, content=content, filepath=filepath)

@app.route("/search")
def do_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    idx = get_index()
    results = search(q, idx)
    return jsonify([{
        "title": r["entry"]["title"],
        "path": r["entry"]["path"],
        "summary": r["entry"]["summary"],
        "topics": r["entry"]["topics"],
        "score": r["score"],
        "matched_in": r["matched_in"],
        "date": r["entry"].get("date"),
    } for r in results])

@app.route("/graph")
def graph():
    import time
    key = "graph"
    if key not in CACHE or (time.time() - CACHE.get("_graph_time", 0)) > 300:
        CACHE[key] = get_knowledge_graph()
        CACHE["_graph_time"] = time.time()
    g = CACHE[key]
    return render_template("graph.html", nodes=g["nodes"][:80], edges=g["edges"][:100])

@app.route("/api/graph")
def api_graph():
    import time
    key = "graph"
    if key not in CACHE or (time.time() - CACHE.get("_graph_time", 0)) > 300:
        CACHE[key] = get_knowledge_graph()
        CACHE["_graph_time"] = time.time()
    return jsonify(CACHE[key])

@app.route("/api/topics")
def api_topics():
    idx = get_index()
    return jsonify({t: len(e) for t, e in idx["topics"].items() if len(e) > 0})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5100))
    app.run(host="0.0.0.0", port=port, debug=False)
