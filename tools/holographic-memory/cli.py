#!/usr/bin/env python3
"""
Holographic Memory — Terminal Interactive CLI
Rich terminal UI for browsing and searching memory.
Usage: python3 cli.py [search query]
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_indexer import build_index, search, TOPIC_PATTERNS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.tree import Tree
from rich.syntax import Syntax
import re

console = Console()

def render_file_content(filepath, max_lines=60):
    """Display file content with syntax highlighting."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except:
        console.print(f"[red]Could not read {filepath}[/red]")
        return

    name = os.path.basename(filepath)
    content = "".join(lines[:max_lines])
    if len(lines) > max_lines:
        content += f"\n... [{len(lines) - max_lines} more lines]"

    syntax = Syntax(content, "markdown", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"[bold]{name}[/bold]", border_style="purple"))

def cmd_browse(args):
    """Browse all files or filter by topic."""
    idx = build_index()
    topic = args[0] if args else ""

    if topic:
        entries = [e for e in idx["files"] if topic in e["topics"]]
    else:
        entries = idx["files"]

    entries.sort(key=lambda x: x.get("date") or "", reverse=True)

    table = Table(title=f"Memory Files {'(topic: ' + topic + ')' if topic else ''}", show_lines=True)
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Title", style="bold")
    table.add_column("Topics", style="magenta")
    table.add_column("Summary", style="dim")

    for e in entries:
        topics_str = ", ".join(e["topics"][:3])
        summary = e["summary"][:60] + "..." if len(e["summary"]) > 60 else e["summary"]
        table.add_row(
            e.get("date") or "—",
            e["title"][:40],
            topics_str,
            summary
        )

    console.print(table)
    console.print(f"\n[dim]{len(entries)} files[/dim]")

def cmd_topics(args):
    """Show all topics."""
    idx = build_index()
    table = Table(title="Memory Topics", show_lines=True)
    table.add_column("Topic", style="cyan")
    table.add_column("Files", style="magenta", justify="right")
    table.add_column("Patterns", style="dim")

    topic_list = [(t, len(es), TOPIC_PATTERNS.get(t, [])[:3]) for t, es in idx["topics"].items()]
    topic_list.sort(key=lambda x: -x[1])

    for topic, count, patterns in topic_list:
        table.add_row(topic.replace("_", " ").title(), str(count), ", ".join(patterns))

    console.print(table)

def cmd_search(args):
    """Search memory files."""
    if not args:
        console.print("[yellow]Usage: search <query>[/yellow]")
        return

    query = " ".join(args)
    idx = build_index()
    results = search(query, idx, limit=15)

    if not results:
        console.print(f"[dim]No results for '{query}'[/dim]")
        return

    console.print(f"\n[bold]Results for '[cyan]{query}[/cyan]'[/bold] ({len(results)} found)\n")

    for r in results:
        e = r["entry"]
        matched = " | ".join(r["matched_in"][:4])
        console.print(Panel(
            f"[bold magenta]{e['title']}[/bold magenta]\n"
            f"[cyan]{matched}[/cyan]\n\n"
            f"[dim]{e['summary'][:120]}...[/dim]\n"
            f"[green]score: {r['score']}[/green] | [yellow]{e.get('date','—')}[/yellow]",
            border_style="purple",
        ))

def cmd_graph(args):
    """Show knowledge graph as ASCII art."""
    idx = build_index()

    # Topic network
    tree = Tree("[bold purple]Knowledge Graph[/bold purple]")
    topic_list = [(t, len(es)) for t, es in idx["topics"].items() if len(es) > 0]
    topic_list.sort(key=lambda x: -x[1])

    for topic, count in topic_list[:10]:
        entries = idx["topics"][topic][:4]
        entry_names = [e["title"][:30] for e in entries]
        topic_node = tree.add(f"[cyan]{topic.replace('_',' ').title()}[/cyan] ({count})")
        for name in entry_names:
            topic_node.add(f"[dim]{name}[/dim]")

    console.print(tree)

def cmd_read(args):
    """Read a memory file."""
    if not args:
        console.print("[yellow]Usage: read <filename or number>[/yellow]")
        return

    idx = build_index()
    query = " ".join(args).lower()

    # Try to match by file number or name
    try:
        num = int(query)
        if 0 < num <= len(idx["files"]):
            filepath = idx["files"][num - 1]["path"]
            render_file_content(filepath)
            return
    except ValueError:
        pass

    # Search by name
    matches = [e for e in idx["files"] if query in e["title"].lower() or query in e["path"].lower()]
    if len(matches) == 1:
        render_file_content(matches[0]["path"])
    elif len(matches) > 1:
        console.print("[yellow]Multiple matches:[/yellow]")
        for i, m in enumerate(matches, 1):
            console.print(f"  {i}. {m['title']}")
    else:
        console.print(f"[red]No file found matching '{query}'[/red]")

def cmd_stats(args):
    """Show memory statistics."""
    idx = build_index()

    col1 = f"[bold]Total files:[/bold] {len(idx['files'])}\n"
    col1 += f"[bold]Topics tracked:[/bold] {len([t for t in len(idx['topics']) if len(idx['topics'][t]) > 0])}\n"

    topic_counts = [(t, len(es)) for t, es in idx["topics"].items() if len(es) > 0]
    topic_counts.sort(key=lambda x: -x[1])

    console.print(Panel(f"[cyan]{col1}[/cyan]", title="Memory Stats", border_style="purple"))
    console.print("\n[bold]Top Topics:[/bold]")
    for topic, count in topic_counts[:10]:
        bar = "█" * min(count, 30)
        console.print(f"  [magenta]{topic:<20}[/magenta] [cyan]{bar}[/cyan] {count}")

def cmd_help(args):
    help_text = """
[bold cyan]Holographic Memory CLI[/bold cyan]

[bold]Commands:[/bold]
  list              Browse all memory files
  topics            Show all topics
  search <query>    Search memory files
  read <file>       Read a file (by name or number)
  graph             Show knowledge graph
  stats             Show memory statistics
  help              Show this help

[bold]Examples:[/bold]
  list racing       Browse files about racing
  search picks      Search for 'picks'
  read MEMORY       Read MEMORY.md
  read 3            Read 3rd file in list

[bold]Shortcuts:[/bold]
  l                 list
  t                 topics
  s <query>         search
  r <file>          read
  g                 graph
  ?                 help
"""
    console.print(Markdown(help_text))

COMMANDS = {
    "list": (cmd_browse, "Browse files [topic]"),
    "topics": (cmd_topics, "Show all topics"),
    "search": (cmd_search, "Search memory"),
    "read": (cmd_read, "Read a file"),
    "graph": (cmd_graph, "Show knowledge graph"),
    "stats": (cmd_stats, "Show statistics"),
    "help": (cmd_help, "Show help"),
    "l": (cmd_browse, "Browse files"),
    "t": (cmd_topics, "Show topics"),
    "s": (cmd_search, "Search"),
    "r": (cmd_read, "Read"),
    "g": (cmd_graph, "Graph"),
    "?": (cmd_help, "Help"),
}

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        args = sys.argv[2:]
    else:
        console.print("[bold purple]🧠 Holographic Memory CLI[/bold purple]")
        cmd = Prompt.ask("\n[cyan]Command[/cyan]", choices=list(COMMANDS.keys()), default="help")
        args = []
        if cmd in ("search", "s", "read", "r"):
            query = Prompt.ask("[cyan]Query[/cyan]")
            args = query.split()

    if cmd in COMMANDS:
        COMMANDS[cmd][0](args)
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        cmd_help([])

if __name__ == "__main__":
    main()
