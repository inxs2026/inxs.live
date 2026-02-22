#!/usr/bin/env python3
import re

with open('FINAL_ALL_RACES.md', 'r') as f:
    md = f.read()

# Simple Markdown to HTML conversion
html = md

# Headers
html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

# Bold
html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

# Italics
html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

# Code
html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)

# Line breaks
html = html.replace('\n\n', '</p><p>')
html = html.replace('\n', '<br>')

# Horizontal rules
html = html.replace('---', '<hr>')

# Stars/emoji
html = html.replace('⭐', '⭐')
html = html.replace('🏇', '🏇')
html = html.replace('🏁', '🏁')
html = html.replace('📊', '📊')
html = html.replace('🌟', '🌟')
html = html.replace('💰', '💰')
html = html.replace('🎯', '🎯')
html = html.replace('📋', '📋')
html = html.replace('⚠️', '⚠️')

# Wrap in HTML
full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Gulfstream Park Picks - February 19, 2026</title>
    <style>
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            max-width: 1000px;
            margin: 20px auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #1a472a;
            border-bottom: 3px solid #2e7d32;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2e7d32;
            margin-top: 30px;
            border-left: 4px solid #4caf50;
            padding-left: 10px;
        }}
        h3 {{
            color: #388e3c;
            margin-top: 20px;
        }}
        strong {{
            color: #1a472a;
        }}
        hr {{
            border: 0;
            border-top: 2px solid #4caf50;
            margin: 30px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #4caf50;
            color: white;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
<p>{html}</p>
</body>
</html>"""

with open('gulfstream_picks.html', 'w') as f:
    f.write(full_html)

print("HTML generated successfully")

