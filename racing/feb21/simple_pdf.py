#!/usr/bin/env python3
"""
Simple text-to-PDF converter using fpdf2 or basic approach
"""
import sys

# Try to use basic text wrapping to PDF
def create_simple_pdf(md_file, pdf_file):
    """Convert markdown to simple PDF"""
    try:
        # Read markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try fpdf2 (might be available)
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Courier", size=9)
            
            # Split into lines and add
            for line in content.split('\n'):
                # Handle special characters
                line = line.encode('latin-1', 'replace').decode('latin-1')
                if len(line) > 90:
                    # Wrap long lines
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= 90:
                            current_line += word + " "
                        else:
                            pdf.cell(0, 4, txt=current_line.strip(), ln=True)
                            current_line = word + " "
                    if current_line:
                        pdf.cell(0, 4, txt=current_line.strip(), ln=True)
                else:
                    pdf.cell(0, 4, txt=line, ln=True)
            
            pdf.output(pdf_file)
            print(f"✅ PDF created: {pdf_file}")
            return True
        except ImportError:
            print("fpdf2 not available, trying alternative...")
            
            # Alternative: just save as text and rename
            with open(pdf_file.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📝 Created text file instead: {pdf_file.replace('.pdf', '.txt')}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 simple_pdf.py input.md output.pdf")
        sys.exit(1)
    
    create_simple_pdf(sys.argv[1], sys.argv[2])
