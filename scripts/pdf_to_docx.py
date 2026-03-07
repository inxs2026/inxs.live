#!/usr/bin/env python3
"""
pdf_to_docx.py — Convert PDF to Microsoft Word (.docx)
Usage: python3 pdf_to_docx.py <input.pdf> [output.docx]

If output path is omitted, saves alongside the PDF with .docx extension.
"""

import sys
import os
from pathlib import Path

def convert(pdf_path: str, docx_path: str = None):
    pdf = Path(pdf_path)

    if not pdf.exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    if not pdf.suffix.lower() == '.pdf':
        print(f"❌ Input must be a PDF file: {pdf_path}")
        sys.exit(1)

    if docx_path is None:
        docx_path = str(pdf.with_suffix('.docx'))

    print(f"📄 Input:  {pdf}")
    print(f"📝 Output: {docx_path}")
    print("Converting...")

    from pdf2docx import Converter
    cv = Converter(str(pdf))
    cv.convert(docx_path, start=0, end=None)
    cv.close()

    size = Path(docx_path).stat().st_size / 1024
    print(f"✅ Done! {docx_path} ({size:.1f} KB)")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_to_docx.py <input.pdf> [output.docx]")
        sys.exit(1)

    pdf_in = sys.argv[1]
    docx_out = sys.argv[2] if len(sys.argv) >= 3 else None
    convert(pdf_in, docx_out)
