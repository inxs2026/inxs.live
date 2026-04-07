#!/usr/bin/env python3
"""
Holographic Memory — Knowledge Graph Generator
Generates static network visualizations of memory connections.
Usage: python3 graph.py [output.png]
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import networkx as nx
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from memory_indexer import build_index, get_knowledge_graph

def generate_graph(output_path=None):
    """Generate and save knowledge graph PNG."""
    if not HAS_MATPLOTLIB:
        print("matplotlib/networkx not available — install with: pip install matplotlib networkx")
        return

    g_data = get_knowledge_graph()
    G = nx.DiGraph()

    # Add nodes
    topic_colors = {}
    cmap = plt.cm.get_cmap('tab20')

    for i, node in enumerate(g_data["nodes"]):
        G.add_node(node["id"], label=node["label"], type=node["type"],
                   count=node.get("count", node.get("topic_count", 1)))
        if node["type"] == "topic":
            topic_colors[node["id"]] = cmap(i % 20)

    # Add edges
    for edge in g_data["edges"]:
        G.add_edge(edge["source"], edge["target"], type=edge["type"])

    # Layout
    plt.figure(figsize=(20, 16))
    plt.style.use('dark_background')

    # Separate topic and file nodes
    topics = [n for n in G.nodes() if G.nodes[n].get("type") == "topic"]
    files = [n for n in G.nodes() if G.nodes[n].get("type") == "file"]

    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw topic nodes
    topic_sizes = [400 + G.nodes[t].get("count", 1) * 200 for t in topics]
    nx.draw_networkx_nodes(G, pos, nodelist=topics,
                           node_color=[topic_colors.get(t, 'purple') for t in topics],
                           node_size=topic_sizes, alpha=0.9)
    nx.draw_networkx_labels(G, pos, labels={t: G.nodes[t]["label"] for t in topics},
                            font_size=9, font_color='white', font_weight='bold')

    # Draw file nodes (dimmed)
    if files:
        nx.draw_networkx_nodes(G, pos, nodelist=files,
                               node_color='steelblue', node_size=80, alpha=0.4)
        nx.draw_networkx_labels(G, pos, labels={f: G.nodes[f]["label"][:20] for f in files},
                                font_size=6, font_color='#a0a0c0')

    # Draw edges
    topic_edges = [(u, v) for u, v in G.edges() if G.nodes[u].get("type") == "file" or G.nodes[v].get("type") == "file"]
    other_edges = [(u, v) for u, v in G.edges() if (u, v) not in topic_edges]

    nx.draw_networkx_edges(G, pos, edgelist=other_edges,
                           edge_color='#6B2D8C', alpha=0.5, width=1.5, arrows=True)
    nx.draw_networkx_edges(G, pos, edgelist=topic_edges,
                           edge_color='#3a3a6a', alpha=0.3, width=0.5)

    plt.title("Charlie's Holographic Memory — Knowledge Graph", fontsize=16, color='white', pad=20)
    plt.axis('off')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
        print(f"Graph saved: {output_path}")
    else:
        plt.show()

    plt.close()

def generate_topic_sunburst(output_path=None):
    """Generate a sunburst/ring chart of topics."""
    if not HAS_MATPLOTLIB:
        print("matplotlib not available")
        return

    from memory_indexer import build_index
    idx = build_index()

    topic_counts = [(t, len(es)) for t, es in idx["topics"].items() if len(es) > 0]
    topic_counts.sort(key=lambda x: -x[1])

    fig, ax = plt.subplots(figsize=(14, 10), subplot_kw=dict(projection='polar'))
    plt.style.use('dark_background')

    N = len(topic_counts)
    angles = [n / (N / 2.0) * 3.14159 for n in range(N)]
    radii = [c[1] * 8 + 20 for c in topic_counts]
    colors = plt.cm.tab20(range(N))

    bars = ax.bar(angles, radii, width=3.14159 / N, bottom=0, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax.set_xticks(angles)
    ax.set_xticklabels([c[0].replace("_", "\n") for c in topic_counts], fontsize=7)
    ax.set_yticks([])

    # Add count labels
    for angle, bar, (topic, count) in zip(angles, bars, topic_counts):
        bar.set_height(bar.get_height() * 0.7)
        ax.text(angle, bar.get_height() + 5, str(count), ha='center', va='center',
                fontsize=8, color='white', fontweight='bold')

    plt.title("Memory Topics — Sunburst View", fontsize=14, color='white', pad=30)
    plt.axis('off')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
        print(f"Sunburst saved: {output_path}")
    else:
        plt.show()
    plt.close()

def generate_timeline(output_path=None):
    """Generate a timeline of daily memory files."""
    if not HAS_MATPLOTLIB:
        print("matplotlib not available")
        return

    from memory_indexer import build_index
    from collections import Counter
    import re

    idx = build_index()

    # Extract dates
    dates = []
    for entry in idx["files"]:
        d = entry.get("date")
        if d:
            dates.append(d)

    date_counts = Counter(dates)
    sorted_dates = sorted(date_counts.items())

    if not sorted_dates:
        print("No dates found")
        return

    fig, ax = plt.subplots(figsize=(16, 6))
    plt.style.use('dark_background')

    x = range(len(sorted_dates))
    y = [c for _, c in sorted_dates]
    labels = [d for d, _ in sorted_dates]

    # Color bars by topic density
    topic_densities = []
    for d, _ in sorted_dates:
        entries_on_date = [e for e in idx["files"] if e.get("date") == d]
        density = sum(len(e.get("topics", [])) for e in entries_on_date)
        topic_densities.append(density)

    colors = [plt.cm.plasma(min(td / 20, 1.0)) for td in topic_densities]

    ax.bar(x, y, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x[::max(1, len(x)//20)])
    ax.set_xticklabels(labels[::max(1, len(x)//20)], rotation=45, fontsize=7, ha='right')
    ax.set_ylabel("Entries", color='white')
    ax.set_title("Memory Timeline", fontsize=14, color='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')
    ax.set_facecolor('#0a0a1a')
    fig.patch.set_facecolor('#0a0a1a')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
        print(f"Timeline saved: {output_path}")
    else:
        plt.show()
    plt.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Holographic Memory Graph Generator")
    parser.add_argument("-o", "--output", default=None, help="Output PNG path")
    parser.add_argument("-t", "--type", choices=["graph", "sunburst", "timeline"], default="graph",
                        help="Type of visualization")
    args = parser.parse_args()

    output = args.output or f"/home/damato/.openclaw/workspace/tools/holographic-memory/data/{args.type}.png"

    if args.type == "graph":
        generate_graph(output)
    elif args.type == "sunburst":
        generate_topic_sunburst(output)
    elif args.type == "timeline":
        generate_timeline(output)
