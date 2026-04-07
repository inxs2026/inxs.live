#!/usr/bin/env python3
"""
GP Picks - April 5, 2026
PPs: TrackData MCP | Beyers: DRF (parse_drf.py)
Style: Same as April 4 picks (PP badge + comment block)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.pp_colors import PP_COLORS, pp_text_hex, pp_border_color

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import datetime

RACES = [
    {
        "num": 1, "post": "12:50 PM ET",
        "cond": "Maiden Claiming $35K | 3yo+ | 1 Mile Turf | Beyer Par: 75",
        "note": "SCRATCH: #6 No More War (vet)",
        "par": 75,
        "picks": [
            {"pp": 11, "name": "FREAKY",
             "beyer": "83-84-88 | Avg: 85.0",
             "trainer": "Pletcher Todd A (18%)",
             "jockey": "Camacho S",
             "comment": "Highest Beyer average in race (85.0). Consistent 83-88 range. Just missed with 83 at this class. Pletcher 18% is top trainer. At 5-2 ML — short but deserved. Best in race."},
            {"pp": 10, "name": "LOCO POR SER LIBRE",
             "beyer": "86-85-71 | Avg: 80.7",
             "trainer": "Rodriguez Angel M (7%)",
             "jockey": "Gonzalez JL",
             "comment": "Second highest Beyer average (80.7). Won at this class/distance with 86. Top figure 91. At 30-1 ML — massive overlay. Use for exotics, possible upset."},
            {"pp": 8, "name": "SWAMP FOX",
             "beyer": "80-63-71 | Avg: 71.3",
             "trainer": "Antonacci Philip (7%)",
             "jockey": "Ruiz J",
             "comment": " turf winner. Won at GP with 80 Beyer. At 8-1 ML — fair exotic price. Antonacci 7% is weak but horse runs consistent. For exotics."},
        ]
    },
    {
        "num": 2, "post": "1:20 PM ET",
        "cond": "Claiming $8K N2L (Fillies/Mares) | 3yo+ | 7 Furlongs | Beyer Par: 59",
        "note": "SCRATCH: #7 Lady O'Brien (vet)",
        "par": 59,
        "picks": [
            {"pp": 2, "name": "HORSEPLAY",
             "beyer": "78-75-77 | Avg: 76.7",
             "trainer": "Hills Timothy A (9%)",
             "jockey": "Maragh R",
             "comment": "Highest Beyer average in race (76.7). Won last start at MTH with 82 Beyer. Best recent race (82) shows room to improve. Hills 9% is OK. At 3-1 ML — short but earned."},
            {"pp": 5, "name": "LA DINAMITA",
             "beyer": "74-79-76 | Avg: 76.3",
             "trainer": "Chapman Beau J (10%)",
             "jockey": "Vasquez M",
             "comment": " turf winner. Consistent 74-84 range. Won at this class with 84. At 5-2 ML — fair price. Chapman 10% is solid. Exotic value."},
            {"pp": 4, "name": "MY SWEET ADALINE",
             "beyer": "79-58-74 | Avg: 70.3",
             "trainer": "McKanas Leon J (10%)",
             "jockey": "Gonzalez JL",
             "comment": " turf winner. Won at this class with 79. Best recent race (79) shows potential. At 15-1 ML — solid exotic value. Gonzalez JL rides well for McKanas."},
        ]
    },
    {
        "num": 3, "post": "1:50 PM ET",
        "cond": "Maiden Claiming $30K (Fillies/Mares) | 3yo+ | 5.5 Furlongs | Beyer Par: 68",
        "note": None,
        "par": 68,
        "picks": [
            {"pp": 7, "name": "THE OTHER ONE",
             "beyer": "85-65 | Avg: 75.0",
             "trainer": "Casse Mark (14%)",
             "jockey": "Vasquez M",
             "comment": "Highest Beyer in race (avg 75.0, top 85). Won OC at this class with 85. Casse 14% is top connections. At 2-1 ML — short but clear class edge over this field."},
            {"pp": 3, "name": "KHOZY ME UP",
             "beyer": "82-78 | Avg: 80.0",
             "trainer": "Jehaludi Amzadali (7%)",
             "jockey": "Martinez C",
             "comment": " turf winner. Only 2 starts so avg equals top races. Won at this class with 82. At 6-1 ML — best exotic value in the race."},
            {"pp": 6, "name": "TERRIMENDOUS",
             "beyer": "74-84-73 | Avg: 73.0",
             "trainer": "Santiago Joel (7%)",
             "jockey": "Torres Y",
             "comment": " turf winner. Consistent 73-84 range. Won at this class with 84. At 3-1 ML — fair price for exotics. Santiago 7% is weak but horse honest."},
        ]
    },
    {
        "num": 4, "post": "2:20 PM ET",
        "cond": "Claiming $25K N2L | 3yo+ | 5 Furlongs | Beyer Par: 63",
        "note": None,
        "par": 63,
        "picks": [
            {"pp": 5, "name": "RENT'S DUE",
             "beyer": "80 | Only start",
             "trainer": "Chapman Beau J (10%)",
             "jockey": "Husbands MJ",
             "comment": "Best Beyer in race (80). Won at this class/distance with 80. Consistent. Chapman 10% is solid. At 4-1 ML — playable."},
            {"pp": 6, "name": "IL PRINCIPADO",
             "beyer": "84-61-82 | Avg: 75.7",
             "trainer": "Barboza Victor Jr (11%)",
             "jockey": "Perez E",
             "comment": " turf winner. Best recent race: 84 at GP. Won at this class. At 5-2 ML — deserved. Barboza 11% is solid. Win candidate."},
            {"pp": 2, "name": "SKEDADDLING HOME",
             "beyer": "79-62-85 | Avg: 75.3",
             "trainer": "Trombetta Michael J (8%)",
             "jockey": "Lopez P",
             "comment": " turf winner. Won at this class with 85. At 2-1 ML — too short for inconsistent Beyers (62-85 range). Only for exotics."},
        ]
    },
    {
        "num": 5, "post": "2:50 PM ET",
        "cond": "Claiming $12,500 | 3yo+ | 1 1/16 Miles | Beyer Par: 74",
        "note": None,
        "par": 74,
        "picks": [
            {"pp": 7, "name": "CAIRO COMEDY",
             "beyer": "77-74-80 | Avg: 77.0",
             "trainer": "Spatz Ronald B (5%)",
             "jockey": "Zayas EJ",
             "comment": "Highest Beyer avg in race (77.0). Won at this class with 80. Best early pace in race. At 9-2 ML — fair price. Spatz 5% is weak but horse is clearly best in race."},
            {"pp": 2, "name": "SOUFFLE ON FIRE",
             "beyer": "75-78-76 | Avg: 76.3",
             "trainer": "Joseph Saffie A Jr (18%)",
             "jockey": "Husbands MJ",
             "comment": " turf winner. Consistent 70-78 range. Won at GP with 78. Joseph 18% is best trainer in race. At 5-2 ML — short but deserved. Win candidate."},
            {"pp": 1, "name": "CORONA PRINCESS",
             "beyer": "79 | Top figure",
             "trainer": "Seyler Douglas J (5%)",
             "jockey": "Ocasio J",
             "comment": " turf winner. Top Beyer 79. At 30-1 ML — biggest overlay in race. Won at this distance with 79. Seyler 5% is very weak. Use for exotics only."},
        ]
    },
    {
        "num": 6, "post": "3:20 PM ET",
        "cond": "Starter Allowance $50K | 3yo+ | 7 Furlongs | Beyer Par: 71",
        "note": None,
        "par": 71,
        "picks": [
            {"pp": 7, "name": "SNEAK PREVIEW",
             "beyer": "83-85-86 | Avg: 84.7",
             "trainer": "Fawkes David (15%)",
             "jockey": "Perez E",
             "comment": "Highest Beyer avg in race (84.7). Consistent 82-86 range. Won at this class with 86. Fawkes 15% is solid. At 9-5 ML — clear class edge. Win candidate."},
            {"pp": 3, "name": "ANTILLEAN",
             "beyer": "80-81-91 | Avg: 84.0",
             "trainer": "Arscott Garrett W (7%)",
             "jockey": "Henry W",
             "comment": " turf winner. Won at this class with 91 Beyer — dominant. At 6-1 ML — best exotic value in race. Arscott 7% is a concern but the 91 speaks."},
            {"pp": 6, "name": "CROSS HASTE",
             "beyer": "70-82-74 | Avg: 74.3",
             "trainer": "Garcia Pedro R (7%)",
             "jockey": "Torres Y",
             "comment": " turf winner. Won at this class with 85. Garcia 7% is weak. At 8-1 ML — exotic value only. Best closing kick in race."},
        ]
    },
    {
        "num": 7, "post": "3:50 PM ET",
        "cond": "Starter Allowance $25K | 3yo+ | 1 Mile Turf | Beyer Par: 74",
        "note": "SCRATCH: #1 Del Mar Sunrise (vet). Field of 6.",
        "par": 74,
        "picks": [
            {"pp": 2, "name": "COME ON POPPI",
             "beyer": "Debut — works :50, :51",
             "trainer": "Barboza Victor Jr (11%)",
             "jockey": "Ruiz J",
             "comment": " turf winner from works alone. Small field (6 runners) favors debuters. Barboza 11% is solid. At 5-2 ML — short for a debut but small field reduces risk. Win candidate."},
            {"pp": 4, "name": "TIGER EYE PEARL",
             "beyer": "68-79 | Avg: 73.5",
             "trainer": "Wilkes Ian R (5%)",
             "jockey": "Zayas EJ",
             "comment": " turf winner. Won at GP with 79. At 6-1 ML — solid exotic value. Small field = less traffic. Wilkes 5% is weak but horse runs honest."},
            {"pp": 3, "name": "BOMBS AWAY",
             "beyer": "62-82-74 | Avg: 72.7",
             "trainer": "Maragh Collin (7%)",
             "jockey": "Maragh R",
             "comment": " turf winner. Best race (82) shows potential. At 10-1 ML — best exotic price in race. Maragh R (jockey) is hot. Exotics only."},
        ]
    },
    {
        "num": 8, "post": "4:20 PM ET",
        "cond": "Claiming $16K N2L | 3yo+ | 1 Mile 70Y Turf | Beyer Par: 74",
        "note": None,
        "par": 74,
        "picks": [
            {"pp": 4, "name": "OUTLAW COUNTRY",
             "beyer": "83-86-88 | Avg: 85.7",
             "trainer": "Sano Antonio (11%)",
             "jockey": "Zayas EJ",
             "comment": " turf winner. Highest Beyer in race (85.7 avg). Won at GP with 92 Beyer — dominant. At 6-1 ML — best value play in race. Sano 11% is solid. Win candidate."},
            {"pp": 3, "name": "SCHNITTKER",
             "beyer": "90-87-93 | Avg: 84.7",
             "trainer": "Delgado Jorge (7%)",
             "jockey": "Husbands MJ",
             "comment": " turf winner. Won at this class with 93. At 2-1 ML — too short given Outlaw Country's 85.7 avg. Exotics underneath."},
            {"pp": 2, "name": "BOLD ADVANCE",
             "beyer": "79-78-82 | Avg: 79.7",
             "trainer": "Barboza Victor Jr (11%)",
             "jockey": "Vasquez M",
             "comment": " turf winner. Won at GP with 87. At 6-1 ML — solid exotic value. Barboza 11% is solid. Third-best Beyer in race."},
        ]
    },
    {
        "num": 9, "post": "4:50 PM ET",
        "cond": " AOC $75K N1X (Fillies/Mares) | 3yo+ | 6 Furlongs Turf | Beyer Par: 80",
        "note": "SCRATCH: #3 Mish (stewards). Field of 6.",
        "par": 80,
        "picks": [
            {"pp": 7, "name": "BEACH COLT",
             "beyer": "84-92-91 | Avg: 89.0",
             "trainer": "Sanchez Amador M (7%)",
             "jockey": "Herrera DA",
             "comment": "Highest Beyer in race (89.0). Won on turf at GP with 92-91. turf 3/3. At 3-1 ML — best value in race. Win candidate."},
            {"pp": 5, "name": "ROLANDO",
             "beyer": "86-90-89 | Avg: 88.3",
             "trainer": "Gutierrez Fausto (7%)",
             "jockey": "Zayas EJ",
             "comment": " turf winner. Consistent 86-90 range. Won at this class with 90. At 9-2 ML — solid exotic. Gutierrez 7% is weak but horse is real."},
            {"pp": 1, "name": "GREAT NAVIGATOR",
             "beyer": "84-85-89 | Avg: 86.0",
             "trainer": "Owens Eddie Jr (7%)",
             "jockey": "Perez E",
             "comment": " turf winner. Won at this class with 89. At 8-1 ML — good exotic value. Owens 7% is weak. Third-best Beyer in race."},
        ]
    },
    {
        "num": 10, "post": "5:20 PM ET",
        "cond": " AOC $75K N1X | 3yo+ | 5 Furlongs Turf | Beyer Par: 78",
        "note": "SCRATCH: #8 First Empire (vet). Field of 8.",
        "par": 78,
        "picks": [
            {"pp": 9, "name": "BOAT'S A ROCKIN",
             "beyer": "97-90-96 | Avg: 94.3",
             "trainer": "Abreu Fernando (5%)",
             "jockey": "Gonzalez E",
             "comment": "Highest Beyer avg in race (94.3). Won at this class with 97. At 9-5 ML — fair price for this class of horse. Win candidate."},
            {"pp": 3, "name": "BIZ BIZ BUZZ",
             "beyer": "95-86-94 | Avg: 91.7",
             "trainer": "D'Angelo Jose F (14%)",
             "jockey": "Camacho S",
             "comment": " turf winner. Won at GP with 96. D'Angelo 14% is best trainer in race. At 8-1 ML — best exotic value. Exotics."},
            {"pp": 5, "name": "ESPERON",
             "beyer": "95-87-92 | Avg: 91.3",
             "trainer": "Braddy J David (7%)",
             "jockey": "Zayas EJ",
             "comment": " turf winner. Won at GP with 95. At 9-2 ML — solid exotic. Braddy 7% is weak but 91+ Beyers are real."},
        ]
    },
]

def build_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    title_style   = ParagraphStyle('title',   parent=styles['Title'],  fontSize=20, textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    sub_style     = ParagraphStyle('sub',     parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#666666'), spaceAfter=16, alignment=TA_CENTER)
    rh_style      = ParagraphStyle('rh',      parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold', textColor=colors.white)
    cond_style    = ParagraphStyle('cond',    parent=styles['Normal'], fontSize=9,  textColor=colors.HexColor('#444444'), spaceAfter=4)
    beyer_style   = ParagraphStyle('beyer',   parent=styles['Normal'], fontSize=9,  textColor=colors.HexColor('#2c5f2e'), fontName='Helvetica-Bold')
    trainer_style = ParagraphStyle('trainer', parent=styles['Normal'], fontSize=8,  textColor=colors.HexColor('#555555'))
    comment_style = ParagraphStyle('comment', parent=styles['Normal'], fontSize=9,  textColor=colors.HexColor('#333333'), leading=13)
    note_style    = ParagraphStyle('note',    parent=styles['Normal'], fontSize=8,  textColor=colors.HexColor('#cc4400'), fontName='Helvetica-Oblique')
    footer_style  = ParagraphStyle('footer',  parent=styles['Normal'], fontSize=8,  textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    story = []
    story.append(Paragraph("🏇 Gulfstream Park – April 5, 2026", title_style))
    story.append(Paragraph(
        "Charlie's Top-3 Picks | PPs: TrackData MCP | Beyers: DRF (parse_drf.py) | PP Colors: Saddlecloth Chart",
        sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 10))

    pick_labels = ["🥇 WIN", "🥈 PLACE", "🥉 SHOW"]

    for race in RACES:
        race_elems = []

        hdr = Table([[Paragraph(
            f"RACE {race['num']}  |  Post: {race['post']}  |  Par: {race['par']}",
            rh_style)]], colWidths=[7.5*inch])
        hdr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        race_elems.append(hdr)
        race_elems.append(Paragraph(race['cond'], cond_style))
        if race.get('note'):
            race_elems.append(Paragraph(f"⚠️ {race['note']}", note_style))

        for i, pick in enumerate(race['picks']):
            pp     = pick['pp']
            bg_col = PP_COLORS.get(pp, colors.gray)
            fg_hex = pp_text_hex(pp)
            bdr    = pp_border_color(pp)
            label  = pick_labels[i]
            pp_txt = f"#{pp}"

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
                ('BOX',           (0,0), (0,-1),  1.5, bdr),
                ('LINEABOVE',     (1,1), (1,1),   0.5, colors.HexColor('#EEEEEE')),
                ('LINEABOVE',     (1,2), (1,2),   0.5, colors.HexColor('#EEEEEE')),
                ('LINEABOVE',     (1,3), (1,3),   0.5, colors.HexColor('#EEEEEE')),
            ]))
            race_elems.append(t)
            race_elems.append(Spacer(1, 4))

        race_elems.append(Spacer(1, 10))
        story.append(KeepTogether(race_elems))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC')))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by Charlie | April 5, 2026 | PPs verified via TrackData MCP | Beyers from DRF (parse_drf.py) | "
        "PP colors: Saddlecloth Chart | For entertainment only. Verify scratches before wagering.",
        footer_style))
    doc.build(story)
    print(f"PDF created: {output_path}")

if __name__ == "__main__":
    build_pdf("/home/damato/.openclaw/workspace/GP_Picks_Apr05_2026.pdf")
