from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

doc = SimpleDocTemplate('GP-Picks-Mar20-2026.pdf', pagesize=letter,
    rightMargin=0.6*inch, leftMargin=0.6*inch, topMargin=0.7*inch, bottomMargin=0.7*inch)

styles = getSampleStyleSheet()

pp_colors = {
    1: colors.HexColor('#FF0000'),
    2: colors.HexColor('#FFFFFF'),
    3: colors.HexColor('#0000FF'),
    4: colors.HexColor('#FFD700'),
    5: colors.HexColor('#00AA00'),
    6: colors.HexColor('#000000'),
    7: colors.HexColor('#FF8C00'),
    8: colors.HexColor('#FF69B4'),
    9: colors.HexColor('#00CED1'),
    10: colors.HexColor('#8B0000'),
}
pp_text_colors = {
    1: colors.white, 2: colors.black, 3: colors.white, 4: colors.black,
    5: colors.white, 6: colors.white, 7: colors.white, 8: colors.black,
    9: colors.black, 10: colors.white,
}

title_style = ParagraphStyle('title', parent=styles['Title'], fontSize=18, spaceAfter=4, alignment=TA_CENTER)
subtitle_style = ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=9, spaceAfter=8, alignment=TA_CENTER, textColor=colors.grey)
race_header_style = ParagraphStyle('race_header', parent=styles['Heading2'], fontSize=13, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor('#1a1a2e'))
footer_style = ParagraphStyle('footer', parent=styles['Normal'], fontSize=7, textColor=colors.grey, alignment=TA_CENTER)

story = []
story.append(Paragraph('GULFSTREAM PARK - TOP 3 PICKS', title_style))
story.append(Paragraph('Friday, March 20, 2026 | All Turf Races Run on Tapeta', subtitle_style))

scratch_text = ('SCRATCHES: R2 #4 Citizen K | R4 #1 City Minute | R4 #6 Victoriously | R4 #8 Humor Me Brother | '
                'R7 #9 Brat Girl | R8 #7 Scootaloo | R9 #1 Kazooza | R10 #7 Social Triumph | R10 #8 Evelyn Louise')
story.append(Paragraph(scratch_text, ParagraphStyle('sc', parent=styles['Normal'], fontSize=7.5,
    spaceAfter=8, textColor=colors.HexColor('#AA0000'))))
story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#cccccc')))
story.append(Spacer(1, 6))

