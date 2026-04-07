#!/usr/bin/env python3
"""GP Picks PDF - March 19, 2026 - ALL TURF OFF → TAPETA"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

OUTPUT_PATH = "/home/damato/.openclaw/workspace/GP-Picks-Mar19-2026.pdf"

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_badge_style, pp_text_hex, pp_border_color
PICKS_DATA = [
    {
        "race": 1, "time": "12:50 ET",
        "conditions": "Md Clm $35,000 | 1 Mile (Tapeta) | 3YO Fillies",
        "scratches": "#9 Blazing Bridgette",
        "picks": [
            {"rank": 1, "pp": 3, "name": "DEL MAR SUNRISE",
             "beyer": "Avg Beyer (last 3): 66.0 | Best turf: 82, 74",
             "note": "Twice claimed upward — connections believe in her. Blinkers added today for the first time, Irad Ortiz Jr (26% win rate) takes the mount. Trainer Tomlinson hits 27% on turf and 25% with maiden claimers. Two consecutive improving Tapeta route efforts (82→74) at this exact trip. Best angle in the race."},
            {"rank": 2, "pp": 2, "name": "TOO LOOSE LA TREK",
             "beyer": "Avg Beyer (last 3): 75.7",
             "note": "Best pure Beyer average in the field (75.7) with three straight route efforts at this distance and surface — all in better company (Moc $50K). Drops to MCL $35K today for class relief. Trainer Trombetta 19% on turf routes. Should sit just off pace and fire."},
            {"rank": 3, "pp": 4, "name": "KINDA CLEVER",
             "beyer": "Avg Beyer (last 3): 69.7 | Best turf: 84",
             "note": "Posted the best single turf Beyer in the field (84) and a solid 70 on yielding ground. Long layoff concern — Matz is 0% in 61-180 day spots — but works have been regular and Rosario is aboard. If she fires fresh, her ceiling is the highest in the race."},
        ]
    },
    {
        "race": 2, "time": "1:21 ET",
        "conditions": "Md Clm $12,500 | 1M 70Y (Tapeta) | 3YO+",
        "scratches": "#2 Magnus Gold, #5 Kukuk",
        "picks": [
            {"rank": 1, "pp": 6, "name": "LOMAX",
             "beyer": "Avg Beyer (last 3): 59.3",
             "note": "Blinkers added today with trainer Carlos David (25% win rate, 26% with synthetic/blinkers) and Irad Ortiz Jr in the irons — a dangerous combination at this level. Steadily improving before layoff, finished 3rd last out at this exact spot. With Tapstick and Live to Ride dueling up front, Lomax has the ideal setup to close."},
            {"rank": 2, "pp": 1, "name": "TAPSTICK",
             "beyer": "Avg Beyer (last 3): 75.7",
             "note": "Best Beyer average in the active field (75.7), has run 9 times in this exact race type/surface/distance. The class of the field on figures — consistently 2nd and 3rd, just can't break through. Panici back on board. Hard to beat if the closers don't fire."},
            {"rank": 3, "pp": 4, "name": "LIVE TO RIDE",
             "beyer": "Avg Beyer (last 3): 75.3",
             "note": "Matched Tapstick on figures and was DQ'd from a win previously. Long layoff since September and last work (5F in 1:04.1) wasn't sharp — fitness is the question. New trainer Castro at 17% synthetic. If sharp off the bench, the figures say he belongs."},
        ]
    },
    {
        "race": 3, "time": "1:52 ET",
        "conditions": "Clm $8,000 N3L | 5 Furlongs (Tapeta) | 3YO+",
        "scratches": "#5 My Anticipation",
        "picks": [
            {"rank": 1, "pp": 3, "name": "HONOR HER",
             "beyer": "Avg Beyer (last 3): 90.0 | Figures: 92, 89, 89",
             "note": "Won last out March 8 with a career-best 92 Beyer — best figure by far in this field. Three consecutive efforts of 89 or better (92-89-89), all on fast Tapeta at GP. Trainer Hurtak 18% with winners off wins, Vasquez back on board. Clear class of the field."},
            {"rank": 2, "pp": 6, "name": "I LOVE TO WIN",
             "beyer": "Avg Beyer (last 3): 82.0 | Figures: 82, 77, 87",
             "note": "Solid mid-80s Beyer range with consistent Tapeta sprint performances. Second-best Beyer average in the active field. Has run in this exact condition type and shown willingness to compete. Best chance at the place spots behind Honor Her."},
            {"rank": 3, "pp": 2, "name": "STUBOLD",
             "beyer": "Avg Beyer (last 3): 77.7 | Best: 91",
             "note": "Won in December with a strong 91 Beyer showing the ceiling is there. Recent form softer (82, 60) but has the profile of a horse that can bounce back. Trainer Coy 21% on Tapeta. Inside post and Gonzalez up — if back to his Dec form, runs a big race."},
        ]
    },
    {
        "race": 4, "time": "2:23 ET",
        "conditions": "Md Clm $12,500 | 5 Furlongs (Tapeta) | 3YO+ Fillies/Mares",
        "scratches": "#7 Soda",
        "picks": [
            {"rank": 1, "pp": 3, "name": "MORE THAN A SHADOW",
             "beyer": "Avg Beyer (last 2): 84.0 | Figures: 85, 83",
             "note": "Best back-to-back Beyer figures in the field (85, 83) — consistently the highest-rated horse here. Has shown she can sustain her effort through the lane on Tapeta. Off a rest since Feb 5 with solid PmM works. Morelos up, trainer Gonzalez 12% on routes."},
            {"rank": 2, "pp": 1, "name": "CUDDLE THE KITTEN",
             "beyer": "1 start: 79 Beyer",
             "note": "Blinkers REMOVED today — equipment changes like this often signal improvement. Alter barn hits 25% on Sprint/Route transitions and 29% as second starters. Sharp GP works including 5F in 1:01.3 and 4F in :48.4. Inside post in a sprint is a plus. Respect as a much-improved second-timer."},
            {"rank": 3, "pp": 4, "name": "CODED ELEGANCE",
             "beyer": "Avg Beyer (last 2): 60.0 | Figures: 56, 64",
             "note": "Modest figures but closed from off the pace last out (5p turn, closed outside) showing tactical improvement. Barboza barn 18% overall, Ruiz up. May benefit from a pace duel up front. At the bottom of the form column but worth a spot at these odds."},
        ]
    },
    {
        "race": 5, "time": "2:54 ET",
        "conditions": "Md Clm $35,000 | 1 Mile (Tapeta) | 3YO Fillies",
        "scratches": "#7 Shrug",
        "picks": [
            {"rank": 1, "pp": 3, "name": "IRISH GENT",
             "beyer": "Avg Beyer (last 3): 87.0 | Figures: 89, 87, 85",
             "note": "Best Beyer average (87.0) with three consecutive figures in the 85-89 range — improving trajectory and consistent quality. Trainer Saffie Joseph Jr (20% wins overall) with Castellano up (15%). Has been running against similar and better company; today's spot looks right. Joseph barn excels at placing horses to win."},
            {"rank": 2, "pp": 8, "name": "PATRICK'S PROMISE",
             "beyer": "Avg Beyer (last 3): 85.3 | Figures: 88, 87, 85",
             "note": "Also from the Joseph barn — same trainer, similar figures (85-88 range). Has been consistently competitive at this level. Gonzalez up as a capable pilot. With two horses from the same barn in this field, the barn clearly likes both — but Irish Gent has the slight edge on trajectory."},
            {"rank": 3, "pp": 4, "name": "KULAPAT",
             "beyer": "Avg Beyer (last 3): 87.0 | Figures: 89, 87, 85",
             "note": "Mark Casse barn (16% wins) with Vasquez up. Figures match Irish Gent almost exactly (89-87-85). Has been running in this same group of horses repeatedly — knows the competition well. Casse is always dangerous when he spots a horse at the right level."},
        ]
    },
    {
        "race": 6, "time": "3:25 ET",
        "conditions": "Md Clm $25,000 | 5 Furlongs (Tapeta) | 3YO+ Fillies",
        "scratches": "#4 Philadelphia Roll",
        "picks": [
            {"rank": 1, "pp": 5, "name": "HIDDEN AGENDA",
             "beyer": "Avg Beyer (last 3): 83.3 | Figures: 86, 80, 84",
             "note": "Best Beyer average in the active field (83.3) with three figures all 80 or better. Two sharp bullet works at :47 flat in January — pure speed. Trainer Coy 20% on Tapeta sprints, Castellano up at 15% wins. Has been running in better company — this spot looks ideal for a breakthrough win."},
            {"rank": 2, "pp": 3, "name": "JUST SILVIA",
             "beyer": "Avg Beyer (last 3): 80.0 | Figures: 86, 70, 84",
             "note": "Posted an 86 Beyer last out (Feb 22) finishing second — career-best figure showing marked improvement. Trainer Sweezey 19% on synthetic, 17% on maiden claiming. Makes the move to GP from PmM which can be a positive angle. If she repeats her last-out figure, she's right there."},
            {"rank": 3, "pp": 2, "name": "GHOSTLIGHT",
             "beyer": "Avg Beyer (last 2): 79.0 | Figures: 84, 74",
             "note": "Showed an 84 Beyer finishing 2nd at Turfway — legitimate figures for this level. Trainer Summers 31% with maiden claimers, Gaffalione (16%) takes over. Long layoff since December but has been working consistently at Belmont training track. If the form is there off the long break, has the talent."},
        ]
    },
    {
        "race": 7, "time": "3:55 ET",
        "conditions": "OC $20,000 N1X | 5 Furlongs (Tapeta) | 3YO+ Fillies/Mares",
        "scratches": "None",
        "picks": [
            {"rank": 1, "pp": 4, "name": "HAPPY RIDE",
             "beyer": "Avg Beyer (last 3): 86.7 | Figures: 87, 85, 88",
             "note": "Most consistent recent form in the field — three straight figures in the 85-88 range with no give-up efforts. Feb 14 hit an 87 fighting on in a pace duel, Dec 11 peaked at 88. No layoff concerns, no fitness questions. Trainer Orseno solid, Zayas (15%) takes the mount. Most reliable horse on paper."},
            {"rank": 2, "pp": 6, "name": "MYWIFEKNOWSITALL",
             "beyer": "Avg Beyer (last 3): 89.3 | Figures: 85, 93, 90",
             "note": "Best raw figures in the field — 93 and 90 in June/July are top-class for this spot. The long layoff since July 27 is the only concern; no recent works visible. Trainer Jackson has limited GP stats. If she fires fresh off the extended break, she wins easily — ability is not in question, only fitness."},
            {"rank": 3, "pp": 5, "name": "VAYESTA",
             "beyer": "Avg Beyer (last 3): 80.7 | Best sprint: 91, 90, 84",
             "note": "Sprint figures of 91 and 90 (Oct and Nov) are excellent — the two route efforts since were disappointing (80, 72) suggesting she's strictly a sprinter. Back to 5F today which is her distance. Simpson barn with Nicholls up. If the sprint form is there, she's dangerous at a price."},
        ]
    },
    {
        "race": 8, "time": "4:26 ET",
        "conditions": "Md Sp Wt $84,000 | 5 Furlongs (Tapeta) | 3YO+ Fillies/Mares",
        "scratches": "None",
        "picks": [
            {"rank": 1, "pp": 5, "name": "BURNING BRIDGES",
             "beyer": "Last start: 90 Beyer | Debut: 2nd place",
             "note": "Ran an impressive 90 Beyer finishing 2nd in her debut Feb 15, leading on the rail before just getting caught late. Mark Casse barn (16% wins, 16% with second starters) — one of the best operations in North America. Zayas (15%) stays on from the debut. Figures to be sharper second time out; best equipped to win."},
            {"rank": 2, "pp": 6, "name": "JUBILEE PARADE",
             "beyer": "Last start: 89 Beyer | 2 starts: 89, 82",
             "note": "Ran an 89 Beyer finishing 3rd in her debut on Feb 15 — the same race as Burning Bridges. Shows she belongs in this class. William Mott barn (22% wins) is blue-chip, Alvarado (16%) up. Has a route start at Belmont on turf that shows tactical versatility. Second race improvement angle is strong."},
            {"rank": 3, "pp": 7, "name": "MR. TRAVELIN' MAN",
             "beyer": "Last start: 87 Beyer",
             "note": "One start showing an 87 Beyer finishing 3rd on Nov 30 — solid figures for a first-time Tapeta effort. Trainer Barboza 21% on Tapeta sprints with second starters, Gaffalione (16%) up. Long absence since November but works suggest fitness is there. Layoff runners from the Barboza barn often bounce back sharp."},
        ]
    },
    {
        "race": 9, "time": "4:57 ET",
        "conditions": "OC $35,000 / SAL $12,000 N | 1 Mile (Tapeta) | 3YO+ Fillies/Mares",
        "scratches": "None",
        "picks": [
            {"rank": 1, "pp": 7, "name": "TURKISH PISTACHIO",
             "beyer": "Avg Beyer (last 3): 82.7 | Figures: 77, 89, 82",
             "note": "Won impressively Jan 29 with an 89 Beyer leading gate-to-wire at GP — best single figure in the field. Tapeta-proven winner at this distance. Off a slightly disappointing 77 at Tampa March 1 (outside trip, 4p, tired) — excusable on turf vs. her preferred Tapeta. Trainer David 25% overall, Vasquez up. Class and form say she's the one."},
            {"rank": 2, "pp": 4, "name": "MO HIJINX",
             "beyer": "Avg Beyer (last 3): 82.0 | Figures: 82, 77, 87",
             "note": "Won most recently March 5 on turf at GP with an 85 Beyer — confirmed she can handle route distances. Prior efforts show 87, 82, 77 range. Trainer Margotta 22% overall (impressive), Irad Ortiz Jr (26%) takes the mount — elite combination. Turf win translates well to Tapeta."},
            {"rank": 3, "pp": 2, "name": "BETTER WITH VINO",
             "beyer": "Avg Beyer (last 3): 83.0 | Figures: 85, 83, 81",
             "note": "Three consecutive figures in the 81-85 range — consistent and competitive at this level. Won on Jan 10 (81 Beyer) and has since run 83 and 85 in optional claimers — improving trajectory. Trainer Tomlinson 21% with routes, Alvarado (16%) up. Has never missed the board in 5 career starts. Reliable play for the exacta."},
        ]
    },
    {
        "race": 10, "time": "5:25 ET",
        "conditions": "Md Sp Wt $84,000 | 5 Furlongs (Tapeta) | 3YO+ Fillies",
        "scratches": "#1 Ez Connect, #10 Full Card",
        "picks": [
            {"rank": 1, "pp": 9, "name": "PEARL OF PEARL",
             "beyer": "Last 2 starts: 89, 87 Beyer",
             "note": "Two starts showing back-to-back figures of 89 and 87 — best Beyer credentials in the field. Ran 2nd on debut (Jan 16) with an 89 Beyer getting bumped at the start, then showed 87 in her second start on turf. Trainer D'Angelo hits 17% on turf sprints, 20% on maiden sprint/routes. Irad Ortiz Jr (26%) up — elite jockey switch. Clear top choice on figures."},
            {"rank": 2, "pp": 3, "name": "IGNIS COR",
             "beyer": "Multiple starts with consistent figures",
             "note": "Brian Lynch barn (30% win rate overall!) — one of the highest-percentage trainers in the game. Lynch 21% on turf routes and 24% on maiden claiming at this level. Perez up. Lynch wins at a rate that demands respect even without premium figures. Class of connections in a first-time starter-heavy field."},
            {"rank": 3, "pp": 7, "name": "DELIGHTFUL DARLING",
             "beyer": "Last starts: 87, 88 Beyer",
             "note": "Has shown 87-88 Beyer figures in recent turf route efforts — solid credentials for this spot. Trainer Dobles 29% in 61-180 day spots, Vasquez (12%) up. Has been running in similar company and knows how to compete. Makes the surface switch to Tapeta today but the figures suggest she handles all-weather well."},
        ]
    },
]

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Normal'],
        fontSize=18, fontName='Helvetica-Bold', alignment=TA_CENTER,
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)

    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica', alignment=TA_CENTER,
        textColor=colors.HexColor('#e94560'), spaceAfter=2)

    notice_style = ParagraphStyle('Notice', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica-BoldOblique', alignment=TA_CENTER,
        textColor=colors.HexColor('#cc0000'), spaceAfter=12)

    race_header_style = ParagraphStyle('RaceHeader', parent=styles['Normal'],
        fontSize=13, fontName='Helvetica-Bold',
        textColor=colors.white, spaceAfter=2)

    conditions_style = ParagraphStyle('Conditions', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#555555'), spaceAfter=2)

    scratch_style = ParagraphStyle('Scratch', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#cc0000'), spaceAfter=6)

    pick_name_style = ParagraphStyle('PickName', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=1)

    beyer_style = ParagraphStyle('Beyer', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-BoldOblique',
        textColor=colors.HexColor('#0055aa'), spaceAfter=2)

    note_style = ParagraphStyle('Note', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#333333'), spaceAfter=6, leading=12)

    story = []

    # Header
    story.append(Paragraph("🏇 GULFSTREAM PARK — TOP 3 PICKS", title_style))
    story.append(Paragraph("Thursday, March 19, 2026", subtitle_style))
    story.append(Paragraph("⚠️ ALL TURF RACES MOVED TO TAPETA TODAY", notice_style))

    for race in PICKS_DATA:
        # Race header bar
        race_label = f"RACE {race['race']}  ·  {race['time']}"
        header_table = Table(
            [[Paragraph(race_label, race_header_style)]],
            colWidths=[7.5*inch]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 3))
        story.append(Paragraph(race['conditions'], conditions_style))
        story.append(Paragraph(f"Scratches: {race['scratches']}", scratch_style))

        rank_labels = {1: "1st PICK", 2: "2nd PICK", 3: "3rd PICK"}
        rank_colors = {
            1: colors.HexColor('#c8a415'),
            2: colors.HexColor('#9e9e9e'),
            3: colors.HexColor('#cd7f32'),
        }

        for pick in race['picks']:
            pp = pick['pp']
            bg_color = PP_COLORS.get(pp, colors.grey)
            txt_color = PP_TEXT_COLORS.get(pp, colors.white)

            pp_cell = Paragraph(f"<b>#{pp}</b>", ParagraphStyle('pp',
                parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold',
                textColor=txt_color, alignment=TA_CENTER))

            rank_cell = Paragraph(f"<b>{rank_labels[pick['rank']]}</b>", ParagraphStyle('rank',
                parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold',
                textColor=rank_colors[pick['rank']], alignment=TA_CENTER))

            name_para = Paragraph(f"<b>{pick['name']}</b>", pick_name_style)
            beyer_para = Paragraph(pick['beyer'], beyer_style)
            note_para = Paragraph(pick['note'], note_style)

            pick_content = Table(
                [[name_para], [beyer_para], [note_para]],
                colWidths=[6.5*inch]
            )
            pick_content.setStyle(TableStyle([
                ('TOPPADDING', (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
            ]))

            row_table = Table(
                [[pp_cell, rank_cell, pick_content]],
                colWidths=[0.5*inch, 0.65*inch, 6.35*inch]
            )
            row_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), bg_color),
                ('BACKGROUND', (1,0), (1,0), colors.HexColor('#f5f5f5')),
                ('BACKGROUND', (2,0), (2,0), colors.HexColor('#fafafa')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (0,0), 4),
                ('LEFTPADDING', (2,0), (2,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
            ]))
            story.append(row_table)
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        story.append(Spacer(1, 6))

    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica-Oblique', alignment=TA_CENTER,
        textColor=colors.grey)
    story.append(Paragraph("Generated by Charlie · Gulfstream Park · March 19, 2026 · In Beyers We Trust 🐴", footer_style))

    doc.build(story)
    print(f"PDF created: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf()
