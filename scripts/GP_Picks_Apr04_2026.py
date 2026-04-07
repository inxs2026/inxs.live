#!/usr/bin/env python3
"""
GP Picks - April 4, 2026 (Corrected post positions from TrackData)
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

RACES = [
    {
        "num": 1, "post": "12:50 ET",
        "cond": "Maiden Claiming $12,500 | 3yo+ | 1 Mile Tapeta | Beyer Par: 64",
        "note": "SCRATCH: #8 Animated (vet scratch)",
        "par": 64,
        "picks": [
            {"pp": 3, "name": "TAPSTICK",
             "beyer": "79-75-70 | Avg: 74.7",
             "trainer": "Smullen Heather (11%)",
             "jockey": "Torres Y",
             "comment": "4 seconds from 10 starts — close and consistent. 79 Beyer last race at this level is sharp. Synth specialist (3/3 second-place finishes on synth). Jockey Panici won 2nd with him last race. Bounce potential at short price (5-2 ML)."},
            {"pp": 2, "name": "FROSTED PUNK",
             "beyer": "75-72-70 | Avg: 72.3",
             "trainer": "O'Connell Kathleen (11%)",
             "jockey": "Herrera D",
             "comment": "Consistent runner-up at this level. 75 Beyer in most recent start vs similar $12.5K maidens. O'Connell 11% OK, horses for this barn run honest. At 6-1 ML — decent price. Exotics play."},
            {"pp": 10, "name": "MY FOOLISH NOTION",
             "beyer": "86-81-82 | Avg: 83.0",
             "trainer": "Miller Herbert (0%)",
             "jockey": "Ocasio J",
             "comment": "Best Beyer average in the field (83.0). Consistently running 80+ in latest 3 at this class/travels. Maiden 0-for-8 but class relief from $25K claiming to $12,500 level is sharp. Synth surface best. Long price (20-1) — must use on exotics."},
        ]
    },
    {
        "num": 2, "post": "1:22 ET",
        "cond": " AOC $75K/N1X (Fillies) | 3yo | 1 1/16M Turf | Beyer Par: NA",
        "note": "Turf (Rail at 45ft). If off-turf goes to Tapeta.",
        "par": None,
        "picks": [
            {"pp": 1, "name": "TULUNO",
             "beyer": "78-91-88 | Trend: rising",
             "trainer": "Gallegos Jose A (24%)",
             "jockey": "Gomez J",
             "comment": "Just won at Tampa going away — Beyer 78. Undefeated on turf (2/2). Turf 2 wins from 2 starts, both front-end trips. Gallegos 24% strong. Rider Gomez back. Gets class relief and should get perfect setup behind speed. Clear top selection at 4-1."},
            {"pp": 3, "name": "OSCAR BOUND",
             "beyer": "85-79-83 | Trend: rising",
             "trainer": "Giddings Melanie (12%)",
             "jockey": "Bridgmohan S",
             "comment": "Won last 2 starts — latest 85 Beyer at Tampa. Turf 1-of-1 at GP. Giddings 12% but improving barn. Bridgmohan rides well for her. Has tactical speed to sit off likely pace. At 10-1 — solid value on exotics."},
            {"pp": 4, "name": "ONE SWEET GIRL",
             "beyer": "76-83-80 | Avg: 79.7",
             "trainer": "David Carlos A (26%)",
             "jockey": "Vasquez M",
             "comment": "Turf 2/2 at GP including a win at this 1 1/16M trip. Late runner (Late 102) — perfect exotics setup behind expected pace duel. David Carlos 26% is very strong. Vasquez has won on her before. Hidden value at 3-1 ML."},
        ]
    },
    {
        "num": 3, "post": "1:54 ET",
        "cond": "Maiden Claiming $17,500 (Fillies) | 3yo | 5 Furlongs Tapeta | Beyer Par: NA",
        "note": "SCRATCHES: #4 Jadacaquiva (vet), #7 Affluenza (vet). Field reduced to 5.",
        "par": None,
        "picks": [
            {"pp": 2, "name": "BARONIA",
             "beyer": "84-84-87 | Avg: 85.0",
             "trainer": "Zanelli Dante (25%)",
             "jockey": "Vasquez M",
             "comment": "Highest Beyer in the field (85 avg). Missed 2nd at Tampa when bumped start, wide trip. Turf 0/4 — drop to synth is a positive. Vasquez rides her regularly. At $17.5K claiming with Beyer 85 against maiden fillies — she dominates."},
            {"pp": 1, "name": "MY GIRL NINA",
             "beyer": "74-67-77 | Avg: 72.7",
             "trainer": "Klesaris Steve (13%)",
             "jockey": "Ruiz J",
             "comment": "Consistent — 1 win, 4 seconds from 7 starts. Class relief: entered at $17.5K after racing $35K and $25K maidens. Ruiz stays aboard. Bad trip excuses in last 2 (bumped start, wide). Fits at this level. Solid place/show at 4-1."},
            {"pp": 5, "name": "TIE IT WITH A BOW",
             "beyer": "N/A — Firster",
             "trainer": "Lightner Mary (14%)",
             "jockey": "Maragh R",
             "comment": "First-time starter with sharp works (fastest :46 on dirt, :46 on synth). Lightner 14% wins at GP. Maragh hot (158 rides, 15 wins). Worth include on debut especially on synth surface. Trainer 14% is a concern — use underneath only."},
        ]
    },
    {
        "num": 4, "post": "2:24 ET",
        "cond": "Claiming $8,000 N2L | 3yo+ | 5 Furlongs Tapeta | Beyer Par: 70",
        "note": "SCRATCH: #6 Saint Cloud (vet). Field reduced to 7.",
        "par": 70,
        "picks": [
            {"pp": 7, "name": "LODATO",
             "beyer": "86-84-77 | Avg: 82.3",
             "trainer": "D'Angelo Jose Francisco (18%)",
             "jockey": "Torres Y",
             "comment": "3 wins, 3 seconds from 5 starts at 5F on synth. Best Beyer (86) is top figure in field. Consistent: 4 starts back at this class — all competitive. D'Angelo 18% solid. If Lavirgen continues — leads gate to wire. At 5-2 ML — fair price."},
            {"pp": 1, "name": "LAST RUN",
             "beyer": "90-84-83 | Avg: 85.7",
             "trainer": "Cadahia Benny C (10%)",
             "jockey": "Nicholls M",
             "comment": "Highest Beyer in race (90) — but inconsistent. Won $8K claiming at this distance in Jan. Cadahia only 10% wins but horses for this barn run honest. Nicholls picks up the mount. Price likely attractive (12-1). Use underneath."},
            {"pp": 2, "name": "KINETIC STONE",
             "beyer": "89-89-86 | Avg: 88.0",
             "trainer": "Chapman Beau J (21%)",
             "jockey": "Vasquez M",
             "comment": "Highest Beyer in field (88 avg). 5 wins from 42 starts shows battleship — but Beyer says he belongs at this level. Chapman 21% excellent. Vasquez hot. Best closing kick in race (Late 50). For exotic players — dangerous late at 3-1."},
        ]
    },
    {
        "num": 5, "post": "2:54 ET",
        "cond": "Maiden Special Weight $68K | 3yo+ | 1 Mile Tapeta | Beyer Par: 77",
        "note": "SCRATCHES: #3 Smooth an Easy (vet), #5 Whine Country (vet). Field reduced to 5.",
        "par": 77,
        "picks": [
            {"pp": 6, "name": "VERSAILLES ROAD",
             "beyer": "81-86-84 | Avg: 83.7",
             "trainer": "Pletcher Todd A (18%)",
             "jockey": "Maragh R",
             "comment": "Top Beyer average (83.7). Finished 4th-6th-4th vs $40-103K maidens — this drop to $68K MSW is sharp relief. Beyer par 77 is HIGHEST PAR in field — he fits well below par. Pletcher 18% with top barn stats. At 9-5 ML — likely a short price but deserved."},
            {"pp": 1, "name": "LIKENESS",
             "beyer": "67-69-79 | Avg: 71.7",
             "trainer": "McGaughey Claude R III (10%)",
             "jockey": "Husbands M",
             "comment": "McGaughey is a top-tier conditioner (Classic/Del Mar). Turf 1/5 but ran 2nd vs $34K MSW last out with trouble. Moves to 1-mile Tapeta — more distance should help. Husbands rides him well. Could round exotics at 6-1."},
            {"pp": 2, "name": "THE BIG GUAVA (FR)",
             "beyer": "77 (first start)",
             "trainer": "Walsh Brendan P (18%)",
             "jockey": "Camacho S",
             "comment": "First-time starter from Europe — blinkers added first time (could boost early). Walsh 18% is strong. Has turf pedigree. First start gets first-time Lasix too. Price likely huge (9-2 ML). Worth a flyer on exotics."},
        ]
    },
    {
        "num": 6, "post": "3:26 ET",
        "cond": "Handicap $75K | 4yo+ | 5 Furlongs Turf | Beyer Par: NA",
        "note": "SCRATCHES: #3 Masseto, #4 Xy Speed, #8 Society's Thunder, #9 Esperon (all scratches). Field reduced to 6.",
        "par": None,
        "picks": [
            {"pp": 5, "name": "WAR BOMBER (IRE)",
             "beyer": "99 (career best) | 89-89-96",
             "trainer": "Coy Ronald (10%)",
             "jockey": "Husbands M",
             "comment": "99 Beyer at 1 mile in Jan — career top at GP. Drops to 5F with early speed (Early 93). If he gets loose on lead, will be tough to run down. Coy 10% is a concern but horse is top draw. On a rebound after freshening. At 6-1 — price is there."},
            {"pp": 2, "name": "TEST FACTOR",
             "beyer": "90-94-98 | Avg: 94.0",
             "trainer": "Crichton Rohan G (29%)",
             "jockey": "Gomez J",
             "comment": "Highest trainer win rate in field (29%). 90+ Beyer figures in last 3 including a 98 at CD. Late runner (Late 69) suits the pace scenario. Should sit mid-pack and close into any hot early fractions. At 15-1 — excellent exotic value."},
            {"pp": 1, "name": "OKIRO",
             "beyer": "97-93-95 | Avg: 95.0",
             "trainer": "Garoffalo Jose (17%)",
             "jockey": "Bravo J",
             "comment": "Near-miss 3rd last out (97 Beyer) in OC $125K/N2X at Tampa — just missed at 5F. Course record-level speed. Bravo hot (76 rides, 7 wins). Runner-up to War Bomber type before. Big threat to win at 6-1."},
        ]
    },
    {
        "num": 7, "post": "3:58 ET",
        "cond": "Claiming $12K | 3yo+ | 5 Furlongs Tapeta | Beyer Par: 79",
        "note": "No scratches in Race 7.",
        "par": 79,
        "picks": [
            {"pp": 1, "name": "BANNEKER",
             "beyer": "84-77-89 | Avg: 83.3",
             "trainer": "Orseno Joseph (13%)",
             "jockey": "Herrera D",
             "comment": "Best Beyer in race (84-77-89 = 83.3 avg). 89 Beyer was a win vs starter $10K at this distance. Orseno 13% solid. Herrera rides him regularly. Has tactical speed to sit off pace. At 15-1 — excellent price on top selection."},
            {"pp": 2, "name": "KINETIC STONE",
             "beyer": "89-89-86 | Avg: 88.0",
             "trainer": "Chapman Beau J (21%)",
             "jockey": "Vasquez M",
             "comment": "Highest Beyer in field (88 avg). 5 wins from 42 starts — warrior. Chapman 21% excellent. Vasquez on fire. Comes from behind (Late 50). Could be catching a softer field here at $12K level. Best closer in race at 3-1."},
            {"pp": 3, "name": "BREEZER",
             "beyer": "88-89-92 | Avg: 89.7",
             "trainer": "Sano Antonio (11%)",
             "jockey": "Zayas E",
             "comment": "Highest late pace in race (Late 43). Zayas is top jockey (158 rides, 25 wins). Won 2 back vs $8K starter. Sano 11% OK. At this level with 89 Beyer average — he's a live underneath play. Pace scenario (Early 95) could set up perfectly for his closing kick at 6-1."},
        ]
    },
    {
        "num": 8, "post": "4:31 ET",
        "cond": " AOC $25K/N1X (Col & Geldings) | 4yo+ | 5 Furlongs Turf | Beyer Par: 89",
        "note": "SCRATCHES: #5 Coffee At K J's (vet), #9 Front End (vet). Field reduced to 8.",
        "par": 89,
        "picks": [
            {"pp": 1, "name": "GIANT TEDDY",
             "beyer": "94-97-88 | Avg: 93.0",
             "trainer": "Spatz Ronald B (7%)",
             "jockey": "Bravo J",
             "comment": "Back-to-back wins with 94-97 Beyer at this level. Highest early pace in race (Early 104). Course specialist (won twice at GP turf). Bravo rides him well. 5 wins from 33 starts shows consistency at this class. Clear top selection at 8-1."},
            {"pp": 3, "name": "FUOCO VIVO",
             "beyer": "86-89-85 | Avg: 86.7",
             "trainer": "Crichton Rohan G (29%)",
             "jockey": "Saez L",
             "comment": "Crichton 29% — best trainer in race. Won 2 back at $50K OC. Saez is top jockey. Turf sprint angle fits well. Pace rating (Early 102) means he'll be forward. Second best early speed behind Giant Teddy. Could pounce if favorite stubs toe at 15-1."},
            {"pp": 4, "name": "PAJARO",
             "beyer": "97-95-79 | Beyer: rising",
             "trainer": "Hernandez Sandino R Jr (0%)",
             "jockey": "Herrera D",
             "comment": "97 Beyer 2 back was a win at $97K OC at GP — that figure is huge for this level. Blinkers added first time could spark improvement. Class relief to $25K N1X is positive. 2 wins at GP turf. At 20-1 likely — use for exotics at big price."},
        ]
    },
    {
        "num": 9, "post": "5:02 ET",
        "cond": "Allowance $65K (FL Bred Fillies/Mares) | 3yo+ | 6 Furlongs Turf | Beyer Par: 73",
        "note": "No scratches in Race 9.",
        "par": 73,
        "picks": [
            {"pp": 5, "name": "GIRVIN STAR",
             "beyer": "93-90-95 | Avg: 92.7",
             "trainer": "Ward Wesley A (0%)",
             "jockey": "Torres Y",
             "comment": "Highest Beyer in race (92.7 avg). Won 2 back with 95 Beyer at Tampa. Improving horse (95-90-93 last 3). Ward 0% is a concern but Torres is solid. Good early speed (Early 92). Could win gate to wire if clear at 6-1."},
            {"pp": 7, "name": "VIVI GET YOUR GUNS",
             "beyer": "99-77-84 | Beyer: mixed",
             "trainer": "Simpson Willoughby (0%)",
             "jockey": "Nicholls M",
             "comment": "99 Beyer 3 back was a big win. Last race 77 was rough (stumbled start). Drops back to 6F from 7F — shorter trip suits better. Nicholls at 15-1. Horse has too much talent at this level. Big if catches trip."},
            {"pp": 2, "name": "ROXY",
             "beyer": "80-79-83 | Avg: 80.7",
             "trainer": "Dobles Elizabeth L (0%)",
             "jockey": "Camacho S",
             "comment": "Camacho is hot (158 rides, 15 wins). Roxy consistently running 79-83 Beyer at this class. Pace scenario (Early 82) suits — close to front. Dobles 0% is a worry. Use for place/show at 2-1."},
        ]
    },
    {
        "num": 10, "post": "5:35 ET",
        "cond": "Claiming $17,500 | 4yo+ | 5 Furlongs Turf | Beyer Par: 75",
        "note": "No scratches in Race 10.",
        "par": 75,
        "picks": [
            {"pp": 7, "name": "SARATOGA CRUISER",
             "beyer": "80-78-85 | Avg: 81.0",
             "trainer": "Maragh Collin (0%)",
             "jockey": "Ruiz J",
             "comment": "Highest Beyer average (81.0). Won last 2 at Tampa and GP. 5 wins from 19 starts at the class. Consistent pattern of 80+ Beyers. Ruiz rides him well. Has early speed. If he gets loose on lead — looks best in race at 20-1 ML."},
            {"pp": 9, "name": "BIG BOB",
             "beyer": "76-85-83 | Avg: 81.3",
             "trainer": "Passley Mark M (5%)",
             "jockey": "Ocasio J",
             "comment": "Best Beyer (85) was 2 back. Passley only 5% but horse is fit and ready. Speed figures match up with top picks. At 5-1 — price is there. Use for exotics."},
            {"pp": 1, "name": "ANTONINO",
             "beyer": "78-80-82 | Avg: 80.0",
             "trainer": "Sano Antonio (11%)",
             "jockey": "Gomez J",
             "comment": "Sano 11% — better than Passley. Consistent 78-80 Beyer range. Late runner (Late 82). If pace is fast — his closing kick could be the best. For exotic players. At 12-1 ML — fair price."},
        ]
    },
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
    story.append(Paragraph("🏇 Gulfstream Park – April 4, 2026", title_style))
    story.append(Paragraph("Charlie's Top-3 Picks | Post Positions Verified via TrackData | PP Colors: Saddlecloth Chart", sub_style))
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
            fg_hex = pp_text_hex(pp)
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
                ('BOX',           (0,0), (0,-1),  1.5, bdr),
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
        f"Generated by Charlie | {datetime.date.today().strftime('%B %d, %Y')} | Post positions verified via TrackData MCP | Saddlecloth colors from /home/damato/.hermes/skills/racing/saddlecloth.md | For entertainment only. Verify scratches before wagering.",
        footer_style))
    doc.build(story)
    print(f"PDF created: {output_path}")

if __name__ == "__main__":
    build_pdf("/home/damato/.openclaw/workspace/GP_Picks_Apr04_2026.pdf")
