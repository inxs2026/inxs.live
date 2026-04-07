#!/usr/bin/env python3
"""GP Picks PDF - March 20, 2026"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUTPUT_PATH = "/home/damato/.openclaw/workspace/GP-Picks-Mar20-2026.pdf"

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_badge_style, pp_text_hex, pp_border_color
PICKS = [
    {
        "race": 1, "time": "12:50 ET",
        "conditions": "Md Clm $12,500 | 1 Mile (Dirt) | 3YO",
        "scratches": "TBD — check morning of",
        "note": "Surface: DIRT (no turf alternative listed)",
        "picks": [
            {"rank": 1, "pp": 9, "name": "OTHER LEVEL",
             "beyer": "Avg Beyer (last 3): 76.0 | Figures: 69, 84, 75, 91",
             "analysis": "Best Beyer average in the field at 76.0 with a peak 91 in only his sixth career start. Has been running in better company (MSW) and now drops to MCL$12,500 — class relief is significant. Trainer Sano 10% overall but Zayas (15%) aboard sharpens the angle. Despite the MSW-to-MCL drop, the raw figures are clearly the best here."},
            {"rank": 2, "pp": 7, "name": "WITCHA WISH",
             "beyer": "Avg Beyer (last 3): 68.3 | Best: 76",
             "analysis": "One win on his record (synthetic at Gulfstream) and has shown willingness on dirt. Trainer Ramirez hits at 30% win rate — excellent — and Irad Ortiz Jr (26%) takes the mount. The combination of the best trainer/jockey combo in the race plus a prior win gives him the best credentials to challenge Other Level."},
            {"rank": 3, "pp": 1, "name": "JACKPOT CREE",
             "beyer": "Avg Beyer (last 2): 64.0 | Best: 77",
             "analysis": "Best single-race Beyer in field (77 on March 6) despite weak lifetime stats. Trainer Barboza (18% with 2Off45-180), Saez (14%) up. Recent 77 Beyer was a genuine effort on fast dirt. Two works since including a solid 5F in 1:02. If he repeats that last figure, he's competitive."},
        ]
    },
    {
        "race": 2, "time": "1:20 ET",
        "conditions": "Clm $35,000 | 1 Mile (Turf — Tapeta if off) | 4YO+",
        "scratches": "TBD — check morning of",
        "note": "Turf race — will move to Tapeta 1M70Y if turf unavailable",
        "picks": [
            {"rank": 1, "pp": 6, "name": "MISTER ABARRIO",
             "beyer": "Avg Beyer (last 3): 86.3 | Figures: 88, 85, 86, 83, 90",
             "analysis": "Best and most consistent Beyer average in the field (86.3) — three consecutive figures of 85-88. Has won 6 times in 36 starts, including multiple wins at GP turf. Trainer Joseph Jr (19% overall, 25% claiming) is the class of trainers in this race. Husbands up. Drops from better company and should dominate."},
            {"rank": 2, "pp": 5, "name": "BAKERS STREET",
             "beyer": "Avg Beyer (last 3): 85.3 | Figures: 85, 88, 83",
             "analysis": "Virtually identical figures to Mister Abarrio (85.3 avg) with 85, 88, 83 in last three. Finished 2nd last out (March 18) and has been knocking on the door in this exact class. Trainer Sano consistent, Ortiz Jr (26%) up — elite jockey upgrade. Ran 3rd two back in this exact race condition. The one to beat Mister Abarrio."},
            {"rank": 3, "pp": 7, "name": "RELAMPAGO VERDE",
             "beyer": "Avg Beyer (last 3): 85.3 | Best: 96, 94",
             "analysis": "Best peak figures in the field (96, 94) but recent form has tailed off (82, 80 in last two). Was running in better graded/stakes company before — this is a class drop. Trainer Dibona 22% in 31-60 day spots, Ruiz up. If his sharp recent work (5F in :59.4, bullet 1/13) translates to race form, he fires big."},
        ]
    },
    {
        "race": 3, "time": "1:51 ET",
        "conditions": "Clm $8,000 N3L | 6.5 Furlongs (Dirt) | 3YO+",
        "scratches": "TBD — check morning of",
        "note": "Surface: DIRT",
        "picks": [
            {"rank": 1, "pp": 1, "name": "KING JULIEN",
             "beyer": "Avg Beyer (last 3): 80.0 | Figures: 71, 81, 88, 89, 92",
             "analysis": "Best Beyer average (80.0) and improving trajectory — 71→81→88→89→92 is exceptional. Career-best 92 was just two starts ago. Trainer Dibona 15% overall with a strong record in claiming sprints. Has the highest ceiling and the best form cycle of anyone in this field. Clear top choice."},
            {"rank": 2, "pp": 3, "name": "DOGWOOD CROSSING",
             "beyer": "Avg Beyer (last 3): 80.0 | Figures: 76, 80, 84, 86, 72",
             "analysis": "Tied with King Julien on Beyer average (80.0) with a peak of 86 two starts back. Trainer Tomlinson 21% in routes, more modest in sprints but consistent. Last out dropped to 76 after an 84 — needs to bounce back. At the same figure level, comes down to pace fit and post."},
            {"rank": 3, "pp": 7, "name": "WASAMATTAFOYOU",
             "beyer": "Avg Beyer (last 3): 73.7 | Best: 91",
             "analysis": "Posted an outstanding 91 Beyer three starts back — clearly capable of running a big number. Recent form uneven (62, 68 in last two) but those were route efforts vs. today's 6.5F sprint. Back to his preferred sprint distance. Trainer Infante with Morelos up. If the sprint form returns, he's dangerous."},
        ]
    },
    {
        "race": 4, "time": "2:25 ET",
        "conditions": "AOC $54,000 | 7.5F (Turf — Tapeta 1M70Y alt) | 3YO+",
        "scratches": "TBD — check morning of",
        "note": "Turf race — Tapeta alternative if off turf",
        "picks": [
            {"rank": 1, "pp": 5, "name": "NINA'S LAST GIFT",
             "beyer": "Avg Beyer (last 3): 88.7 | Figures: 86, 87, 93",
             "analysis": "Best Beyer average in the field (88.7) with a peak 93 two starts back. Three consecutive figures of 86 or better — remarkably consistent at this level. Trainer Ubide with a solid record at this level. The 93 was a career-best and she's been knocking on the door for a win. Best figures, best form."},
            {"rank": 2, "pp": 1, "name": "CITY MINUTE",
             "beyer": "Avg Beyer (last 3): 88.3 | Figures: 80, 94, 91",
             "analysis": "Nearly identical average to Nina's Last Gift (88.3) with a peak 94 and back-to-back 91+. Trainer Joseph Jr (19% overall) — the best barn in the field. Has run at this level consistently. The 80 last out is the only recent blemish. Rosario or similar elite jockey expected. Second-best figures, first-rate connections."},
            {"rank": 3, "pp": 7, "name": "SAPPHIRE GIRL",
             "beyer": "Avg Beyer (last 3): 86.3 | Figures: 82, 87, 90",
             "analysis": "Third-best average (86.3) with improving figures (82→87→90) — a horse on the rise. Also trained by Joseph Jr — the barn has two live horses in this race. With elite connections and improving form, she's the third wheel of a competitive trio. Don't overlook."},
        ]
    },
    {
        "race": 5, "time": "2:58 ET",
        "conditions": "Md Sp Wt $84,000 | 1.5 Miles (Dirt) | 3YO+",
        "scratches": "TBD — check morning of",
        "note": "Surface: DIRT | Long route — stamina key",
        "picks": [
            {"rank": 1, "pp": 3, "name": "STOMPIN GRAPES",
             "beyer": "Avg Beyer (last 3): 80.3 | Figures: 78, 81, 82",
             "analysis": "Best Beyer average (80.3) with a perfectly consistent improving line (78→81→82). Trainer Wilkes 22% win rate is excellent, and has shown ability to handle longer routes. No bounce concerns. The most reliable figure horse in the field for a maiden route this long."},
            {"rank": 2, "pp": 7, "name": "THE PULSE",
             "beyer": "Avg Beyer (last 2): 79.0 | Figures: 80, 78",
             "analysis": "Two-start horse with back-to-back figures of 80 and 78 — consistent and competitive. Trainer Joseph Jr (19%) — arguably the best trainer at GP this meet. With only two starts, there's upside improvement to tap. If he improves third time out, wins easily."},
            {"rank": 3, "pp": 1, "name": "MAKE MY DAY",
             "beyer": "Avg Beyer (last 3): 72.7 | Figures: 81, 69, 68",
             "analysis": "Pletcher barn (12% overall) with a peak 81 figure two starts back. Route specialist — has been running in maiden routes consistently. The 81 is competitive for this level. Recent form softer (69, 68) but both at tough tracks. Pletcher always dangerous in maiden routes at this level."},
        ]
    },
    {
        "race": 6, "time": "3:31 ET",
        "conditions": "Alw $54,000 N1X | 6 Furlongs (Dirt) | FL-Bred Fillies 3YO",
        "scratches": "TBD — check morning of",
        "note": "Surface: DIRT | State-bred fillies allowance",
        "picks": [
            {"rank": 1, "pp": 5, "name": "CALYPSO MOON",
             "beyer": "Avg Beyer (last 2): 89.5 | Figures: 88, 91",
             "analysis": "Best figures in the field by a clear margin — 88 and 91 in last two starts. That 91 is near-elite for a 3YO filly allowance sprint at GP. Trainer Plesa consistent at this level, and the figures speak for themselves. Has already won (N1X condition means she can win again today). Class and form say she's the one."},
            {"rank": 2, "pp": 4, "name": "JESTINA",
             "beyer": "Avg Beyer (last 3): 78.0 | Figures: 76, 83, 75",
             "analysis": "Second-best figures (78 avg) with a peak 83 two starts back. Trainer Joseph Jr (19%) — perennial powerhouse. Best she's run was competitive for this class. Should sit second in the Beyer rankings and be the main one to challenge Calypso Moon."},
            {"rank": 3, "pp": 3, "name": "LOVE LIKE LUCY",
             "beyer": "Avg Beyer (last 3): 74.7 | Best: 87",
             "analysis": "Career-best 87 Beyer two starts back shows the ceiling is there. Recent form has dipped (79, 64) — the 64 was clearly an off-day. Trainer Joseph Jr again — barn has two horses here. If she returns to her 87 peak, she's competitive. Joseph Jr placing two fillies in the same race means both are live."},
        ]
    },
    {
        "race": 7, "time": "4:07 ET",
        "conditions": "SOC $35,000 | 1.5 Miles (Tapeta) | 3YO Fillies",
        "scratches": "TBD — check morning of",
        "note": "Surface: TAPETA (fixed surface) | Starter Optional Claiming",
        "picks": [
            {"rank": 1, "pp": 4, "name": "SLEWTY PRINCESS",
             "beyer": "Avg Beyer (last 3): 81.0 | Figures: 80, 86, 77",
             "analysis": "Best Beyer average in the active field (81.0) and has proven Tapeta form. Peak 86 is competitive for this condition. Trainer Coy 20% on synthetic surfaces — solid. Has raced specifically on Tapeta in the past with good results. Most proven horse at the surface and distance combination."},
            {"rank": 2, "pp": 11, "name": "MAGIC COLORS",
             "beyer": "Avg Beyer (last 3): 79.3 | Figures: 78, 90, 70",
             "analysis": "That 90 Beyer middle figure is the best single figure in the field — shows elite ceiling. Form has been inconsistent (90 sandwiched by 78 and 70) but if she hits her peak, she wins. Track record suggests she can fire big on the right day. Price horse worth keying."},
            {"rank": 3, "pp": 1, "name": "SAMARITAN'S JOY",
             "beyer": "Avg Beyer (last 3): 75.0 | Best: 85",
             "analysis": "Career-best 85 two starts back shows the talent is there. Recent form dipped to 64 but bounced back to 76 last out — shows resilience. Trainer Subratie with a modest win rate but knows this horse well. Inside post in a long Tapeta route is an advantage. Third-best figures but gets a good trip."},
        ]
    },
    {
        "race": 8, "time": "4:37 ET",
        "conditions": "Clm $35,000 N2L | 5 Furlongs (Turf — Tapeta 5F alt) | 3YO+",
        "scratches": "TBD — check morning of",
        "note": "Turf sprint — if off moves to Tapeta 5F",
        "picks": [
            {"rank": 1, "pp": 5, "name": "BLACKFOOT DAISY",
             "beyer": "Avg Beyer (last 3): 88.0 | Figures: 80, 86, 98",
             "analysis": "That 98 Beyer last out is the best figure in the field — elite for a $35K claiming sprint. Huge jump from her prior figures (80, 86) suggests she's at the top of her game right now. Trainer Ward (Wesley) has excellent stats with turf sprinters. She's the class of this field on the most recent performance."},
            {"rank": 2, "pp": 1, "name": "BRITTANY'S WAY",
             "beyer": "Avg Beyer (last 3): 87.0 | Figures: 91, 87, 83",
             "analysis": "Most consistent horse in the field — three consecutive figures of 83 or better (91-87-83). That 91 two starts back is the second-best figure here. Trainer Owens and the inside post in a short turf sprint are both positives. If Blackfoot Daisy is off her peak, Brittany's Way is the alternative."},
            {"rank": 3, "pp": 3, "name": "MIDSUMMER MO",
             "beyer": "Avg Beyer (last 3): 87.0 | Figures: 85, 95, 81",
             "analysis": "That 95 Beyer two starts back is the highest figure among all horses in this race. Peak figure horse — if she recaptures that form she wins by daylight. Mark Casse barn (16%) with consistent high-end form. The 81 last out was a step back but the 95 shows what she's capable of on her day."},
        ]
    },
    {
        "race": 9, "time": "5:08 ET",
        "conditions": "SOC $35,000 | 5.5 Furlongs (Tapeta) | 3YO",
        "scratches": "TBD — check morning of",
        "note": "Surface: TAPETA (fixed) | Starter Optional Claiming",
        "picks": [
            {"rank": 1, "pp": 8, "name": "WIN N JUICE",
             "beyer": "Avg Beyer (last 3): 83.3 | Figures: 80, 84, 86",
             "analysis": "Best Beyer average (83.3) AND improving trajectory (80→84→86) — the ideal combination. Has been consistently competitive at this level with no give-up efforts. Trainer Ramsey with a solid record on synthetic, the figures support a win. Best form in the field right now."},
            {"rank": 2, "pp": 7, "name": "COPERNIUM",
             "beyer": "Avg Beyer (last 3): 73.0 | Best: 89",
             "analysis": "That 89 Beyer shows elite potential but the 51 in between is a major concern. Trainer David 20% overall (excellent) and has worked the horse back into form. If the 89 was the real him and the 51 was an anomaly, he fires today. Price horse — the upside is significant if the form holds."},
            {"rank": 3, "pp": 8, "name": "NOT NOW NICK",
             "beyer": "Avg Beyer (last 3): 77.7 | Figures: 77, 84, 72",
             "analysis": "Mid-70s to low-80s range — reliable and competitive at this level. Trainer Hurtak consistent in sprint spots, 84 peak shows he can run a useful figure. Won't win unless the top two underperform but is a solid contender for the place slots. Consistent presence in these sprints."},
        ]
    },
    {
        "race": 10, "time": "5:40 ET",
        "conditions": "Clm $35,000 N2L | 1.5 Miles (Turf — Tapeta alt) | F&M 3YO+",
        "scratches": "TBD — check morning of",
        "note": "Turf route — Tapeta 1M70Y alt if off turf",
        "picks": [
            {"rank": 1, "pp": 7, "name": "LOTUS PETAL",
             "beyer": "Avg Beyer (last 3): 88.0 | Figures: 78, 92, 94",
             "analysis": "Best Beyer average in the field (88.0) and an improving rocket — 78→92→94 over three starts. That back-to-back 92-94 is elite for a $35K N2L claimer. Trainer Antonucci with a solid record, and Lotus Petal has been firing at the highest level. She's the class of this field right now."},
            {"rank": 2, "pp": 9, "name": "WILL REIGN",
             "beyer": "Avg Beyer (last 3): 84.3 | Figures: 90, 72, 91",
             "analysis": "Two figures of 90+ with a soft 72 sandwiched in between. Mark Casse barn (16%) — blue-chip connections. The 90 and 91 say she's capable of running with the top horses in this field. The 72 is dismissed as an anomaly. If she fires to her peak form, she challenges Lotus Petal all the way."},
            {"rank": 3, "pp": 4, "name": "PRACTICALLY FAMOUS",
             "beyer": "Avg Beyer (last 3): 85.0 | Figures: 87, 85, 83",
             "analysis": "Most consistent horse in the field — three straight figures of 83-87, no bad days. Trainer Alter with a smaller string but this horse is very reliable. The 87 peak is competitive, and consistency beats a horse like Will Reign who goes up and down. Safe play for the place/show."},
        ]
    },
]

def build_pdf():
    doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=letter,
        rightMargin=0.5*inch, leftMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()

    title_sty = ParagraphStyle('T', parent=styles['Normal'],
        fontSize=18, fontName='Helvetica-Bold', alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    sub_sty = ParagraphStyle('S', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica', alignment=TA_CENTER,
        textColor=colors.HexColor('#e94560'), spaceAfter=10)
    cond_sty = ParagraphStyle('C', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#555555'), spaceAfter=1)
    scratch_sty = ParagraphStyle('Sc', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#cc0000'), spaceAfter=4)
    race_hdr_sty = ParagraphStyle('RH', parent=styles['Normal'],
        fontSize=13, fontName='Helvetica-Bold',
        textColor=colors.white, spaceAfter=2)
    name_sty = ParagraphStyle('N', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=1)
    beyer_sty = ParagraphStyle('B', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-BoldOblique',
        textColor=colors.HexColor('#0055aa'), spaceAfter=2)
    note_sty = ParagraphStyle('An', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#333333'), spaceAfter=4, leading=12)
    footer_sty = ParagraphStyle('F', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica-Oblique', alignment=TA_CENTER,
        textColor=colors.grey)

    rank_labels = {1: "1st PICK", 2: "2nd PICK", 3: "3rd PICK"}
    rank_colors_map = {
        1: colors.HexColor('#c8a415'),
        2: colors.HexColor('#9e9e9e'),
        3: colors.HexColor('#cd7f32'),
    }

    story = []
    story.append(Paragraph("🏇 GULFSTREAM PARK — TOP 3 PICKS", title_sty))
    story.append(Paragraph("Friday, March 20, 2026", sub_sty))

    for race in PICKS:
        # Race header bar
        hdr = Table([[Paragraph(f"RACE {race['race']}  ·  {race['time']}", race_hdr_sty)]],
            colWidths=[7.5*inch])
        hdr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(hdr)
        story.append(Spacer(1, 3))
        story.append(Paragraph(race['conditions'], cond_sty))
        if race.get('note'):
            story.append(Paragraph(race['note'], ParagraphStyle('nt', parent=styles['Normal'],
                fontSize=8, fontName='Helvetica-Oblique',
                textColor=colors.HexColor('#cc6600'), spaceAfter=2)))
        story.append(Paragraph(f"Scratches: {race['scratches']}", scratch_sty))

        for pick in race['picks']:
            pp = pick['pp']
            bg = PP_COLORS.get(pp, colors.grey)
            tc = PP_TEXT.get(pp, colors.white)

            pp_cell = Paragraph(f"<b>#{pp}</b>", ParagraphStyle('pp',
                parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold',
                textColor=tc, alignment=TA_CENTER))
            rank_cell = Paragraph(f"<b>{rank_labels[pick['rank']]}</b>",
                ParagraphStyle('rk', parent=styles['Normal'], fontSize=9,
                fontName='Helvetica-Bold',
                textColor=rank_colors_map[pick['rank']], alignment=TA_CENTER))

            content = Table([
                [Paragraph(f"<b>{pick['name']}</b>", name_sty)],
                [Paragraph(pick['beyer'], beyer_sty)],
                [Paragraph(pick['analysis'], note_sty)],
            ], colWidths=[6.4*inch])
            content.setStyle(TableStyle([
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
            ]))

            row = Table([[pp_cell, rank_cell, content]],
                colWidths=[0.5*inch, 0.65*inch, 6.35*inch])
            row.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), bg),
                ('BACKGROUND', (1,0), (1,0), colors.HexColor('#f5f5f5')),
                ('BACKGROUND', (2,0), (2,0), colors.HexColor('#fafafa')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (0,0), 4),
                ('LEFTPADDING', (2,0), (2,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
            ]))
            story.append(row)
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        story.append(Spacer(1, 5))

    story.append(Paragraph(
        "Generated by Charlie · Gulfstream Park · March 20, 2026 · In Beyers We Trust 🐴 · Scratches TBD morning of",
        footer_sty))

    doc.build(story)
    print(f"✅ PDF created: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf()
