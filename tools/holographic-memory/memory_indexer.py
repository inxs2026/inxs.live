"""
Holographic Memory — Core Indexer
Parses all memory files and builds a searchable index.
"""
import os
import re
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = "/home/damato/.openclaw/workspace"
MEMORY_FILES = [
    f"{MEMORY_ROOT}/MEMORY.md",
    f"{MEMORY_ROOT}/USER.md",
    f"{MEMORY_ROOT}/IDENTITY.md",
    f"{MEMORY_ROOT}/SOUL.md",
]
DAILY_DIR = f"{MEMORY_ROOT}/memory"

# Topics/keywords to track for graph connections
TOPIC_PATTERNS = {
    "racing": ["racing", "picks", "beyers", "handicapping", "drf", "gulfstream", "horse", "race"],
    "stocks": ["stock", "portfolio", "watchlist", "market", "trading"],
    "coding": ["code", "python", "script", "git", "github", "repo", "web", "app", "api"],
    "system": ["openclaw", "cron", "update", "install", "config", "server", "exec"],
    "weather": ["weather", "temperature", "forecast", "rain"],
    "calendar": ["calendar", "event", "meeting", "schedule"],
    "memory": ["memory", "lesson", "mistake", "remember", "forget"],
    "inxs": ["inxs", "vercel", "pdf2docx", "tool", "domain", "subdomain"],
    "mini_max": ["minimax", "model", "m2.7", "token"],
    "telegram": ["telegram", "message", "notification", "approve"],
    "email": ["email", "gmail", "smtp"],
    "photos": ["photo", "image", "camera", "video"],
    "home": ["home", "address", "stephanie", "location", "routing"],
    "racing_picks_process": ["methodology", "top-3-picks", "process", "verification", "scratch"],
    "racing_results": ["result", "winner", "exotic", "trifecta", "exacta"],
    "picks_corrections": ["wrong", "error", "correction", "fix", "post position", "pp"],
}

def get_all_memory_files():
    """Return all memory-related file paths."""
    files = list(MEMORY_FILES)
    daily_path = Path(DAILY_DIR)
    if daily_path.exists():
        files.extend(sorted(daily_path.glob("*.md")))
    return files

def extract_date_from_file(filepath):
    """Extract date from filename if it's a daily log."""
    name = os.path.basename(filepath)
    match = re.match(r"(\d{4}-\d{2}-\d{2})", name)
    if match:
        return match.group(1)
    return None

def parse_file_content(filepath):
    """Return (title, topics, entities, summary) for a file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return None, [], [], ""

    name = os.path.basename(filepath)
    date = extract_date_from_file(filepath)

    # Detect topics
    topics = []
    for topic, patterns in TOPIC_PATTERNS.items():
        for p in patterns:
            if p.lower() in content.lower():
                if topic not in topics:
                    topics.append(topic)
                break

    # Extract section headers as entities
    headers = re.findall(r"^#{1,4}\s+(.+)$", content, re.MULTILINE)
    entities = [h.strip() for h in headers if len(h) > 3 and len(h) < 80]

    # First paragraph summary
    paras = content.split("\n\n")
    summary = ""
    for p in paras:
        p = p.strip()
        if p and not p.startswith("#") and len(p) > 20:
            summary = p[:200] + "..." if len(p) > 200 else p
            break

    title = f"{date} — {name}" if date else name
    return title, topics, entities, summary

def build_index():
    """Build complete memory index."""
    files = get_all_memory_files()
    index = {
        "files": [],
        "topics": {t: [] for t in TOPIC_PATTERNS},
        "by_date": {},
        "entities": {},
    }

    for filepath in files:
        result = parse_file_content(filepath)
        title, topics, entities, summary = result
        if not title:
            continue

        date = extract_date_from_file(filepath)
        entry = {
            "path": filepath,
            "title": title,
            "topics": topics,
            "entities": entities,
            "summary": summary,
            "date": date,
            "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat() if os.path.exists(filepath) else None,
        }

        index["files"].append(entry)

        if date:
            if date not in index["by_date"]:
                index["by_date"][date] = []
            index["by_date"][date].append(entry)

        for topic in topics:
            if topic in index["topics"]:
                index["topics"][topic].append(entry)

        for entity in entities:
            if entity not in index["entities"]:
                index["entities"][entity] = []
            index["entities"][entity].append(entry)

    return index

def search(query, index, limit=20):
    """Full-text search across all memory files."""
    query_lower = query.lower()
    results = []

    for entry in index["files"]:
        score = 0
        matched_in = []

        if query_lower in entry["title"].lower():
            score += 10
            matched_in.append("title")
        if query_lower in entry["summary"].lower():
            score += 5
            matched_in.append("summary")
        for topic in entry["topics"]:
            if query_lower in topic:
                score += 3
                matched_in.append(f"topic:{topic}")
        for entity in entry["entities"]:
            if query_lower in entity.lower():
                score += 2
                matched_in.append(f"entity:{entity}")

        if score > 0:
            results.append({
                "entry": entry,
                "score": score,
                "matched_in": matched_in,
            })

    results.sort(key=lambda x: -x["score"])
    return results[:limit]

def get_knowledge_graph():
    """Build nodes and edges for knowledge graph visualization."""
    index = build_index()
    nodes = []
    edges = []
    seen_edges = set()

    # Topic nodes
    for topic in TOPIC_PATTERNS:
        entries = index["topics"].get(topic, [])
        if entries:
            nodes.append({
                "id": f"topic:{topic}",
                "label": topic.replace("_", " ").title(),
                "type": "topic",
                "count": len(entries),
            })

    # File nodes
    for entry in index["files"][:50]:  # limit for readability
        date_str = entry.get("date", "undated")
        nodes.append({
            "id": entry["path"],
            "label": entry["title"][:40],
            "type": "file",
            "date": date_str,
            "topic_count": len(entry["topics"]),
        })

        # Connect file to its topics
        for topic in entry["topics"]:
            edge_key = (entry["path"], f"topic:{topic}")
            if edge_key not in seen_edges:
                edges.append({
                    "source": entry["path"],
                    "target": f"topic:{topic}",
                    "type": "contains",
                })
                seen_edges.add(edge_key)

        # Connect related files by shared topics
        for other in index["files"]:
            if other["path"] == entry["path"]:
                continue
            shared = set(entry["topics"]) & set(other["topics"])
            if shared:
                edge_key = tuple(sorted([str(entry["path"]), str(other["path"])]))
                if edge_key not in seen_edges:
                    edges.append({
                        "source": entry["path"],
                        "target": other["path"],
                        "type": "related",
                        "topics": list(shared),
                    })
                    seen_edges.add(edge_key)

    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    idx = build_index()
    print(f"Indexed {len(idx['files'])} files across {len(idx['topics'])} topics")
    print(f"Top topics: {[(t, len(e)) for t, e in sorted(idx['topics'].items(), key=lambda x: -len(x[1]))[:5]]}")
