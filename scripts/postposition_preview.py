#!/usr/bin/env python3
"""Preview the saddlecloth post position colors."""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Saddlecloth colors from the file
COLORS = [
    {"post": 1, "background": "#FF0000", "number": "#FFFFFF"},
    {"post": 2, "background": "#FFFFFF", "number": "#000000"},
    {"post": 3, "background": "#0000FF", "number": "#FFFFFF"},
    {"post": 4, "background": "#FFFF00", "number": "#000000"},
    {"post": 5, "background": "#008000", "number": "#FFFFFF"},
    {"post": 6, "background": "#000000", "number": "#FFDD00"},
    {"post": 7, "background": "#FF7F00", "number": "#000000"},
    {"post": 8, "background": "#FF69B4", "number": "#000000"},
    {"post": 9, "background": "#00CED1", "number": "#000000"},
    {"post": 10, "background": "#800080", "number": "#FFFFFF"},
    {"post": 11, "background": "#808080", "number": "#FF0000"},
    {"post": 12, "background": "#ADFF2F", "number": "#000000"},
    {"post": 13, "background": "#8B4513", "number": "#FFFFFF"},
    {"post": 14, "background": "#A52A2A", "number": "#FFDD00"},
    {"post": 15, "background": "#F0E68C", "number": "#000000"},
    {"post": 16, "background": "#7EC8E8", "number": "#FF7F00"},
    {"post": 17, "background": "#000080", "number": "#FFFFFF"},
    {"post": 18, "background": "#006400", "number": "#FFDD00"},
    {"post": 19, "background": "#4682B4", "number": "#FF0000"},
    {"post": 20, "background": "#FF1493", "number": "#FFDD00"},
    {"post": 21, "background": "#E6E6FA", "number": "#000080"},
    {"post": 22, "background": "#003366", "number": "#FFFFFF"},
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def create_preview():
    c = canvas.Canvas("/home/damato/.openclaw/workspace/postposition_preview.pdf", pagesize=landscape(letter))
    width, height = landscape(letter)

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 40, "Post Position Color Chart")

    # Grid: 11 columns, 2 rows
    cols = 11
    box_size = 50
    gap = 8
    start_x = (width - (cols * (box_size + gap))) / 2
    start_y = height - 100

    for i, item in enumerate(COLORS):
        row = i // cols
        col = i % cols
        x = start_x + col * (box_size + gap)
        y = start_y - row * (box_size + gap + 20)

        # Draw filled square
        bg_rgb = hex_to_rgb(item["background"])
        c.setFillColorRGB(*bg_rgb)
        c.rect(x, y, box_size, box_size, fill=1, stroke=1)

        # Draw post number centered
        num_rgb = hex_to_rgb(item["number"])
        c.setFillColorRGB(*num_rgb)
        c.setFont("Helvetica-Bold", 20)
        num_width = c.stringWidth(str(item["post"]), "Helvetica-Bold", 20)
        c.drawString(x + (box_size - num_width)/2, y + box_size/2 - 7, str(item["post"]))

        # Label below
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 9)
        c.drawCentredString(x + box_size/2, y - 12, f"#{item['post']}")

    c.save()
    print("Created: /home/damato/.openclaw/workspace/postposition_preview.pdf")

create_preview()
