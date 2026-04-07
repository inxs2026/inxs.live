#!/usr/bin/env python3
"""
picks_pdf_template.py — Template for GP Picks PDF scripts.
Copy this for each new race day. NEVER hardcode PP colours.
Always use pp_colors.py for badge colours and text.

Key rule: pp_text_hex(pp) returns the correct hex for the number text.
#6 = yellow text on black, #7 = black text on orange, etc.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_badge_style, pp_text_hex, pp_border_color

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import datetime

# ── RACE DATA — fill this in ───────────────────────────────────────────────
RACES = [
    # {
    #     "num": 1, "post": "12:50 ET",
    #     "cond": "Claiming $25,000 N2L | 3yo+ | 1 Mile Turf",
    #     "note": "",   # scratches or surface changes
    #     "par": 78,
    #     "picks": [
    #         {"pp": 6, "name": "HORSE NAME",
    #          "beyer": "88-85-90 | Avg: 87.7",
    #          "trainer": "Trainer Name (stat%)",
    #          "jockey": "Jockey Name",
    #          "comment": "2-3 sentence explanation."},
    #     ]
    # },
]

def build_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    title_style    = ParagraphStyle('title',   parent=styles['Title'],  fontSize=20, textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    sub_style      = ParagraphStyle('sub',     parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#666666'), spaceAfter=16, alignment=TA_CENTER)
    rh_style       = ParagraphStyle('rh',      parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold', textColor=colors.white)
    cond_style     = ParagraphStyle('cond',    parent=styles['Normal'], fontSize=9,  textColor=colors.HexColor('#444444'), spaceAfter=4)
    beyer_style    = ParagraphStyle('beyer',   parent=styles['Normal'], fontSize=9,  textColor=colors.HexColor('#2c5f2e'), fontName='Helvetica-Bold')
    trainer_style  = ParagraphStyle('trainer', parent=styles['Normal'], fontSize=8,  textColor=colors.HexColor('#555555'))
    comment_style  = ParagraphStyle('comment', parent=styles['Normal'], fontSize=9,  textColor=colors.HexColor('#333333'), leading=13)
    note_style     = ParagraphStyle('note',    parent=styles['Normal'], fontSize=8,  textColor=colors.HexColor('#cc4400'), fontName='Helvetica-Oblique')
    footer_style   = ParagraphStyle('footer',  parent=styles['Normal'], fontSize=8,  textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    story = []
    story.append(Paragraph("🏇 Gulfstream Park – RACE DATE", title_style))
    story.append(Paragraph("Charlie's Top-3 Picks | Beyers + Form + Class + Angles", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 10))

    pick_labels = ["🥇 WIN", "🥈 PLACE", "🥉 SHOW"]

    for race in RACES:
        hdr = Table([[Paragraph(f"RACE {race['num']}  |  Post: {race['post']}  |  Par: {race['par'] if race['par'] else 'N/A'}", rh_style)]],
                    colWidths=[7.5*inch])
        hdr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(hdr)
        story.append(Paragraph(race['cond'], cond_style))
        if race.get('note'):
            story.append(Paragraph(f"⚠️ {race['note']}", note_style))

        for i, pick in enumerate(race['picks']):
            pp     = pick['pp']
            bg_col = PP_COLORS.get(pp, colors.gray)
            fg_hex = pp_text_hex(pp)   # ← ALWAYS use this, never hardcode white/black
            bdr    = pp_border_color(pp)
            label  = pick_labels[i]
            pp_txt = f"#{pp}" if pp else "??"

            data = [
                [Paragraph(f"<b><font color='{fg_hex}'>{pp_txt}</font></b>",
                           ParagraphStyle('pp', fontSize=13, fontName='Helvetica-Bold', alignment=TA_CENTER)),
                 Paragraph(f"{label}  <b>{pick['name']}</b>",
                           ParagraphStyle('nm', fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a1a2e')))],
                ["", Paragraph(f"📊 {pick['beyer']}", beyer_style)],
                ["", Paragraph(f"🎽 {pick['trainer']}  |  👤 {pick['jockey']}", trainer_style)],
                ["", Paragraph(pick['comment'], comment_style)],
            ]
            t = Table(data, colWidths=[0.55*inch, 6.95*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (0,-1), bg_col),
                ('BACKGROUND',    (1,0), (1,-1), colors.HexColor('#F8F9FA')),
                ('SPAN',          (0,0), (0,-1)),
                ('VALIGN',        (0,0), (0,-1), 'MIDDLE'),
                ('ALIGN',         (0,0), (0,-1), 'CENTER'),
                ('TOPPADDING',    (1,0), (1,0),  8),
                ('BOTTOMPADDING', (1,-1),(1,-1),  8),
                ('LEFTPADDING',   (1,0), (1,-1),  8),
                ('RIGHTPADDING',  (1,0), (1,-1),  8),
                ('TOPPADDING',    (0,0), (0,-1),  0),
                ('BOTTOMPADDING', (0,0), (0,-1),  0),
                ('BOX',           (0,0), (-1,-1), 1,   colors.HexColor('#DDDDDD')),
                ('BOX',           (0,0), (0,-1),  1.5, bdr),   # border for white/yellow badges
                ('LINEABOVE',     (1,1), (1,1),   0.5, colors.HexColor('#EEEEEE')),
                ('LINEABOVE',     (1,2), (1,2),   0.5, colors.HexColor('#EEEEEE')),
                ('LINEABOVE',     (1,3), (1,3),   0.5, colors.HexColor('#EEEEEE')),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC')))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by Charlie | {datetime.date.today().strftime('%B %d, %Y')} | For entertainment only.",
        footer_style))
    doc.build(story)
    print(f"PDF created: {output_path}")

if __name__ == "__main__":
    build_pdf("GP_Picks_DATE.pdf")
