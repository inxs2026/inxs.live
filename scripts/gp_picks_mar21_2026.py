#!/usr/bin/env python3
"""
Gulfstream Park Picks – March 21, 2026
Charlie's Top-3 Picks methodology
All turf races are OFF THE TURF (running on Tapeta)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import datetime

# ── Post-position colours ──────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_badge_style, pp_text_hex, pp_border_color
# ── RACE DATA ──────────────────────────────────────────────────────────────
RACES = [
    {
        "num": 1, "post": "12:50 ET",
        "cond": "Maiden Special Weight $84k | 3YO Fillies | 1M 70Y TAPETA (off turf)",
        "note": "⚠️ Originally 7.5f Turf – moved to Tapeta. Scratched: #5 Friendship Sloop, #8 Aporia, #12 Voluntary",
        "par": 77,
        "picks": [
            {"pp": 3, "name": "PAN PAN",
             "beyer": "73-69-63 | Avg: 68.3",
             "trainer": "Joseph Jr (19% W)",
             "jockey": "Husbands M J",
             "comment": "Best Beyers in field, has two turf starts at GP including a 73. Pressed pace, showed versatility. Joseph Jr 19% at GP is strong. Synthetic/Tapeta unknown but most qualified."},
            {"pp": 7, "name": "TAP THIS WAY",
             "beyer": "First starter | Works: 5f 1:00.3",
             "trainer": "Casse (16% W) | 1stStart 16%",
             "jockey": "Castellano J J",
             "comment": "Power first-starter connections — Casse 16% debut, Castellano. Multiple sharp works at GP including bullet 5f. Race moving to Tapeta suits an unknown. Don't dismiss."},
            {"pp": 10, "name": "SHOT AT PERFECTION",
             "beyer": "65-67-44 | Avg: 58.7",
             "trainer": "Wilkes Ian (15% W)",
             "jockey": "Herrera D A",
             "comment": "Has four dirt starts prior to turf experiment — most Tapeta-ready of experienced horses. 65 Beyer on turf recently shows ability. Class and experience edge over maidens."},
        ]
    },
    {
        "num": 2, "post": "1:20 ET",
        "cond": "Maiden Claiming $12,500 | 3yo+ | 5f Tapeta",
        "note": "Scratched: #7 Freedom Street",
        "par": 64,
        "picks": [
            {"pp": 5, "name": "VELOCIRAPTOR",
             "beyer": "61-54-64 | Avg: 59.7",
             "trainer": "Casse (16% W)",
             "jockey": "Castellano J J",
             "comment": "Best Beyers by a wide margin (avg 59.7 vs field avg ~47). 5yo who has shown 74 in past. All dirt wins; drops from much higher company to $12,500. Casse/Castellano confident with the claim. Class makes this one."},
            {"pp": 4, "name": "ONE MORE DUKE",
             "beyer": "53-53-45 | Avg: 50.3",
             "trainer": "Yates Michael (10% W)",
             "jockey": "Vasquez M A",
             "comment": "Most Tapeta experience in field (4 starts on GP synthetic), knows the surface. Hit the board at this level multiple times including a 3rd. Consistent enough to hit."},
            {"pp": 2, "name": "BROKEN SOUND",
             "beyer": "52-44-42 | Avg: 46",
             "trainer": "Barboza V Jr (18% W)",
             "jockey": "Morelos J E",
             "comment": "4yo colt, 2nd in debut (44 Beyer). Only 3 starts, best was 52 on turf. Barboza 18% win is solid. Has shown front-running speed and could improve."},
        ]
    },
    {
        "num": 3, "post": "1:51 ET",
        "cond": "Claiming $6,250 | 4yo+ | 1M Dirt",
        "note": "Scratched: #4 Mr Scatter",
        "par": 73,
        "picks": [
            {"pp": 7, "name": "TUT'S REVENGE",
             "beyer": "76-74-79(turf) | Recent: 76",
             "trainer": "De La Cerda (11% W) | 1stClaim",
             "jockey": "Ruiz J",
             "comment": "10yo former G3 winner just won at $6,250 in the slop (76 Beyer). Massive class drop from OC 25k-75k level. Won last out — trainer claiming him shows confidence. Ruiz aboard. Clear standout."},
            {"pp": 3, "name": "BRODERICK",
             "beyer": "70-62-67 | Avg: 66.3",
             "trainer": "Reynolds P (17% W) | WonLastStart",
             "jockey": "Henry W",
             "comment": "Won last out at Clm 8000, now dropping to 6250. That's a positive class drop after a win. Pace horse (Early 106). 3 wins at GP this meet. Hot form."},
            {"pp": 1, "name": "BROTHER BRAD",
             "beyer": "72-76-69 | Avg: 72.3",
             "trainer": "Coy Ronald (9% W)",
             "jockey": "Morelos J E",
             "comment": "9yo veteran who finished 2nd last out vs Tut's Revenge. Best avg Beyer in field (72.3). Consistent at 6250 level, knows how to hit the board. Should be in the mix."},
        ]
    },
    {
        "num": 4, "post": "2:22 ET",
        "cond": "Claiming $8,000 N2L | 3yo+ | 1M 70Y Tapeta",
        "note": "Scratched: #6 So So, #7 Saratoga Cruiser",
        "par": 70,
        "picks": [
            {"pp": 5, "name": "LIAM'S SONG",
             "beyer": "74-63 | Avg: 68.5",
             "trainer": "Luces Eduardo | 1stW/Trn 40%(!)",
             "jockey": "Gonzalez E",
             "comment": "Won Feb 15 at $17,500 maiden level, now in N2L at $8,000 — significant class drop. 74 Beyer in that win. New trainer angle with 40% first-time win stat (!). Gonzalez riding. Should dominate this field."},
            {"pp": 1, "name": "HEAVEN'S CHAMPION",
             "beyer": "67-42-62 | Avg: 57",
             "trainer": "Chapman B J (14% W)",
             "jockey": "Vasquez M A",
             "comment": "2nd last out at this level (67 Beyer), caught late. Bobbled start that day so had excuses. Chapman 14% and Vasquez make this formful. Has Tapeta experience."},
            {"pp": 9, "name": "ESPERANZITO",
             "beyer": "61-51-47 | Avg: 53",
             "trainer": "Perez C L (5% W)",
             "jockey": "Karamanos H A",
             "comment": "3rd last out at 12.5k level (61 Beyer), consistent closer. Multiple Tapeta starts at GP. Improving trajectory (47-51-61). Could sneak into the ticket."},
        ]
    },
    {
        "num": 5, "post": "2:52 ET",
        "cond": "Maiden Claiming $35,000 | 3YO Fillies | 6.5f Dirt",
        "note": "No scratches confirmed",
        "par": 0,
        "picks": [
            {"pp": 3, "name": "SWEET DREAM LADY",
             "beyer": "57-57-57 | Avg: 57",
             "trainer": "Yates Michael (10% W) | 2Off45-180: 19%",
             "jockey": "Vasquez M A",
             "comment": "Most experienced horse, three consecutive 57 Beyers showing remarkable consistency. 2nd and 3rd in last two sprints, always competing. Yates 19% after layoff stat is key. ML favorite with reason."},
            {"pp": 7, "name": "SPOTTED",
             "beyer": "First starter | Multiple sharp works",
             "trainer": "Robson Lauren (38% W — ELITE)",
             "jockey": "Maragh R",
             "comment": "Robson's 38% win rate for first starters is exceptional. Works include bullets and consistent drills. Known Agenda filly, Spendthrift-bred. At 7-2, worth the risk given trainer stats."},
            {"pp": 3, "name": "MY GIRL NINA",
             "beyer": "59-59-45 | Avg: 54.3",
             "trainer": "Klesaris Steve (19% W with Dirt)",
             "jockey": "Davis D",
             "comment": "Has finished 3rd in three straight sprints — consistently competitive. Klesaris 19% on dirt and 19% 31-60 days. Should be right there again."},
        ]
    },
    {
        "num": 6, "post": "3:22 ET",
        "cond": "Maiden Claiming $17,500 | 3yo+ | 1M 1/16 TAPETA (off turf)",
        "note": "⚠️ Originally 1.5M Turf – moved to Tapeta. Scratched: #2 Numinous, #6 Smooth an Easy, #9 Marc Kentucky",
        "par": 70,
        "picks": [
            {"pp": 5, "name": "GLOBECREST",
             "beyer": "69-68-65 | Avg: 67.3 (on WO synthetic)",
             "trainer": "Casse Mark (16% W) | MSWtoMCL: 27%",
             "jockey": "Davis D",
             "comment": "Best Beyers in field (67.3 avg) — all earned on synthetic surfaces at Woodbine. Race moving to Tapeta plays RIGHT into his strengths. Casse 27% MSW-to-MCL stat is huge. First GP start but surface fits."},
            {"pp": 1, "name": "SEAWISE",
             "beyer": "65-65-67 | Avg: 65.7",
             "trainer": "Kelly Blake (15% W) | 31-60Days: 25%",
             "jockey": "Maragh R",
             "comment": "Consistent 65-67 Beyers on turf, 3 times 2nd at this class. Kelly 25% with 31-60 day angle. Moving to Tapeta is unknown but has shown class. Should be competitive off turf shift."},
            {"pp": 4, "name": "ASTIN STYLE",
             "beyer": "66-63-62 | Avg: 63.7",
             "trainer": "Tharrenos William (12% W) | MdnClm: 28%",
             "jockey": "Gonzalez E",
             "comment": "Has 4 GP Tapeta starts (0-1-2), KNOWS this surface better than anyone else in the race. 63.7 avg is solid. Tharrenos MdnClm 28% is excellent. Tapeta familiarity is a significant edge."},
        ]
    },
    {
        "num": 7, "post": "3:52 ET",
        "cond": "Allowance Optional Claiming $125k N2X | 4yo+ | 1.5M Dirt",
        "note": "Scratched: #3 Forged Steel, #5 Seeking Unity",
        "par": 0,
        "picks": [
            {"pp": 1, "name": "GOSGER",
             "beyer": "93-97-87 | Avg: 92.3",
             "trainer": "Walsh Brendan P (20% W) | BlinkOff: 9%",
             "jockey": "Davis D",
             "comment": "PREAKNESS 2nd last year, G2 placed, 101 career best Beyer. Massive class drop from G1/G2 to OC 125k. Blinkers off for Walsh. 180+ days off is the concern but figures are in another galaxy vs this field. Should win if fit."},
            {"pp": 7, "name": "EXCITE",
             "beyer": "80-92-88 | Avg: 86.7",
             "trainer": "Mott William I (22% W)",
             "jockey": "Alvarado J",
             "comment": "G3 winner at Keeneland last summer. 89.7 avg last 3 including a 92. Won two stakes. Mott/Alvarado strong connections. Last out slow race at Churchill (80) but back at GP should suit. Best legitimate challenger to Gosger."},
            {"pp": 2, "name": "NAVAJO WARRIOR",
             "beyer": "80-94-90 | Avg: 88",
             "trainer": "Joseph S A Jr (19% W)",
             "jockey": "Husbands M J",
             "comment": "7 career wins, 88 avg Beyer. Won 6 of last 8 at various tracks. 3rd last out at OC 62k on wet track. Joseph 19% is strong. Husbands knows horse well. Best pace horse in the race."},
        ]
    },
    {
        "num": 8, "post": "4:23 ET",
        "cond": "Allowance Optional Claiming $25k N1X | F&M 4yo+ | 1M 70Y TAPETA (off turf)",
        "note": "⚠️ Originally 1M Turf – moved to Tapeta. Scratched: #2 Calathea, #12 Turino",
        "par": 84,
        "picks": [
            {"pp": 6, "name": "EQUITAS",
             "beyer": "79-65-72 | Avg: 72",
             "trainer": "DePaulo Michael (0% W) | 1stClaim: 27%",
             "jockey": "Panici L",
             "comment": "WON on GP Tapeta Feb 22 at this exact class level (79 Beyer). Race moving to Tapeta is IDEAL for her. Claimed in that win — DePaulo 27% with first claims is strong. Only horse proven on today's surface at this level."},
            {"pp": 12, "name": "LA CANTERA",
             "beyer": "78-78-79 | Avg: 78.3",
             "trainer": "David Carlos A (25% W)",
             "jockey": "Alvarado J",
             "comment": "Best overall Beyers in the field (78.3 avg, multiple wins at GP). Has 4 Woodbine synthetic starts (67 avg). David 25% win rate is top tier. Multiple GP wins at this class. Second choice off turf switch."},
            {"pp": 3, "name": "VAZHI",
             "beyer": "76-73 | Avg: 74.5",
             "trainer": "Carroll Josie (13% W) | Turf: 12%",
             "jockey": "Moran P",
             "comment": "Won Feb 23 on GP DIRT at this class level (73 Beyer). Has shown she handles non-turf. 76 Beyer on turf. Consistent 2nd-place finishes at GP. Surface versatile — race moving off turf helps her cause."},
        ]
    },
    {
        "num": 9, "post": "4:54 ET",
        "cond": "Starter Optional Claiming $20k | 4yo+ | 7f Dirt",
        "note": "No scratches",
        "par": 0,
        "picks": [
            {"pp": 3, "name": "PROUD AMERICAN",
             "beyer": "82-81-71 | Avg: 78",
             "trainer": "Eppler Mary E (27% W) | WonLastStart",
             "jockey": "Karamanos H A",
             "comment": "Won last THREE starts including this exact race condition (OC20k/SAL12k) at GP on March 21. Avg 78 Beyer. Eppler 27% — elite trainer stat. Karamanos 10% but knows the horse. On fire, repeats winners in this spot."},
            {"pp": 2, "name": "PET MAT",
             "beyer": "81-79-71 | Avg: 77",
             "trainer": "Moreno-Barban Leandro (6% W) | WonLastStart: 31%",
             "jockey": "Torres Y",
             "comment": "Won last TWO starts including 7f dirt race. 77 avg Beyer. Won a 7f dirt race Feb 11 (81 Beyer). Moreno-Barban 31% WonLastStart is strong. Should be right there with Proud American in another hot duel."},
            {"pp": 8, "name": "TO THE EASTSIDE",
             "beyer": "78-76 | Avg: 77",
             "trainer": "Puckett Andrea L (21% W) | Dirt: 25%",
             "jockey": "Gutierrez Mario",
             "comment": "3rd last out in this exact race condition (OC20k). 78-76 Beyers trending up. Puckett 25% on dirt is excellent. Zayas won't be up but Gutierrez is capable. Improving horse — could upset the top two."},
        ]
    },
    {
        "num": 10, "post": "5:25 ET",
        "cond": "THE TEXAS GLITTER (Stakes) $125k | 3YO | 5f TAPETA (off turf)",
        "note": "⚠️ Originally 5f Turf – moved to Tapeta. This is a Stakes race.",
        "par": 0,
        "picks": [
            {"pp": 5, "name": "SHIPMATE",
             "beyer": "85-73-68 | Avg: 75.3",
             "trainer": "Ramsey Nolan (13% W) | WonLastStart: 18%",
             "jockey": "Vasquez M A",
             "comment": "Won last out at GP at 85 Beyer (5.5f dirt) — BEST recent Beyer in the field. Won 3 of 5 lifetime. Won a maiden then OC 75k at this distance. Dirt/Tapeta speed horse. Race moving off turf plays right into his strengths. Ramsey 18% WonLastStart."},
            {"pp": 2, "name": "MONSTER",
             "beyer": "84-74-75 | Avg: 77.7",
             "trainer": "D'Angelo Jose F (12% W) | WonLastStart: 21%",
             "jockey": "Ruiz J",
             "comment": "Won OC 75k last out (84 Beyer) at GP on dirt. Front runner with blazing speed (Early 115). Won on GP dirt — Tapeta suits speed horses. D'Angelo 21% WonLastStart. Multiple stakes experience. Could wire the field."},
            {"pp": 8, "name": "INTRICATE SPIRIT",
             "beyer": "83-79-69 | Avg: 77",
             "trainer": "Clement Miguel (11% W) | TurfSprints: 16%",
             "jockey": "Alvarado J",
             "comment": "G3 Futurity winner at BAQ on turf (83 Beyer). Best overall credentials in the field. Moving to Tapeta for first time but won on a different artificial surface (Aqueduct turf). Clement 16% turf sprints. Won't be easy to ignore."},
        ]
    },
    {
        "num": 11, "post": "5:55 ET",
        "cond": "Claiming $10,000 | F&M 4yo+ | 1.5M Tapeta",
        "note": "Scratched: #1 U Know When U Know, #12 Alta Calibre",
        "par": 73,
        "picks": [
            {"pp": 8, "name": "LOIS LEN",
             "beyer": "74 | Won last out",
             "trainer": "Drexler Martin (13% W) | WonLastStart: 15%",
             "jockey": "Castellano J J",
             "comment": "WON last out at GP at this exact class level — 74 Beyer, dominant. CASTELLANO picks up the mount — that's a major upgrade. 7yo Canadian mare who knows how to win. Drexler 15% WonLastStart. Clear top pick."},
            {"pp": 3, "name": "AMELIA",
             "beyer": "68-66-62 | Avg: 65.3",
             "trainer": "Sweezey J K (12% W)",
             "jockey": "Morelos J E",
             "comment": "Won last TWO starts including at this level (68 Beyer). Hot horse on a 2-race winning streak. Sweezey 12% solid. Avg 65.3 is strong for this field. Keep alive in exactas."},
            {"pp": 11, "name": "LET'S DANCE AGAIN",
             "beyer": "68-70-73 | Avg: 70.3",
             "trainer": "De La Cerda Armando (11% W)",
             "jockey": "Ruiz J",
             "comment": "Best avg Beyer (70.3) of the non-winners in the field. 3rd last out, has multiple wins at this level. Improving trajectory (68-70-73). Should hit the board."},
        ]
    },
    {
        "num": 12, "post": "6:25 ET",
        "cond": "Maiden Optional Claiming $50k | F&M 3yo+ FL-bred | 1M 70Y TAPETA (off turf)",
        "note": "⚠️ Originally 1M Turf – moved to Tapeta. Scratched: #4 Di Capri, #7 Clocklike, #9 Tellnotales",
        "par": 68,
        "picks": [
            {"pp": 2, "name": "BIG MAGIC (IRE)",
             "beyer": "69-67 | Avg: 68",
             "trainer": "Dutrow Anthony W (22% W) | Routes: 28%",
             "jockey": "Castellano J J",
             "comment": "Best Beyers in field (68 avg). 3rd last out in a MSW beaten 1.5 lengths. Dutrow 28% routes — elite stat. Castellano confident in the mount. Moving to Tapeta from turf but has shown ability. FL-bred eligibility confirmed."},
            {"pp": 8, "name": "SPINNING CLASS",
             "beyer": "66-66 | Avg: 66",
             "trainer": "McGaughey III C R (5% W) | BlinkOn: 25%",
             "jockey": "Alvarado J",
             "comment": "Beaten a HEAD last out in MSW — desperately unlucky! Adding blinkers (McGaughey 25% BlinkOn stat — excellent). Has shown ability (66-66 consistent). Moving to Tapeta from turf; improvement expected with the headgear."},
            {"pp": 11, "name": "IN TIMING",
             "beyer": "66-34-58 | Recent: 66",
             "trainer": "Crichton Rohan G (27% W)",
             "jockey": "Ruiz J",
             "comment": "Led most of the way last out (66 Beyer) before being caught late. Front-running style suits Tapeta. Crichton 27% win rate is elite. FL-bred. Could lead wire-to-wire on the synthetic."},
        ]
    },
]

# ── PDF BUILDER ───────────────────────────────────────────────────────────
def build_pdf(path):
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=18, textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#444444'), spaceAfter=2)
    race_header_style = ParagraphStyle('RaceHeader', parent=styles['Normal'],
        fontSize=13, fontName='Helvetica-Bold', textColor=colors.white, spaceAfter=0)
    cond_style = ParagraphStyle('Cond', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#555555'), spaceAfter=2)
    note_style = ParagraphStyle('Note', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#CC4400'), spaceAfter=4)
    pick_name_style = ParagraphStyle('PickName', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a1a2e'))
    detail_style = ParagraphStyle('Detail', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#333333'), spaceAfter=1)
    comment_style = ParagraphStyle('Comment', parent=styles['Normal'],
        fontSize=8.5, textColor=colors.HexColor('#222222'), spaceAfter=4)

    story = []

    # ── Header ──
    story.append(Paragraph("🏇 Gulfstream Park — Top-3 Picks", title_style))
    story.append(Paragraph(
        f"March 21, 2026 &nbsp;|&nbsp; Prepared by Charlie &nbsp;|&nbsp; "
        f"All turf races are OFF THE TURF (Tapeta)",
        sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 8))

    for race in RACES:
        # Race header bar
        race_header_data = [[
            Paragraph(f"RACE {race['num']}  |  Post {race['post']}", race_header_style),
        ]]
        race_header_table = Table(race_header_data, colWidths=[7.5*inch])
        race_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(race_header_table)
        story.append(Spacer(1, 3))
        story.append(Paragraph(race['cond'], cond_style))
        story.append(Paragraph(race['note'], note_style))

        for idx, pick in enumerate(race['picks']):
            pp = pick['pp']
            rank_labels = ['1ST PICK', '2ND PICK', '3RD PICK']
            rank_colors = [colors.HexColor('#B8860B'), colors.HexColor('#708090'), colors.HexColor('#8B4513')]

            bg_color = PP_COLORS.get(pp, colors.HexColor('#dddddd'))
            text_color = PP_TEXT_COLORS.get(pp, colors.black)

            pp_cell_style = ParagraphStyle('PPCell', parent=styles['Normal'],
                fontSize=14, fontName='Helvetica-Bold',
                textColor=text_color, alignment=TA_CENTER)
            rank_style = ParagraphStyle('Rank', parent=styles['Normal'],
                fontSize=8, fontName='Helvetica-Bold',
                textColor=rank_colors[idx], alignment=TA_LEFT)
            name_style = ParagraphStyle('Name', parent=styles['Normal'],
                fontSize=11, fontName='Helvetica-Bold',
                textColor=colors.HexColor('#1a1a2e'))

            row_data = [[
                Paragraph(f"#{pp}", pp_cell_style),
                [
                    Paragraph(rank_labels[idx], rank_style),
                    Paragraph(pick['name'], name_style),
                    Paragraph(f"<b>Beyers:</b> {pick['beyer']}", detail_style),
                    Paragraph(f"<b>Trainer:</b> {pick['trainer']}  •  <b>Jockey:</b> {pick['jockey']}", detail_style),
                    Paragraph(pick['comment'], comment_style),
                ]
            ]]

            row_table = Table(row_data, colWidths=[0.5*inch, 7.0*inch])
            row_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), bg_color),
                ('VALIGN', (0,0), (0,0), 'MIDDLE'),
                ('VALIGN', (1,0), (1,0), 'TOP'),
                ('LEFTPADDING', (0,0), (0,0), 4),
                ('RIGHTPADDING', (0,0), (0,0), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
            ]))
            story.append(row_table)
            story.append(Spacer(1, 2))

        story.append(Spacer(1, 8))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#999999')))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=7.5, textColor=colors.HexColor('#666666'), alignment=TA_CENTER)
    story.append(Paragraph(
        "Charlie's Picks — Gulfstream Park 3/21/2026 | IN BEYERS WE TRUST | "
        "All turf races run on Tapeta today. Good luck! 🍀",
        footer_style))

    doc.build(story)
    print(f"PDF saved: {path}")

if __name__ == '__main__':
    out = '/home/damato/.openclaw/workspace/GP_Picks_Mar21_2026.pdf'
    build_pdf(out)