races = [
    (1, '1 Mile Dirt | Maiden Claiming $12,500 | 3YO | Post 12:50 PM', [
        (1, 7, 'WITCHA WISH', 'Beyers: 52/46/39 | Avg 45.7',
         'Drops from $25k MCL to $12.5k with class relief. Has a 52 Beyer dirt win and 46 Beyer 2nd at this level. Irad Ortiz Jr (26% win) and trainer Ramirez (30% dirt) are the best connections on board. 31-60 Days angle at 20%. Lone top horse on figures and connections.'),
        (2, 6, 'ONE BID', 'Beyers: 48/43/38 | Avg 43.0',
         'Steadily improving route runner with figures progressing 38 to 43 to 48. Showed up 3rd in best effort after being bumped at the start. Hills trainer 19% Mdn Clm. Two sharp works (4F :47.2 and :47.1). Legitimate contender.'),
        (3, 5, 'TYBEE ECHO', 'Beyers: 54/53/54 (turf) | Avg 53.7',
         'Best overall figures in race (54 Beyers x3) switching to dirt today. Trainer Spatz hits 19% on turf/dirt switches. Vasquez up. Three consecutive competitive turf efforts. Surface switch is the question but figures say he belongs.'),
    ]),
    (2, '1 Mile Tapeta (off turf) | Claiming $35,000 | 4YO+ NW3 | Post 1:20 PM | SCRATCH: #4 Citizen K', [
        (1, 6, 'MISTER ABARRIO', 'Beyers: 78/79/85 | Avg 80.7',
         'Best Beyer average in the field. Career-best 87 on synth, consistent 78-85 recently. Saffie Joseph Jr barn (19% win, 25% claiming). Husbands aboard. Lifetime 36-6-7-11, proven at GP synthetic. Class dropper from OC50k to Clm35k - motivated spot.'),
        (2, 5, 'BAKERS STREET', 'Beyers: 72/71/76 | Avg 73.0',
         'Two Tapeta starts in 2026 (Beyers 71 and 76) - proven he handles the surface. Close 2nd last out on Tapeta (4-wide, bid). Irad Ortiz Jr up - biggest rider upgrade in the barn. Sano trainer. Best surface match of 2026 for this horse.'),
        (3, 2, 'JUNCTION ROAD', 'Career Synth Beyer: 87 | Best field',
         'Best career synthetic figure (87) among the field. Deep closer with late punch. Has run into traffic repeatedly in recent starts - step up to Tapeta where he can close wide. Crichton trainer 27% win rate. Pattern points to a forward move.'),
    ]),
    (3, '6.5 Furlongs Dirt | Claiming $8,000 | 4YO+ NW3 | Post 1:51 PM', [
        (1, 4, 'PRINCE DAVID', 'Beyers: 68 win last out | Career best',
         'WON his last start at this exact class and distance (6.5F $8k, Beyer 68) - career-best figure. Palmer trainer 21% win rate. Has improved dramatically in 2026 after struggling in routes. Circles back to sprint where he is proven. Best recent Beyer in the race.'),
        (2, 2, 'FIGHTING WORDS', 'Beyers: 47/67/56 | Avg 56.7',
         'Most experience at this level, has won here before (66 Beyer). Showed sharp 67 Beyer two starts back, dipped slightly last out but showed pace. Cornejo trainer 18% at GP. Speed horse in a race that could set up for him.'),
        (3, 3, 'DOGWOOD CROSSING', 'Beyers: 40/51/68 | Avg 53.0',
         'Added BLINKERS ON today - equipment change. Won this exact level in Dec (68 Beyer), came back flat but equipment change can spark a forward move. Tomlinson 21% trainer, Ortiz Jr rides - jockey switch from recent B-riders is significant.'),
    ]),
    (4, '7.5F Tapeta (off turf) | AOC $20k NW1X | State Bred Fillies 4YO+ | Post 2:25 PM | SCRATCHES: #1 #6 #8', [
        (1, 3, 'I LOVE VENEZUELA', 'Beyers: 68/63/84 (synth) | Avg 71.7',
         'Dominant on synthetic - 16 synth starts, 4 wins (best Beyer 84). With turf off and on Tapeta, this is her best surface. Recent poor efforts were on DIRT - not her surface. Coy trainer 21% in 2025. Gonzalez aboard. Class dropper from OC20k to this spot.'),
        (2, 7, 'SAPPHIRE GIRL', 'Beyers: 70/76/70 | Avg 72.0',
         'Best recent Beyer avg in reduced field (72.0). Won at GP on turf (70 Beyer), consistent 70-76 range. Saffie Jr (19%) and Irad Ortiz Jr - deepest connections in race. First Tapeta start is the only question. Turf speed figures translate to synthetic.'),
        (3, 5, "NINA'S LAST GIFT", 'Beyers: 77/73/76 | Avg 75.3',
         'Best raw figures in the field (77 Beyer last out on turf, 2nd at this exact class). Likes to set pace - if she controls the flow she is dangerous. Turf form translates as pace-setter. Ubide trainer. Vasquez up. Danger if she steals the lead.'),
    ]),
    (5, '1.5 Miles Dirt | Maiden Special Weight $84k | 3YO+ | Post 2:58 PM', [
        (1, 3, 'STOMPIN GRAPES', 'Beyers: 76/75/80 | Avg 77.0',
         'Best Beyer average in the race at 77.0 - three consecutive figures of 75-76-80 show consistency. Multiple 3rds in competitive MSW fields, improving. Wilkes trainer 15% (29% 31-60 days). Zayas aboard (18%). 5-year-old now eligible, has been knocking on the door.'),
        (2, 1, 'MAKE MY DAY', 'Beyer: 73 debut 3rd | 2nd start spot',
         'Pletcher trains and hits 22% in Mdn 2nd-start spot - his best angle. Bullet works: 4F :49.0 (1/16) and 5F 1:01.0 (1/6). Third in debut (73 Beyer). Saez up. Gun Runner colt purchased for $1.1M - connections invest for reasons. Class of the field on pedigree.'),
        (3, 6, 'EZ ORB NOT', 'Beyer: 62 debut 3rd | 2nd start spot',
         'Orseno hits 31% in Mdn 2nd-start angle - best trainer stat in this race. Sharp Tapeta works. Showed 4-wide late kick to grab 3rd in debut (62 Beyer). Gaffalione aboard (16%). Second-start improvement is the story here.'),
    ]),
    (6, '6 Furlongs Dirt | Allowance NW1X | State Bred Fillies 3YO | Post 3:31 PM', [
        (1, 4, 'JESTINA', 'Beyers: 66/60/43 | Avg 56.3',
         'Second in THIS EXACT race last start (Beyer 66, career best). Won the Moc $50k race before that (60 Beyer). Clear forward trajectory (43 to 60 to 66). Saffie Jr (19%) and Husbands - strongest connections in the field. 2Off45-180 angle at 22%. Ready to take the next step.'),
        (2, 6, 'WINPLACEANDSHOW', 'Beyers: 59/73/41 | Avg 57.7',
         'Won at Moc50k level (73 Beyer career best) - proven can fire a big figure at this level. Last out (59) went wide early, legitimate excuse. Orseno (16%), Gaffalione (16%). 2-1 morning line favorite. Bounce-back spot after excusable last effort.'),
        (3, 3, 'LOVE LIKE LUCY', 'Beyers: 63/48/57 | Avg 56.0',
         'Highest-class horse in the field - has run in FSS stakes races. Saffie Jr and Gaffalione combo (28% J/T at GP). Shows up with a win and multiple seconds in tougher spots. Dropping to NW1X allowance for class relief. 5/2 ML reflects class edge.'),
    ]),
    (7, '1.5 Miles Tapeta | SOC $17,500 | Fillies 3YO NW1X | Post 4:07 PM | SCRATCH: #9 Brat Girl', [
        (1, 6, 'NOCHE DE DAMAS', 'Beyers: 62/53/45 | Avg 53.3',
         'Best trajectory in the field - improving every start (45 to 53 to 62). Close 2nd in OC35k on synthetic last out (62 Beyer). Won Md$25k on synth earlier. Tharrenos trainer 12% (17% 31-60 days). IRAD ORTIZ JR aboard - massive jockey upgrade. Best late pace rating (86) in race.'),
        (2, 8, 'STELLA BIONDA', 'Beyers: 64/48/39 | Avg 50.3',
         'Career-best figure last out (64 Beyer, close 2nd). Improving sharply on this surface type. D Angelo trainer 21% routes on synth. Torres Y aboard. Best raw single Beyer among contenders at 64. Won at this level in 2025, now showing that form again.'),
        (3, 1, 'MAGIC COLORS', 'Beyers: 55 win last | Synth specialist',
         'WON last at Md$17.5k on synth (55 Beyer), then claimed. D Angelo fires at 24% with 1st claim horses - top angle in the race. Sharp Tapeta works. Speed horse (Early pace 93) could control from the front. Proven winner at this level on this surface type.'),
    ]),
    (8, '5 Furlongs Tapeta (off turf) | Claiming $35,000 NW2L | F and M 3YO+ | Post 4:37 PM | SCRATCH: #7 Scootaloo', [
        (1, 3, 'MIDSUMMER MO', 'Beyers: 64/74/63 (synth) | Avg 67.0',
         'Best synth figures in the race - 7 synth starts with wins, avg 67 and career-high 74. WON at WO on synth going to the lead. Casse trainer 16%, hits with synthetic horses. Tapeta is most similar surface to synth. Zayas aboard (18%). Set pace angle fits a sprint.'),
        (2, 1, "BRITTANY'S WAY", 'Beyers: 65/65/66 | Avg 65.3',
         'Most consistent horse in the race - three straight figures of 65-65-66. Natural pace-setter who likes to lead. Has been 2nd and 3rd in recent turf sprints at this class. Steve Owens trainer 20% overall. Ruiz J aboard. First Tapeta start but figures say she belongs.'),
        (3, 6, 'YOU BE THE JUDGE', 'Beyers: 60/69/63 (synth) | Avg 64.0',
         'BLINKERS ON today - equipment change for a synth specialist (14 synth starts). Trainer Owens with blinker addition at 33%. Has run competitive figures on this surface type. With sharper equipment and this sprint distance, capable of turning around recent form.'),
    ]),
    (9, '5.5 Furlongs Tapeta | SOC $17,500 | 3YO NW1X | Post 5:08 PM | SCRATCH: #1 Kazooza', [
        (1, 7, 'COPERNIUM', 'Beyer: 62 win last out',
         'WON last at this exact distance and condition (5.5F Tapeta $17.5k, Beyer 62). Carlos David trainer hits at 25% win rate. 1stClaim angle fires at 31% ($2.15 ROI) - elite angle. Claimed specifically for this spot. Vasquez M.A. up. 8-5 ML reflects the strong form.'),
        (2, 4, 'LOSMASTIX', 'Beyers: 56/56/45 | Avg 52.3',
         'WON his last start on this exact Tapeta surface (56 Beyer), with consistent back-to-back 56s. Sano trainer and Zayas are a clicking combo at GP. Proven he handles the Tapeta. Clear second-best recent form in the race.'),
        (3, 6, 'NOT NOW NICK', 'Beyers: 63/58/-0 | Synth wins',
         'Won at Md$17.5k on synth (63 Beyer) and ran 2nd in OC35k (58 Beyer). Last out stopped cold on a wet track - legitimate excuse for the poor figure. Two legit good efforts on this surface type before the bad one. Hurtak trainer, Ruiz J aboard. Figures say he belongs here.'),
    ]),
    (10, '1-1/16 Miles Tapeta (off turf) | Claiming $35,000 NW2L | F and M 3YO+ | Post 5:40 PM | SCRATCHES: #7 #8', [
        (1, 5, 'MOONLIGHT PROMISES', 'Beyers: 63/81/68 | Avg 70.7',
         'Best Beyer average in the race AND career-best 81 Beyer on synthetic (WON convincingly). Last out was a turf sprint (wrong distance, wrong surface) - ignore it. Moving to Tapeta route today which perfectly matches her dominant synth win. Casse trainer 16%. Castellano rides. Best horse on figures.'),
        (2, 2, 'DAZZLING CRUISER', 'Beyers: 73/67/62 | Avg 67.3',
         'Two straight runner-up finishes at GP on Tapeta (73 and 67 Beyer). She keeps showing up and the win is overdue. DePaulo trainer loaded with 2nds (consistent exacta threat). Gaffalione aboard (16%). 5-2 ML is fair. Best bet for an exacta key.'),
        (3, 1, 'THAMES', 'Beyer: 68 win last out (turf)',
         'WON last out at GP on turf (68 Beyer, drew off). Mott trainer 25% with claim horses. Now moving to Tapeta - surface switch is the main risk, but has bullet Tapeta works. Zayas up. Won last, competes here.'),
    ]),
]

