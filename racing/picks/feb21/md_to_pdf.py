#!/usr/bin/env python3
"""Convert Markdown to PDF using markdown2 and reportlab"""

import sys
from pathlib import Path

try:
    import markdown2
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "markdown2", "reportlab"], check=True)
    # Re-import after installation
    import markdown2
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

def markdown_to_pdf(md_file, pdf_file):
    """Convert markdown file to PDF"""
    
    # Read markdown content
    with open(md_file, 'r') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(md_content)
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='darkgreen',
        spaceAfter=10,
        spaceBefore=12
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Parse HTML and add to PDF
    # Simple parsing - split by lines and format
    lines = md_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 0.1*inch))
            continue
        
        # Handle headers
        if line.startswith('# '):
            text = line[2:].strip()
            elements.append(Paragraph(text, title_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, heading_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            p = Paragraph(f"<b>{text}</b>", body_style)
            elements.append(p)
        elif line.startswith('**') and line.endswith('**'):
            # Bold line (pick headers)
            text = line[2:-2]
            elements.append(Paragraph(f"<b>{text}</b>", body_style))
        elif line.startswith('- ') or line.startswith('* '):
            # Bullet point
            text = line[2:]
            elements.append(Paragraph(f"• {text}", body_style))
        elif line.startswith('---'):
            # Horizontal rule
            elements.append(Spacer(1, 0.2*inch))
        else:
            # Regular text
            if line:
                elements.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF created successfully: {pdf_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 md_to_pdf.py input.md output.pdf")
        sys.exit(1)
    
    md_file = sys.argv[1]
    pdf_file = sys.argv[2]
    
    if not Path(md_file).exists():
        print(f"Error: Input file not found: {md_file}")
        sys.exit(1)
    
    markdown_to_pdf(md_file, pdf_file)
