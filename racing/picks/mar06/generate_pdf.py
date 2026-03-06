#!/usr/bin/env python3
"""Generate Gulfstream Park picks PDF with post position colors — March 6, 2026"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# Standard North American post position colors
PP_COLORS = {
    1:  colors.HexColor('#CC0000'),   # Red
    2:  colors.HexColor('#FFFFFF'),   # White
    3:  colors.HexColor('#003DA5'),   # Blue
    4:  colors.HexColor('#FFD700'),   # Yellow
    5:  colors.HexColor('#00873D'),   # Green
    6:  colors.HexColor('#1A1A1A'),   # Black
    7:  colors.HexColor('#FF6B00'),   # Orange
    8:  colors.HexColor('#FF69B4'),   # Pink
    9:  colors.HexColor('#00CED1'),   # Turquoise
    10: colors.HexColor('#7B2FBE'),   # Purple
    11: colors.HexColor('#808080'),   # Gray
    12: colors.HexColor('#32CD32'),   # Lime
}

PP_TEXT_COLORS = {
    1: colors.white, 2: colors.black, 3: colors.white,
    4: colors.black, 5: colors.white, 6: colors.white,
    7: colors.white, 8: colors.black, 9: colors.black,
    10: colors.white, 11: colors.white, 12: colors.black,
}

def pp_badge(pp_num, horse_name):
    """Return HTML string for a colored PP badge + horse name"""
    bg = PP_COLORS.get(pp_num, colors.grey)
    tc = PP_TEXT_COLORS.get(pp_num, colors.white)
    bg_hex = bg.hexval() if hasattr(bg, 'hexval') else '#888888'
    tc_hex = tc.hexval() if hasattr(tc, 'hexval') else '#ffffff'
    return f'<font color="{tc_hex}"><b> #{pp_num} </b></font> <b>{horse_name}</b>'

def make_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.65*inch,
        leftMargin=0.65*inch,
        topMargin=0.75*inch,
        bottomMargin=0.65*inch
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
        fontSize=18, textColor=colors.HexColor('#003DA5'),
        alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold')
    
    subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER, spaceAfter=6)

    warning_style = ParagraphStyle('Warn', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#CC0000'),
        alignment=TA_CENTER, spaceAfter=8, backColor=colors.HexColor('#FFF3CD'),
        borderPadding=4)

    race_header_style = ParagraphStyle('RaceHdr', parent=styles['Normal'],
        fontSize=12, textColor=colors.white, fontName='Helvetica-Bold',
        spaceAfter=4, spaceBefore=10)

    pick_label_style = ParagraphStyle('PickLabel', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#888888'),
        fontName='Helvetica-Bold', spaceAfter=1)

    pick_horse_style = ParagraphStyle('PickHorse', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold', spaceAfter=2)

    beyer_style = ParagraphStyle('Beyer', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#333333'), spaceAfter=2)

    analysis_style = ParagraphStyle('Analysis', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#222222'), spaceAfter=6,
        leading=13)

    best_bet_style = ParagraphStyle('BestBet', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#7B2FBE'), spaceAfter=4)

    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER, spaceBefore=8)

    elems = []

    # Title block
    elems.append(Paragraph('🏇 GULFSTREAM PARK — TOP 3 PICKS', title_style))
    elems.append(Paragraph('March 6, 2026 &nbsp;|&nbsp; 10 Races &nbsp;|&nbsp; First Post: 12:50 PM ET', subtitle_style))
    elems.append(Paragraph('Method: Beyer Avg (last 3) + Form / Class / Pace / Trainer-Jockey', subtitle_style))
    elems.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#003DA5'), spaceAfter=6))
    elems.append(Paragraph('⚠️  Scratch Status: No GP scratches posted as of 9:00 AM — Re-verify at 11:30 AM before betting', warning_style))
    elems.append(Spacer(1, 4))

    # Race data
    races = [
        {
            'num': 1, 'title': 'OC35k/SAL35k | 1M Turf | 3YO | Post: 12:50 PM',
            'picks': [
                (7, 'RAMSES THE GREAT', '62.0 avg (72-55-59)',
                 'Best Beyer in field at 72 earned two starts ago in this exact race (OC35k GP turf). Rallied 3-wide, led upper stretch, finished 2nd — shows he belongs at top. Trainer Nolan 19% GP routes; Vasquez 30% J/T GP.'),
                (9, 'ANTONINO', '57.3 avg (63-52-57)',
                 'Won 1M GP turf Jan 1 (63 Beyer) going 3-wide. Two prior turf wins at GP at this exact distance. Trainer Sano 22% J/T GP. Proven at this course and surface.'),
                (2, 'CHICKEN DANCE', '55.7 avg (66-57-44)',
                 'Finished a strong 3rd at 1⅛M GP turf Feb 12 (66 Beyer), rallying 4-wide from 8th. Two wins in three career starts. Trainer Abreu 25% J/T GP; Rosario up. Shorter 1M trip suits.'),
            ]
        },
        {
            'num': 2, 'title': 'Clm12500N2L | 6.5f Dirt | F&M 3yo+ | Post: 1:20 PM | Beyer par: 60',
            'picks': [
                (5, 'BOOMBOX BETTY', '54.0 avg (65-49-48)',
                 'Best career Beyer in field at 65 — won wire-to-wire at GP Md12500 (Oct 2025). Early pace figure of 87 gives her a lead from the gate. Trainer Spatz 15% Dirt, 16% Claim. Back at right spot.'),
                (1, 'JAYANA', '45.3 avg (35-51-50)',
                 'Most experienced horse in the field — 21 career starts, multiple 2nd/3rd at Clm12500N2L at GP. Class familiarity and Morelos returns for this mare. Most consistent at this exact level.'),
                (6, 'ALONGCOMESAWOMAN', '56.7 avg (18-56-76)',
                 'Career top Beyer of 76 (win, Clm16000 mud) and 56 at same level — both above par here. The 18 last out was a troubled trip at GP. Massive class relief back to Clm12500N2L. Trainer Delgado 21% Dirt.'),
            ]
        },
        {
            'num': 3, 'title': 'Md25000(25-20) | 5f Tapeta | Fillies 3yo | Post: 1:50 PM',
            'picks': [
                (5, 'MISS JENNA', 'First Start',
                 'Trainer Orseno hits at 23% 1stStart and 22% DebutMCL. Hard Spun filly (proven speed sire on Tapeta) with bullet 4f :47.2 (2nd/6 at GP). Alvarado Jr. up. Best connections in the race for a debut.'),
                (8, 'STREET SUE', '45.0 avg (50-45--)',
                 'Ran 2nd at BAQ MSW (50 Beyer). Early pace figure 104 — highest in field, will lead from gate. Authentic filly ($140k purchase). Trainer Sacco 20% 1stLasix. Front-runner on Tapeta is a potent combo.'),
                (3, 'LOOKS TO KILL', '46.3 avg (55-47-37)',
                 'Most experienced Tapeta/Synth runner in field (8 starts). Best Beyer 55 on Synth at Turfway (Clm30000). Has the experience edge in a field of lightly-raced fillies. Trainer Antonucci; Morelos up.'),
            ]
        },
        {
            'num': 4, 'title': 'Clm8000N3L | 5f Tapeta | 4yo+ | Post: 2:20 PM | Beyer par: 75',
            'picks': [
                (6, 'MAITRE D', '78.0 avg (87-90-78)',
                 'TOP PICK of the day. Best Beyer in field — won Clm17500N2L (90 speed), ran 2nd in Clm8000N3L (87 speed). Just claimed by trainer Tomlinson: 30% WonLastStart, 26% 1stClaim. Massive class relief, early pace 103 puts him on the lead.'),
                (3, 'TRANSACTIONAL GUY', '69.0 avg (66-45-69)',
                 'Won last out at Clm8000N2L Feb 28 (91 speed). Trainer Tharrenos 22% WonLastStart, 25% Synth. Ortiz Jr. 40% J/T GP with this horse recently. Explosive early speed (pace 103). Steps up but form is live.'),
                (4, 'MACKOR', '70.3 avg (67-63-65)',
                 'Best career Beyer 73 — consistent Clm8000 performer with multiple placings at this exact level/distance at GP. Trainer Hurtak 18% Synth; Perez E knows this horse from prior starts. Reliable third.'),
            ]
        },
        {
            'num': 5, 'title': 'Alw54000N1X | 1M Turf | 3YO FL-bred | Post: 2:51 PM',
            'picks': [
                (4, 'SQUIRE', '73.0 avg (87-73-69)',
                 'Best Beyer in field — 3rd in this exact race Feb 1 (87 speed), 2nd in FS Affirmed Stakes (69), WON debut (73). Most consistently competitive FL-bred in the division. Trainer Biancone 24% J/T GP; Egan aboard.'),
                (1, 'MY FAVORITE BIRD', '67.3 avg (75-70-51)',
                 'Won last out OC35k/SAL35k GP turf Feb 12 (75 Beyer). Earned the class rise. 2nd the start before at same level. Trainer Luces 15% WonLastStart; Morelos keeps the mount after win.'),
                (7, 'NICKEL C', '69.0 avg (69-68-66)',
                 'Won last out Moc50k GP turf Feb 27 (69 Beyer). Previous 3rd in same race series. Consistent turf performer. Trainer Fawkes 26% WonLastStart, 22% Turf, 19% Routes. Gaffalione up 16% J/T GP.'),
            ]
        },
        {
            'num': 6, 'title': 'Clm8000N3L | 7f Dirt | F&M 4yo+ | Post: 3:22 PM | Beyer par: 63',
            'picks': [
                (6, 'FIVE EYES ONMICHEL', '57.7 avg (61-59-56)',
                 'Won last out Clm8000N2L Feb 9 (81 speed). 6 top-3 finishes in last 10 starts at GP — most experienced horse in this field (20 GP starts!). Won wire-to-wire; will be prominent early. Trainer Rodriguez 17% Claim; Torres Jr. returns.'),
                (1, 'WIDERTHANAMILE', '46.3 avg (46-55-35)',
                 'Won last out Clm8000N2L Feb 22 (71 speed). Trainer Orseno 14% WonLastStart. Stepping from N2L to N3L, but form is sharp. Juarez aboard for the win and stays on. Best recent race at 7f — distance suits.'),
                (5, 'BEAUTIFUL BOLT', '54.3 avg (58-65-40)',
                 '2nd last out at Clm8000N3L (77 speed) — this exact level today. Won at Clm7500 (92 speed). Trainer Breen 26% 2Off45-180 — fits the angle perfectly. Has the figures to win if today\'s form matches the best.'),
            ]
        },
        {
            'num': 7, 'title': 'OC75k/N1X | 5f Turf | Fillies 3yo | Post: 3:53 PM',
            'picks': [
                (10, 'CATALONIA', '76.3 avg (79-79-75)',
                 'Best Beyer in field at 79. Multiple 2nds at OC75k/N1X — dominant consistent performer at this exact level at GP. Won GP MdSpWt (94 speed). Always rallies at this distance. Trainer D\'Angelo 20% Alw; Ruiz J up. Class of the field.'),
                (5, 'GLANCING MY WAY', '61.0 avg (61-58-42)',
                 'Won back-to-back at OC35k GP turf (86 speed last out Feb 28). Hot horse stepping up for first time. Trainer Castro 25% WonLastStart, 21% TurfSprints. Castellano (elite at 5f turf) takes over — big upgrade in rider.'),
                (12, 'TIZASWEETLADY (AE)', '80.0 avg (80-49-65)',
                 'ALSO ELIGIBLE — needs scratch to draw in. Won Alw54k Feb 28 at this exact distance (80 Beyer, 94 speed) — stronger company, won easily going 4-wide. Karamanos 20% WonLastStart stays on. IF she draws in, move to #1 pick.'),
            ]
        },
        {
            'num': 8, 'title': 'Md25000(25-20) | 6f Dirt | 3yo Males | Post: 4:23 PM',
            'picks': [
                (5, 'EPICO', '57.7 avg (63-42--)',
                 'Best recent Beyer — 2nd at Moc50k Feb 3 (63 Beyer), missed by a nose. BlinkerON today: trainer Sano 20% 1stBlink, 18% BlinkOn. Zayas Jr. keeps the mount. Equipment change is the catalyst in a weak field.'),
                (1, 'SONIC SURGE', '52.0 avg (64--)',
                 'Best career Beyer 64 earned vs MSW company at Aqueduct. Drops into maiden claiming — significant class relief. Trainer Weaver 21% MSWtoMCL, 26% 1stLasix. Gaffalione up (16% J/T GP). Should find this much easier.'),
                (2, 'MO RAPIDO', 'First Start',
                 'Trainer Barboza 20% 1stStart, 19% DebutMCL. Best work: bullet 4f :46.0 (2nd of 28 at GP Feb 21) — elite debut figure. Uncle Chuck sire (Mo speed on Tapeta). Perez E up. If talent matches works, wins fresh.'),
            ]
        },
        {
            'num': 9, 'title': 'Clm25000(25-20)B | 5.5f Tapeta | 4yo+ | Post: 4:54 PM | Beyer par: 80',
            'picks': [
                (8, 'MOON LANDING', '82.3 avg (85-89-73)',
                 'Best Beyer in field — 2nd at Clm25000B (94 speed last out Feb 10). Multiple WO wins at OC32k. Claimed by Drexler who excels at 2Off45-180 (20%) and Synth (18%). Class fits, figures are best in race. Top pick.'),
                (2, 'AIR FORCE CRUISING', '84.0 avg (89-91-73)',
                 'Best career Beyer 84 (Alw25k win at GP). 2nd at Clm25000B last out (89 speed). New trainer Sweezey 29% 1stClaim — elite new-trainer angle. Pace figure 112 puts him on the lead. Won at Alw25k; this is class relief.'),
                (5, 'GIANT TEDDY', '83.0 avg (90-83-83)',
                 'Best career Beyer 95 — all at WO competing at OC32k-80k level. Steps DOWN dramatically at GP Clm25k. Trainer Drexler 20% 2Off45-180, 20% Synth, 19% Claim. If WO form transfers, class is far above this field. Upset threat.'),
            ]
        },
        {
            'num': 10, 'title': 'OC125k/N2X | 5f Turf | 4yo+ | Post: 5:24 PM | Beyer par: 92',
            'picks': [
                (2, "ASHER'S EDGE", '90.0 avg (92-90-94)',
                 '4th in GpTrfSptL155k Jan 24 (top-class race), 90+ Beyers three starts running. Won OC25k/N1X at this distance (94 Beyer). Trainer Fawkes 16% TurfSprints, 22% Turf. Ortiz JL up. Most reliable and consistent horse in field.'),
                (7, 'MASSETO (GB)', '97.0 avg (103-97-88)',
                 'Best career Beyer in field at 103 (CD OC80k win). Long layoff but trainer O\'Connell 16% 2OffOver180 specializes in returning horses. Zayas up (38% J/T GP). If he fires fresh, class is clearly best in the race. High upside.'),
                (1, 'EXTENDO', '84.3 avg (78-69-96)',
                 'Won GP Alw at 100 Beyer in 2025. Bombed at Tampa (78, 12th of 12) but was a terrible trip. Multiple 90s+ at GP turf. Trainer Orseno 16% TurfSprints. Returns to home track: 7-7-1 career record at GP on this surface.'),
            ]
        },
    ]

    for race in races:
        rnum = race['num']
        # Race header bar
        hdr_table = Table([[Paragraph(f"RACE {rnum}  —  {race['title']}", ParagraphStyle(
            'RH', parent=styles['Normal'], fontSize=10, textColor=colors.white,
            fontName='Helvetica-Bold'))]],
            colWidths=[7.2*inch])
        hdr_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#003DA5')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        elems.append(hdr_table)
        elems.append(Spacer(1, 4))

        for rank, (pp, horse, beyer_text, analysis) in enumerate(race['picks'], 1):
            rank_labels = {1: '⭐ #1 PICK', 2: '  #2 PICK', 3: '  #3 PICK'}
            rank_color_hex = {1: '#CC7700', 2: '#555555', 3: '#555555'}

            # PP color badge
            bg_col = PP_COLORS.get(pp, colors.grey)
            txt_col = PP_TEXT_COLORS.get(pp, colors.white)

            pp_cell = Paragraph(f'<b>#{pp}</b>', ParagraphStyle(
                'PPCell', parent=styles['Normal'], fontSize=11,
                textColor=txt_col, fontName='Helvetica-Bold', alignment=TA_CENTER))

            horse_cell = Paragraph(
                f'<font color="{rank_color_hex[rank]}"><b>{rank_labels[rank]}</b></font>  <b>{horse}</b>  <font size="8" color="#666666">— Beyer: {beyer_text}</font>',
                ParagraphStyle('HC', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold'))

            pick_table = Table([[pp_cell, horse_cell]], colWidths=[0.42*inch, 6.8*inch])
            pick_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), bg_col),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (0,0), 'CENTER'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (1,0), (1,0), 6),
                ('ROUNDEDCORNERS', [3]),
            ]))
            elems.append(pick_table)
            elems.append(Paragraph(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{analysis}', analysis_style))

        elems.append(Spacer(1, 6))

    # Best bets
    elems.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#CC7700'), spaceAfter=6))
    elems.append(Paragraph('⭐ BEST BETS OF THE DAY', ParagraphStyle('BBH', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#CC7700'),
        spaceAfter=4)))
    
    bets = [
        ('R4 #6 MAITRE D', 'Claimed horse + hot trainer (30% WonLastStart, 26% 1stClaim) + best Beyer in field'),
        ('R5 #4 SQUIRE', 'Best figures in FL-bred Allowance — 3rd in this race last time, consistent stakes performer'),
        ('R9 #8 MOON LANDING', 'Best Beyer 85, 2nd last out at Clm25000B — class fits, figures are top of race'),
    ]
    for horse, reason in bets:
        elems.append(Paragraph(f'<b>{horse}</b> — {reason}', best_bet_style))

    # Footer
    elems.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceAfter=4))
    elems.append(Paragraph(
        'In Beyers We Trust 🐴 | Generated by Charlie @ 9:00 AM ET | Verify scratches at 11:30 AM before betting',
        footer_style))

    doc.build(elems)
    print(f"PDF created: {output_path}")

if __name__ == '__main__':
    make_pdf('/home/damato/.openclaw/workspace/racing/picks/mar06/picks_gp_2026-03-06.pdf')