rank_labels = {1: '1st PICK', 2: '2nd PICK', 3: '3rd PICK'}

for race_num, race_info, picks in races:
    story.append(Paragraph(f'RACE {race_num}', race_header_style))
    story.append(Paragraph(race_info, ParagraphStyle('ri', parent=styles['Normal'], fontSize=8,
        spaceAfter=4, textColor=colors.HexColor('#666666'))))

    for rank, pp, horse, beyers, analysis in picks:
        bg_color = pp_colors.get(pp, colors.grey)
        txt_color = pp_text_colors.get(pp, colors.white)

        data = [[
            Paragraph(f'<b> #{pp} </b>', ParagraphStyle('pp', parent=styles['Normal'],
                fontSize=10, textColor=txt_color, fontName='Helvetica-Bold')),
            Paragraph(f'<b>{rank_labels[rank]} -- {horse}</b>  [{beyers}]',
                ParagraphStyle('hn', parent=styles['Normal'], fontSize=9.5, fontName='Helvetica-Bold'))
        ]]
        t = Table(data, colWidths=[0.55*inch, 6.4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), bg_color),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f8f8f8')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (0, 0), 6),
            ('LEFTPADDING', (1, 0), (1, 0), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(t)
        story.append(Paragraph(analysis, ParagraphStyle('an', parent=styles['Normal'],
            fontSize=8, spaceAfter=5, leftIndent=8, textColor=colors.HexColor('#333333'))))

    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#eeeeee'), spaceAfter=2))

story.append(Spacer(1, 8))
story.append(Paragraph('Generated by Charlie | In Beyers We Trust | Picks for entertainment purposes only',
    footer_style))

doc.build(story)
print('PDF created successfully')
