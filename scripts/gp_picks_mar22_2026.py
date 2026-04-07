#!/usr/bin/env python3
"""
Gulfstream Park Picks – March 22, 2026
Charlie's Top-3 Picks methodology
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_badge_style, pp_text_hex, pp_border_color
RACES = [
    {
        "num": 1, "post": "12:50 ET",
        "cond": "Claiming $25,000 N2L | 3yo+ | 1 Mile Turf",
        "note": "",
        "par": 78,
        "picks": [
            {"pp": 6, "name": "CORSO'S PICK",
             "beyer": "92-88-91 | Avg: 90.3",
             "trainer": "Oliver Victoria (0% W! — Saez/Zayas level jockey switch)",
             "jockey": "Saez L",
             "comment": "Best figures in the field by a massive margin (avg 90.3). Has been running OC 20k/N1X company and all three recent starts are 88+ Beyers. Drops from N1X to N2L for the first time — a significant class relief. Front-running style suits the 1M turf perfectly."},
            {"pp": 9, "name": "NAME IT",
             "beyer": "82-78-88 | Avg: 82.7",
             "trainer": "Toner James J (6% W)",
             "jockey": "Zayas E J",
             "comment": "Two straight top-3 finishes at this exact condition (Clm 25000 N2L, 1M turf at GP), led at the 1/4 pole last time. Best recent Beyer 88 two back. Zayas returns; has been knocking on the door and the 82 last out was a creditable effort from a prompting position."},
            {"pp": 7, "name": "ABUELO",
             "beyer": "87-72-80 | Avg: 83.3",
             "trainer": "Zanelli Dante (11% W)",
             "jockey": "Husbands M J",
             "comment": "Won a GP maiden at this distance with an 87 Beyer two starts back. Forms show closing style late, and competitive with better horses (posted 74 figure at GP turf). Fresh off a layoff but works look solid. Husbands sits back; drop to claiming level for the first time is the key angle."},
        ]
    },
    {
        "num": 2, "post": "1:20 ET",
        "cond": "Maiden Claiming $12,500 | 3yo+ Fillies | 1 1/16 Miles Tapeta",
        "note": "",
        "par": 57,
        "picks": [
            {"pp": 5, "name": "LA CYBER",
             "beyer": "71-69-76 | Avg: 72.0",
             "trainer": "Castro Jose M (9% W) | BlinkOn 50%!",
             "jockey": "Gonzalez E",
             "comment": "BLINKERS ON today — trainer Castro wins 50% with BlinkOn, one of the most powerful trainer angles in the DRF. Has run 71-69-76 last three at GP Tapeta, familiar with the track. Multiple 2nd and 3rd place finishes show she's competitive; the equipment change should push her over the top."},
            {"pp": 4, "name": "IT'S JUST A GAME",
             "beyer": "66-72-80 | Avg: 72.7",
             "trainer": "Cordero Eniel (0% W at GP)",
             "jockey": "Saez L",
             "comment": "Best recent Beyer trend (66-72-80 improving!) and ran 2nd last out at $12,500. Saez is a huge pickup from Rodriguez. Has run 12 times and clearly improving — the trend line is pointing up. Closing style suits the longer Tapeta route."},
            {"pp": 6, "name": "FURYS CHARM",
             "beyer": "55 (1 race) | Trainer Weaver 31% MdnClm",
             "trainer": "Weaver George (31% MdnClm!)",
             "jockey": "Gaffalione T",
             "comment": "Only one start but trainer Weaver wins 31% with maiden claimers — one of the best angles in the book. Gaffalione is the #1 jock at Gulfstream. Shipping from Palm Beach Downs with sharp recent works. First time routing from a sprint; Volatile sire gets distance. Big price for a horse with serious connections."},
        ]
    },
    {
        "num": 3, "post": "1:51 ET",
        "cond": "Maiden Claiming $35,000 | 3YO | 6 Furlongs Dirt",
        "note": "",
        "par": None,
        "picks": [
            {"pp": 7, "name": "EYES ON THE GROUND",
             "beyer": "76-83 | Avg: 79.5",
             "trainer": "Klesaris Steve (27% 61-180 Days!)",
             "jockey": "Maragh R",
             "comment": "Best back-to-back Beyers in the field (83-76) and finished 2nd in his last start at GP. Claimed last race and trainer Klesaris hits 27% with fresh claims — live angle. Fresh works at GP (4f :50.1, 4f :50.4). Closing style; has the best figures of experienced horses in this field."},
            {"pp": 1, "name": "SONIC SURGE",
             "beyer": "74-82 | Avg: 78.0",
             "trainer": "Weaver George (21% Sprint, 27% 1st Lasix)",
             "jockey": "Gaffalione T",
             "comment": "Posted 74 and 82 in two starts at Aqueduct. Adding Lasix today (trainer Weaver 27% with 1st Lasix). Gaffalione up is the best. Best-bred horse in the field (Maclean's Music $170k) dropping from $170k MSW company to $35k maiden claimer. Natural bounce-back off troubled trips."},
            {"pp": 3, "name": "CANDY ADDICTION",
             "beyer": "73-84-75 | Avg: 77.3",
             "trainer": "Sano Antonio (25% J/T with Ortiz Jr at GP!)",
             "jockey": "Ortiz I Jr",
             "comment": "Back-to-back Beyers of 73-84-75 with an 84 in a MOC50000C field. Ortiz Jr is the elite jockey and trainer Sano is 25% with him at GP. Sharp recent works (5f 1:01). Has GP experience and the figures say he belongs."},
        ]
    },
    {
        "num": 4, "post": "2:22 ET",
        "cond": "Claiming $8,000 N3L | 4yo+ | 5.5 Furlongs Tapeta",
        "note": "",
        "par": 75,
        "picks": [
            {"pp": 6, "name": "MACKOR",
             "beyer": "87-86-92 | Avg: 88.3",
             "trainer": "Hurtak Daniel C (7% W — patient)",
             "jockey": "Vasquez M A",
             "comment": "Best pure figures in the race (87-86-92 last three). Multiple wins on GP Tapeta sprints including a dominant 89-Beyer winner at this exact level. Has beaten $25k horses previously. Bumpd at start last two but still posted 87+. Hurtak's barn knows this horse cold."},
            {"pp": 3, "name": "RISK FACTOR",
             "beyer": "86-91-84 | Avg: 87.0",
             "trainer": "Dibona Robert S (22% Claim, 16% Return from Layoff)",
             "jockey": "Ocasio J",
             "comment": "Won the Clm 17500 at GP with an 88 Beyer and has back-class figures of 86-91. Multiple wins and hard-knocking performer who always runs honest. Dibona hits 22% with claimers. At $8k this is the best-performed horse in the field and should be right up front throughout."},
            {"pp": 7, "name": "RIPTON'S MUSIC",
             "beyer": "85-92-75 | Avg: 84.0",
             "trainer": "Arscott Garrett W (20% W, 18% Claim)",
             "jockey": "Martinez C",
             "comment": "Won a Clm 8000 last out at Castellano-supervised odds-on (85 Beyer), won his maiden with a 92 Beyer. Back at the winning level. Trainer Arscott is 20% and has shown confidence claiming him. The 92 maiden Beyer is the best figure any horse in this field has ever run."},
        ]
    },
    {
        "num": 5, "post": "2:52 ET",
        "cond": "Maiden Special Weight $84k | 3YO | 7.5 Furlongs Turf",
        "note": "",
        "par": 81,
        "picks": [
            {"pp": 8, "name": "ZAKINTHOS",
             "beyer": "88-82-65 | Avg: 78.3",
             "trainer": "Lynch Brian A (31% TurfSprints!)",
             "jockey": "Ortiz I Jr",
             "comment": "Has a turf Beyer of 88 in his last race — best among horses with figures. Trainer Lynch wins 31% with turf sprint horses, his best angle. Ortiz Jr is the best jockey in the race. The 88 figure in a competitive MSW field is strong; first-time around two turns which is the question, but connections are elite."},
            {"pp": 2, "name": "CANDIED UP",
             "beyer": "First Starter",
             "trainer": "Joseph S A Jr (14% 1st Start, 25% J/T w/ Gaffalione at GP!)",
             "jockey": "Gaffalione T",
             "comment": "Elite debut connections: Joseph Jr 14% with first starters and the GP J/T with Gaffalione is 25%. Bullet work (4f in :48.4) and well-bred ($95k Twirling Candy). Joseph typically sends turf maiden winners fresh. Can't ignore the connections in a field full of first-timers and lightly-raced horses."},
            {"pp": 7, "name": "HIGH LEVERAGE",
             "beyer": "75 (1 race)",
             "trainer": "D'Angelo Jose F (22% 2nd Starters!)",
             "jockey": "Saez L",
             "comment": "Posted a 75 Beyer in debut despite two bumps in the stretch. Trainer D'Angelo 22% with second starters — one of his best angles. Bullet work (4f in :45.0, 1st of 65) is elite. Saez up is the second-best jockey. Should improve significantly off that first effort."},
        ]
    },
    {
        "num": 6, "post": "3:22 ET",
        "cond": "Claiming $17,500 | 3YO | 1 Mile 70 Yards Tapeta",
        "note": "",
        "par": None,
        "picks": [
            {"pp": 4, "name": "VIN NUMBER",
             "beyer": "82-83-79 | Avg: 81.3",
             "trainer": "Mongeon Kathy P (7% W — new trainer after claim)",
             "jockey": "Gonzalez E",
             "comment": "Won last out with an 82 Beyer and ran 83 the race before that. Best recent back-to-form figures in this 3-year-old field. Front-running style controls the pace from the rail (PP 4). Was claimed to this barn — connections clearly see something. Consistent 79-82-83 trend is the best pattern here."},
            {"pp": 6, "name": "MAGNETO",
             "beyer": "80-74 | Avg: 77.0",
             "trainer": "Delgado Jorge (23% at GP, 29% Synth/Turf!)",
             "jockey": "Zayas E J",
             "comment": "Won last out gate-to-wire at this level (Md 17500) — second start off the bench, typically improves. Trainer Delgado hits 23% at GP and 29% with synthetic/turf transitions. Zayas is a massive upgrade. Two-start pattern of 74-80 shows improvement; horse is arriving at peak fitness."},
            {"pp": 1, "name": "DEEP STAR",
             "beyer": "73-76-70 | Avg: 73.0",
             "trainer": "D'Angelo Jose F (24% at GP, 20% Layoffs)",
             "jockey": "Saez L",
             "comment": "Won at this exact track, surface, and distance (1M 70Y Tapeta) going wire to wire. Trainer D'Angelo is 24% at GP and has 20% with layoff horses. Saez up is elite. Drops from OC32k to claiming $17,500 is a sharp class drop. Route specialist who should relish the distance."},
        ]
    },
    {
        "num": 7, "post": "3:52 ET",
        "cond": "Optional Claiming $25,000 / N1X | F&M 4yo+ | 7 Furlongs Dirt",
        "note": "",
        "par": 79,
        "picks": [
            {"pp": 7, "name": "COOEY",
             "beyer": "76-89-86 | Avg: 83.7",
             "trainer": "Joseph S A Jr (21% 61-180 Day!)",
             "jockey": "Gaffalione T",
             "comment": "Best figures in the field (89-86) with a dominant 89-Beyer win at GP 7F last year. Trainer Joseph Jr 21% with 61-180 day layoffs — his strongest angle for returns. Gaffalione up is the best jockey at GP. Works are sharp (4f :47.3, :48.3). Front-running speed from a good post; dominant form when she's right."},
            {"pp": 1, "name": "JUST A PHILLY",
             "beyer": "73-50-66 | Recent Win",
             "trainer": "Miller Herbert (16% Claim)",
             "jockey": "Gonzalez E",
             "comment": "Won her last start convincingly at this exact track and distance. Multiple wins at GP including a 77 career Beyer. Claimed back and trainer Miller has now won with her in this spot. Consistent performer who knows this strip; should lead from the inside."},
            {"pp": 6, "name": "HEARTBEAT",
             "beyer": "65-85 | Avg: 75.0",
             "trainer": "Lynch Brian A (22% Sprint, 13% Route/Sprint)",
             "jockey": "Rosario J",
             "comment": "Won at Churchill Downs impressively (85 Beyer) on a wet track — shown she can run big. Trainer Lynch 22% with sprint horses off layoff. First GP start but sharp works (5f 1:02, 5f 1:03 recent). First-time starters for Lynch off that caliber win get my attention. Legitimate if she translates."},
        ]
    },
    {
        "num": 8, "post": "4:24 ET",
        "cond": "Leinster Melody of Colors $125k Stakes | 3YO Fillies | 5F Turf",
        "note": "STAKES RACE",
        "par": None,
        "picks": [
            {"pp": 1, "name": "LENNILU",
             "beyer": "92-96-90 | Avg: 92.7",
             "trainer": "Biancone Patrick L (22% Turf, 20% Stakes)",
             "jockey": "Saez L",
             "comment": "The class of this field with back-to-back 96 and 90 Beyer wins at this exact track and distance. Won the Hollywood Beach Stakes and Royal Palm Juvenile Florida Bred here at GP. Competed in the BC Juvenile Turf Sprint (finished 7th but against the world's best). Saez has partnered with her for multiple wins — dominant."},
            {"pp": 4, "name": "MYSTICAL BELLE",
             "beyer": "91-90-88 | Avg: 89.7",
             "trainer": "Joseph S A Jr (6% 1st Turf — small concern)",
             "jockey": "Gaffalione T",
             "comment": "Won her last two starts with figures of 91 and 90 — only horse who can challenge Lennilu on pure numbers. Front-running style suits the 5F turf sprint. First-time turf is a question mark but the 91 Beyer on synthetic says the talent is there. Gaffalione/Joseph Jr pairing wins 25% together."},
            {"pp": 3, "name": "VIABLE ASSET",
             "beyer": "94-81-75 | Avg: 83.3",
             "trainer": "Abreu Fernando (12% Stakes)",
             "jockey": "Rosario J",
             "comment": "That 94 Beyer on debut turf is elite-level talent — won an OC35k allowance at GP last out. Rosario up is solid. The question is can she replicate the 94 against stakes horses, but the ceiling is very high. Must-use for trifecta tickets."},
        ]
    },
    {
        "num": 9, "post": "4:55 ET",
        "cond": "Starter OC $50k/SAL $35k | 4yo+ | 5.5 Furlongs Tapeta",
        "note": "",
        "par": None,
        "picks": [
            {"pp": 6, "name": "SOSUA SUMMER",
             "beyer": "89-92-91 | Avg: 90.7",
             "trainer": "Barboza V Jr (25% 2Off45-180!)",
             "jockey": "Saez L",
             "comment": "Won his last start at this exact condition (OC50k/SAL35k-N) with a 93 Beyer and posted 89-92-91 the last three. Trainer Barboza 25% with horses returning after brief layoffs. Saez up is a big jockey. Front-running style at 5.5F Tapeta is the ideal setup; won the race before here and comes back pointing perfectly."},
            {"pp": 7, "name": "SURF'S UP",
             "beyer": "95-90-89 | Avg: 91.3",
             "trainer": "Fawkes David (37% 1st Claim!)",
             "jockey": "Gaffalione T",
             "comment": "Won last out at 95 Beyer going wire-to-wire after being claimed. Trainer Fawkes wins 37% with first-time claims — one of the best stats in the DRF today. Gaffalione takes over; has a 31% J/T at GP with Fawkes. Fresh off the claim and clearly improving; the 95 Beyer is the best single-race figure in this race."},
            {"pp": 1, "name": "POULIN IN O T",
             "beyer": "88-90-96 | Avg: 91.3",
             "trainer": "Owens Steve (17% W)",
             "jockey": "Husbands M J",
             "comment": "Competed against N3X company at Woodbine posting 88-90-96 Beyers and won here at GP Tapeta with an 85 figure. Multiple elite Beyers in his career and Husbands knows him well. Dropping from N2X to starter optional condition — class relief. Dangerous in this field."},
        ]
    },
    {
        "num": 10, "post": "5:25 ET",
        "cond": "Maiden Special Weight $84k | F&M 3yo+ | 1 1/8 Miles Turf",
        "note": "",
        "par": 77,
        "picks": [
            {"pp": 4, "name": "PINCH OF BOURBON",
             "beyer": "87-91-70 | Avg: 82.7",
             "trainer": "Hennig Mark (13% 61-180 Day)",
             "jockey": "Zayas E J",
             "comment": "Best Beyer in this field — the 91 was a near-miss at Belmont in a very competitive $85k MSW. The second-place finish against quality Belmont stock says she absolutely belongs here. Zayas takes over as jockey; Hennig's barn shows sharp works (5f turf 1:01.0, bullet). First GP turf start for a filly with obvious talent."},
            {"pp": 2, "name": "ILLUMINATRICE",
             "beyer": "79-82-87 | Avg: 82.7",
             "trainer": "Engler Jeff (14% W, 15% Turf Routes)",
             "jockey": "Ortiz I Jr",
             "comment": "Three consecutive top-3 turf finishes (79-82-87 improving trend!) at multiple tracks. Bumped at the start last time at GP but still finished 2nd by a neck. Ortiz Jr is the best jockey in the race. Pattern of finishing 2nd multiple times suggests she's knocking on the door; this could be the day."},
            {"pp": 12, "name": "SNIPSNIPPITYSNIP",
             "beyer": "75-81-76 | Avg: 77.3",
             "trainer": "Walsh Brendan P (17% Turf Routes, 20% 31-60 Days!)",
             "jockey": "Saez L",
             "comment": "Seven turf starts with figures hovering 70-81, showed well at CD and Keeneland. Trainer Walsh hits 17% with turf routes and 20% off 31-60 day layoffs. Saez up is elite. Third-place MSW finish at CD shows she can compete; closing style suits the 1 1/8 mile turf at big odds."},
        ]
    },
]

def pp_badge(pp, size=14):
    bg = PP_COLORS.get(pp, colors.gray)
    fg = PP_TEXT.get(pp, colors.white)
    return bg, fg

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('title', parent=styles['Title'],
        fontSize=20, textColor=colors.HexColor('#1a1a2e'), spaceAfter=4)
    sub_style = ParagraphStyle('sub', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#666666'), spaceAfter=16, alignment=TA_CENTER)
    race_header_style = ParagraphStyle('race_header', parent=styles['Normal'],
        fontSize=13, fontName='Helvetica-Bold', textColor=colors.white, spaceAfter=0)
    cond_style = ParagraphStyle('cond', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#444444'), spaceAfter=4)
    pick_name_style = ParagraphStyle('pick_name', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a1a2e'))
    pick_beyer_style = ParagraphStyle('pick_beyer', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#2c5f2e'), fontName='Helvetica-Bold')
    trainer_style = ParagraphStyle('trainer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#555555'))
    comment_style = ParagraphStyle('comment', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#333333'), leading=13)
    note_style = ParagraphStyle('note', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#cc4400'), fontName='Helvetica-Oblique')
    footer_style = ParagraphStyle('footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER)

    story = []

    # Title
    story.append(Paragraph("🏇 Gulfstream Park – March 22, 2026", title_style))
    story.append(Paragraph("Charlie's Top-3 Picks | Methodology: Beyers + Form + Class + Angles", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 10))

    pick_labels = ["🥇 WIN", "🥈 PLACE", "🥉 SHOW"]
    label_colors = [colors.HexColor('#FFD700'), colors.HexColor('#C0C0C0'), colors.HexColor('#CD7F32')]

    for race in RACES:
        # Race header
        header_data = [[Paragraph(f"RACE {race['num']}  |  Post: {race['post']}  |  Par: {race['par'] if race['par'] else 'N/A'}", race_header_style)]]
        header_table = Table(header_data, colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(header_table)
        story.append(Paragraph(race['cond'], cond_style))
        if race.get('note'):
            story.append(Paragraph(f"⚠️ {race['note']}", note_style))

        # Each pick
        for i, pick in enumerate(race['picks']):
            pp = pick['pp']
            bg_col, fg_col = pp_badge(pp)
            label = pick_labels[i]
            lc = label_colors[i]
            
            # PP badge cell
            pp_text = f"#{pp}" if pp else "??"
            fg_hex = pp_text_hex(pp)
            
            pick_data = [
                [
                    Paragraph(f"<b><font color='{fg_hex}'>{pp_text}</font></b>", ParagraphStyle('pp', fontSize=13, fontName='Helvetica-Bold', alignment=TA_CENTER)),
                    Paragraph(f"{label}  <b>{pick['name']}</b>", ParagraphStyle('nm', fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#1a1a2e'))),
                ],
                [
                    "",
                    Paragraph(f"📊 {pick['beyer']}", pick_beyer_style),
                ],
                [
                    "",
                    Paragraph(f"🎽 {pick['trainer']}  |  👤 {pick['jockey']}", trainer_style),
                ],
                [
                    "",
                    Paragraph(pick['comment'], comment_style),
                ],
            ]
            
            t = Table(pick_data, colWidths=[0.55*inch, 6.95*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), bg_col),
                ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#F8F9FA')),
                ('SPAN', (0,0), (0,-1)),
                ('VALIGN', (0,0), (0,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),
                ('TOPPADDING', (1,0), (1,0), 8),
                ('BOTTOMPADDING', (1,-1), (1,-1), 8),
                ('LEFTPADDING', (1,0), (1,-1), 8),
                ('RIGHTPADDING', (1,0), (1,-1), 8),
                ('TOPPADDING', (0,0), (0,-1), 0),
                ('BOTTOMPADDING', (0,0), (0,-1), 0),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#DDDDDD')),
                ('BOX', (0,0), (0,-1), 1.5, colors.HexColor('#888888') if bg_col in [colors.white, colors.HexColor('#F5E642')] else bg_col),
                ('LINEABOVE', (1,1), (1,1), 0.5, colors.HexColor('#EEEEEE')),
                ('LINEABOVE', (1,2), (1,2), 0.5, colors.HexColor('#EEEEEE')),
                ('LINEABOVE', (1,3), (1,3), 0.5, colors.HexColor('#EEEEEE')),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 10))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC')))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by Charlie | {datetime.date.today().strftime('%B %d, %Y')} | "
        "Picks based on DRF past performances, Beyer figures, class, trainer/jockey angles. For entertainment only.",
        footer_style
    ))

    doc.build(story)
    print(f"PDF created: {output_path}")

if __name__ == "__main__":
    build_pdf("GP_Picks_Mar22_2026.pdf")
