#!/usr/bin/env python3
"""Generate GP Picks PDF for March 7, 2026"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import KeepTogether

# DRF Post Position Colors
PP_COLORS = {
    1: colors.HexColor('#CC0000'),    # Red
    2: colors.HexColor('#CCCCCC'),    # White/Light gray for visibility
    3: colors.HexColor('#0000CC'),    # Blue
    4: colors.HexColor('#CCCC00'),    # Yellow
    5: colors.HexColor('#009900'),    # Green
    6: colors.HexColor('#222222'),    # Black
    7: colors.HexColor('#FF6600'),    # Orange
    8: colors.HexColor('#FF69B4'),    # Pink
    9: colors.HexColor('#00AAAA'),    # Turquoise
    10: colors.HexColor('#660099'),   # Purple
    11: colors.HexColor('#888888'),   # Gray
    12: colors.HexColor('#88AA00'),   # Lime Green
    13: colors.HexColor('#CC9966'),   # Buff/Tan
    14: colors.HexColor('#336600'),   # Forest Green
}

PP_TEXT_COLORS = {
    1: colors.white, 2: colors.black, 3: colors.white,
    4: colors.black, 5: colors.white, 6: colors.white,
    7: colors.white, 8: colors.black, 9: colors.white,
    10: colors.white, 11: colors.white, 12: colors.black,
    13: colors.black, 14: colors.white,
}

RACES = [
    {
        "num": 1, "post": "12:20 PM ET",
        "desc": "1 Mile (Turf) | Maiden Special Weight $84,000 | 3yo Fillies",
        "notes": "Scratched: #7 Together Again, #9 Dutch Girl, #11 Horsing Around, #12 Classic Move, #13 Pan Pan",
        "picks": [
            {"rank":1,"pp":2,"name":"RULES AND REGS","trainer":"Wilkes / Lanerie","ml":"2-1",
             "beyers":"75","avg":"75.0",
             "comment":"Best Beyer in the field from her only start. Wilkes/Lanerie is a sharp pairing and this filly projects to improve — an improving second-starter that could dominate this softened field."},
            {"rank":2,"pp":4,"name":"DANCE CLASS","trainer":"Mott / Kingsley","ml":"5-2",
             "beyers":"First Start","avg":"N/A",
             "comment":"First start for Bill Mott, one of the best turf conditioners in the country. Debut turf fillies from this barn are dangerous, and Kingsley gives her a live shot to fire fresh."},
            {"rank":3,"pp":3,"name":"FLETCH'S ROCKETTE","trainer":"Mott / Vasquez","ml":"4-1",
             "beyers":"58, 66","avg":"62.0",
             "comment":"Improving from 58 to 66 in two starts shows she's learning the game. Second Mott runner brings stable depth; her turf experience could trump the debut horses in the stretch."},
        ]
    },
    {
        "num": 2, "post": "12:50 PM ET",
        "desc": "1 1/8 Miles (Dirt) | Maiden Claiming $12,500 | 3yo & Up",
        "notes": "Full field — no scratches",
        "picks": [
            {"rank":1,"pp":7,"name":"MAGIC RED","trainer":"Joseph / Zayas","ml":"9-5",
             "beyers":"—","avg":"—",
             "comment":"Morning-line favorite for the powerful Saffie Joseph barn; Zayas is tops locally and this horse figures to be the class of a soft maiden claimer field. Trust the barn here."},
            {"rank":2,"pp":4,"name":"DOMINICAN PIRATE","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Second choice with enough early pace to be competitive on the front end; use in exacta/trifecta tickets underneath Magic Red at a better price."},
            {"rank":3,"pp":6,"name":"OLD MARSH","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Third choice offers fair value in a thin maiden claimer. Keep him in trifecta plays as a closer if the pace heats up early."},
        ]
    },
    {
        "num": 3, "post": "1:22 PM ET",
        "desc": "6 Furlongs (Dirt) | AOC $20,000/N1X | F&M 4yo+",
        "notes": "Full field — no scratches",
        "picks": [
            {"rank":1,"pp":2,"name":"VUELA PALOMA","trainer":"—","ml":"5-2",
             "beyers":"Competitive local","avg":"—",
             "comment":"Morning-line 5-2 that has been competitive in tougher spots. The class drop to this level at a sprint suits her pace-pressing style — she should be close throughout and last."},
            {"rank":2,"pp":4,"name":"FOGGY NOTE","trainer":"—","ml":"7-2",
             "beyers":"Competitive local","avg":"—",
             "comment":"Second on the ML at 7-2 has class-appropriate figures and could outrun her price if the pace sets up for closers. Solid alternative to the favorite in all exotics."},
            {"rank":3,"pp":1,"name":"WHATINTHELITERAL","trainer":"—","ml":"—",
             "beyers":"Veteran","avg":"—",
             "comment":"Local veteran knows the track conditions and is capable of a big effort when spotted correctly by connections. Use on the bottom of trifectas at fair odds."},
        ]
    },
    {
        "num": 4, "post": "1:52 PM ET",
        "desc": "1 1/8 Miles (Tapeta) | Maiden Claiming $17,500 | 3yo",
        "notes": "Full field — no scratches",
        "picks": [
            {"rank":1,"pp":2,"name":"BE WISER BOB","trainer":"—","ml":"2-1",
             "beyers":"—","avg":"—",
             "comment":"Odds-on morning-line choice in a soft 3yo maiden claimer on the Tapeta. Projects to control the pace around this route trip — the 2-1 is fair for a horse that fits the spot ideally."},
            {"rank":2,"pp":5,"name":"DAVID'S KITTEN","trainer":"—","ml":"3-1",
             "beyers":"—","avg":"—",
             "comment":"Second on the morning line at 3-1 and a legitimate alternative. Has early speed to engage the favorite throughout and could benefit if Be Wiser Bob is pressured into a hot pace."},
            {"rank":3,"pp":1,"name":"IMPONENTE","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Best of the rest in a race where the top two are expected to duel. Worth a small exotic play at a price if the field compresses post-scratch."},
        ]
    },
    {
        "num": 5, "post": "2:21 PM ET",
        "desc": "5 Furlongs (Turf) | Starter Optional Claiming $50,000 | 4yo+",
        "notes": "Scratched: #4 Louie the Sun King, #5 Fluid Situation, #9 Beeline, #10 Warrior's Pride, #11 Poulin in O T",
        "picks": [
            {"rank":1,"pp":6,"name":"SPEED FIGURES","trainer":"—","ml":"9-5",
             "beyers":"—","avg":"—",
             "comment":"Heavily favored at 9-5 after heavy scratching reduced the field. Suits turf sprint conditions and has been consistent in this company — the ML odds reflect real talent. Trust the top choice."},
            {"rank":2,"pp":3,"name":"ACT A FOOL","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Can press the pace in a short turf sprint and is capable of lasting if Speed Figures gets pressured. Use him to complete exacta/trifecta combinations with the favorite."},
            {"rank":3,"pp":1,"name":"CLASSY WAR","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Third choice in a compact 6-horse field after scratches; stalks the pace and benefits from front-end pressure. Keep in trifecta plays as a come-from-behind type."},
        ]
    },
    {
        "num": 6, "post": "2:51 PM ET",
        "desc": "1 1/8 Miles (Tapeta) | Claiming $8,000 (N3L) | 4yo+",
        "notes": "Full field — no scratches",
        "picks": [
            {"rank":1,"pp":4,"name":"LAS OLAS","trainer":"—","ml":"3-1",
             "beyers":"—","avg":"—",
             "comment":"Morning-line co-favorite at 3-1 in a low-level claimer where class wins. This Tapeta distance suits an experienced horse that can relax early and apply steady pressure in the stretch."},
            {"rank":2,"pp":7,"name":"WARRIOR WAYNE","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Second choice that runs efficient pace fractions; with a fair setup he has every opportunity to last and could surprise the favorite if Las Olas does not get a clean setup."},
            {"rank":3,"pp":1,"name":"SECRET BAGENT MAN","trainer":"—","ml":"—",
             "beyers":"—","avg":"—",
             "comment":"Long-time Tapeta local knows this surface better than most. Use on the bottom of trifectas — he's capable of a big effort at a price if the pace collapses in front of him."},
        ]
    },
    {
        "num": 7, "post": "3:21 PM ET",
        "desc": "5 Furlongs (Turf) | Silks Run Stakes (Listed) $125,000 | 3yo+",
        "notes": "Full field — no scratches",
        "picks": [
            {"rank":1,"pp":3,"name":"LITIGATION","trainer":"—","ml":"6-5",
             "beyers":"Dominant last win","avg":"—",
             "comment":"Last-out winner by a wide margin enters as the 6-5 betting favorite. Dominated this company recently and the form is real — there is no compelling reason to fade a horse this sharp coming back in the same condition."},
            {"rank":2,"pp":1,"name":"REZASROLEX","trainer":"—","ml":"8-5",
             "beyers":"Dominant record","avg":"—",
             "comment":"The other main contender at 8-5 brings an impressive recent record and will likely battle Litigation for supremacy. These two are head and shoulders above the field in a race that figures as a two-horse battle."},
            {"rank":3,"pp":4,"name":"COPPOLA","trainer":"—","ml":"6-1",
             "beyers":"Multiple stakes wins","avg":"—",
             "comment":"Multiple stakes winner at 6-1 is the clear best of the rest. If Litigation and Rezasrolex duel hard, Coppola has the tactical speed to rally past tiring rivals and deliver strong trifecta value."},
        ]
    },
    {
        "num": 8, "post": "4:21 PM ET",
        "desc": "5 Furlongs (Tapeta) | Claiming $10,000 (N3L) | F&M 4yo+",
        "notes": "Scratched: #6 Chloe's Toy",
        "picks": [
            {"rank":1,"pp":7,"name":"MISPRINT","trainer":"Simms / Maragh","ml":"4-1",
             "beyers":"75, 69, 60","avg":"68.0",
             "comment":"Best 3-race Beyer average in the field at 68.0 — wired the field two back with a dominant 75 in this exact condition. She drops back into the right spot and her natural speed should prove the class edge at this price."},
            {"rank":2,"pp":5,"name":"PLUM IRISH","trainer":"David / Vasquez","ml":"6-1",
             "beyers":"64, 50, 44","avg":"52.7",
             "comment":"Won her last start (Beyer 64) in sharp fashion for trainer Carlos David (25% win rate locally). The step up in company is manageable given consecutive winning form and Vasquez is a strong booking."},
            {"rank":3,"pp":2,"name":"ANY MOMENT","trainer":"Cazares / Zayas","ml":"6-1",
             "beyers":"73, 48, 38","avg":"53.0",
             "comment":"Posted a sharp 73 Beyer two starts back when she won wire-to-wire. Two subsequent poor performances are excusable (claimed + surface switch) — back on the Tapeta she could bounce back sharply."},
        ]
    },
    {
        "num": 9, "post": "4:52 PM ET",
        "desc": "1 1/8 Miles (Tapeta) | Handicap $100,000 | F&M 3yo+",
        "notes": "Full field — no scratches",
        "picks": [
            {"rank":1,"pp":1,"name":"FANTASY PERFORMER","trainer":"Gambolati / Egan","ml":"10-1",
             "beyers":"83, 74, 81","avg":"79.3",
             "comment":"Won this EXACT race (GP Hcp, Tapeta, 1-1/8M) on February 1st with a Beyer 83. Getting 10-1 on a proven winner returning to repeat conditions is extraordinary value — she's tailor-made for today."},
            {"rank":2,"pp":2,"name":"MISS MARY NELL","trainer":"David / Bravo","ml":"27-2",
             "beyers":"83, 78, 76","avg":"79.0",
             "comment":"Won this same Handicap on February 24th defeating Fantasy Performer with a Beyer 83. Carlos David is on a heater (25% win rate) and both horses deserve top respect — this is a repeat of the Feb 24 exacta."},
            {"rank":3,"pp":7,"name":"CHARLIE'S WISH","trainer":"Fawkes / Gutierrez M","ml":"73-1",
             "beyers":"83, 85, 69","avg":"79.0",
             "comment":"Ran second in the February 1st edition of this race (Beyer 83) behind Fantasy Performer. Proven on this surface and condition, she's a staggering overlay — use in exotics for incredible value."},
        ]
    },
    {
        "num": 10, "post": "5:23 PM ET",
        "desc": "1 Mile (Turf) | AOC $75,000/N1X | 3yo Fillies",
        "notes": "Scratched: #13 Dandona, #14 Pure Eloquence",
        "picks": [
            {"rank":1,"pp":4,"name":"CALL THE BULLPEN","trainer":"David / Ortiz I Jr","ml":"8-1",
             "beyers":"68, 67, 53","avg":"62.7",
             "comment":"Two consecutive turf wins at Gulfstream (Beyers 67 and 68) — she absolutely loves this course. Top trainer Carlos David + Irad Ortiz Jr on a horse proven at 1M turf here in repeat conditions is a power angle."},
            {"rank":2,"pp":9,"name":"KENTUCKY BELLE","trainer":"Cox / Zayas","ml":"6-1",
             "beyers":"64, 65, 66","avg":"65.0",
             "comment":"Won on turf at Churchill Downs (Beyer 64) for Brad Cox who wins 30% of starts here. First-time Lasix is a 34% win stat for Cox — that's a legitimate angle at a price worth using in all wagers."},
            {"rank":3,"pp":1,"name":"DUNMORE BEACH","trainer":"Carroll / Moran","ml":"15-1",
             "beyers":"67, 56, 59","avg":"60.7",
             "comment":"Won a turf route at Woodbine (Beyer 67) in similar class. Josie Carroll prepares shippers well and Moran is underrated — she's a live longshot at 15-1 if she fires first-out at this course."},
        ]
    },
    {
        "num": 11, "post": "5:52 PM ET",
        "desc": "6 1/2 Furlongs (Dirt) | Hurricane Bertie Stakes (Grade III) $175,000 | F&M 4yo+",
        "notes": "Scratched: #2 Taliesin",
        "picks": [
            {"rank":1,"pp":5,"name":"R DISASTER","trainer":"Joseph / Husbands","ml":"9-5",
             "beyers":"90, 95, 90","avg":"91.7",
             "comment":"Best 3-race Beyer average in the field at an elite 91.7 — won the Gallant Bloom G2 with a 95 Beyer and has been consistently around 90 in graded company. Saffie Joseph is dominant locally — this is the horse to beat."},
            {"rank":2,"pp":4,"name":"STERLING SILVER","trainer":"Margotta / Maragh","ml":"2-1",
             "beyers":"95, 87, 95","avg":"92.3",
             "comment":"Life earnings of $1.365 million with a career-best 95 Beyer when winning the Iroquois Stakes G2. The betting favorite ran a gutsy second last time in this same race — she's proven here and always competitive."},
            {"rank":3,"pp":3,"name":"BEYOND BELIEF","trainer":"Breen / Bravo","ml":"10-1",
             "beyers":"92, 74, 85","avg":"83.7",
             "comment":"Posted a brilliant 92 Beyer when she wired the field in December — that figure is Grade-quality and good enough to compete here today. At 10-1 she represents a massive overlay if she repeats anywhere near that peak."},
        ]
    },
    {
        "num": 12, "post": "6:21 PM ET",
        "desc": "1 5/8 Miles (Turf) | AOC $35,000/N1X | 4yo+",
        "notes": "Scratched: #6 Side Street, #12 Mortal Lock",
        "picks": [
            {"rank":1,"pp":10,"name":"JUST FOR LUCK","trainer":"Dutrow / Zayas","ml":"6-1",
             "beyers":"82, 76, 77","avg":"78.3",
             "comment":"Won his last start at GP on turf (Beyer 82) going 1 mile — stretching to 1-5/8M on turf is a logical progression for this late-running style. Zayas takes the call and Dutrow has him primed to repeat."},
            {"rank":2,"pp":4,"name":"SPY NOVEL","trainer":"Ramsey / Maragh","ml":"15-1",
             "beyers":"80, 84, 80","avg":"81.3",
             "comment":"Won at Gulfstream on this turf earlier in the meet (Beyer 84) and posts a consistent 80-level Beyer pattern. He clearly fits locally and is a massive 15-1 overlay — a top-value play in all exotics."},
            {"rank":3,"pp":3,"name":"PIERRE","trainer":"Attard / Castellano","ml":"36-1",
             "beyers":"83, 80, 85","avg":"82.7",
             "comment":"Best 3-race Beyer average among the turf route specialists at 82.7. Won a turf marathon in Canada and ran third here last out — Castellano would not ride a 36-1 shot without believing he belongs. Trifecta dart."},
        ]
    },
]

def make_pp_badge(pp):
    return PP_COLORS.get(pp, colors.gray), PP_TEXT_COLORS.get(pp, colors.white)

def build_pdf(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('title', parent=styles['Title'],
        fontSize=18, textColor=colors.HexColor('#003366'),
        spaceAfter=2, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'],
        fontSize=9.5, textColor=colors.HexColor('#003366'),
        spaceAfter=1, alignment=TA_CENTER)
    race_hdr_style = ParagraphStyle('racehdr', parent=styles['Normal'],
        fontSize=11.5, textColor=colors.white, fontName='Helvetica-Bold',
        spaceAfter=0, alignment=TA_LEFT)
    horse_style = ParagraphStyle('horse', parent=styles['Normal'],
        fontSize=10.5, fontName='Helvetica-Bold', textColor=colors.HexColor('#003366'))
    detail_style = ParagraphStyle('detail', parent=styles['Normal'],
        fontSize=7.5, textColor=colors.HexColor('#555555'))
    comment_style = ParagraphStyle('comment', parent=styles['Normal'],
        fontSize=8.5, textColor=colors.HexColor('#222222'), leading=11)
    note_style = ParagraphStyle('note', parent=styles['Normal'],
        fontSize=7.5, textColor=colors.HexColor('#880000'), fontName='Helvetica-Oblique')

    rank_colors_bg = {
        1: colors.HexColor('#B8860B'),  # dark gold
        2: colors.HexColor('#888888'),  # silver
        3: colors.HexColor('#8B4513'),  # bronze
    }
    rank_labels = {1: '#1 PICK', 2: '#2 PICK', 3: '#3 PICK'}

    story = []

    story.append(Paragraph("GULFSTREAM PARK — TOP 3 PICKS", title_style))
    story.append(Paragraph("Saturday, March 7, 2026   |   Charlie's Handicapping Analysis", subtitle_style))
    story.append(Paragraph("Scratches confirmed via TrackData.live   |   Beyer Speed Figures from DRF Past Performances", subtitle_style))
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#003366'), spaceBefore=4, spaceAfter=6))

    for race in RACES:
        block = []

        hdr = [[Paragraph(f"RACE {race['num']}   {race['post']}   {race['desc']}", race_hdr_style)]]
        hdr_tbl = Table(hdr, colWidths=[7.5*inch])
        hdr_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#003366')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        block.append(hdr_tbl)
        block.append(Spacer(1, 2))

        if race['notes']:
            block.append(Paragraph("SCRATCH: " + race['notes'], note_style))
            block.append(Spacer(1, 3))

        for p in race['picks']:
            pp = p['pp']
            bg, fg = make_pp_badge(pp)
            rbg = rank_colors_bg[p['rank']]

            pp_para = Paragraph(f"<b>#{pp}</b>", ParagraphStyle('pp', fontSize=12,
                fontName='Helvetica-Bold', textColor=fg, alignment=TA_CENTER))
            rank_para = Paragraph(f"<b>{rank_labels[p['rank']]}</b>", ParagraphStyle('rk', fontSize=7,
                fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER))
            horse_para = Paragraph(p['name'], horse_style)
            detail_para = Paragraph(
                f"Trainer: {p['trainer']}  |  ML: {p['ml']}  |  Last 3 Beyers: {p['beyers']}  |  3-Race Avg: {p['avg']}",
                detail_style)
            comment_para = Paragraph(p['comment'], comment_style)

            row_bg = colors.HexColor('#FFFEF0') if p['rank'] == 1 else colors.white

            pt = Table([
                [pp_para, rank_para, horse_para],
                ['', '', detail_para],
                ['', '', comment_para],
            ], colWidths=[0.42*inch, 0.62*inch, 6.46*inch])
            pt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,-1), bg),
                ('BACKGROUND', (1,0), (1,0), rbg),
                ('BACKGROUND', (2,0), (2,-1), row_bg),
                ('SPAN', (0,0), (0,-1)),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (0,-1), 2),
                ('LEFTPADDING', (2,0), (2,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#CCCCCC')),
                ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#999999')),
            ]))
            block.append(pt)
            block.append(Spacer(1, 2))

        block.append(Spacer(1, 6))
        story.append(KeepTogether(block))

    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#003366'), spaceBefore=4))
    story.append(Paragraph(
        "Analysis by Charlie (AI Handicapper) | For entertainment purposes only | Bet responsibly | "
        "Data: DRF & TrackData.live | Generated March 7, 2026",
        ParagraphStyle('footer', parent=styles['Normal'],
            fontSize=7, textColor=colors.gray, alignment=TA_CENTER)))

    doc.build(story)
    print(f"PDF created: {output_path}")

if __name__ == '__main__':
    build_pdf('/tmp/gp_picks_mar7_2026.pdf')
