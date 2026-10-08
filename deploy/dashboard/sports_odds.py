"""Read public ScoresAndOdds boards; never substitute odds across games."""
import datetime as dt
import json
import re
import urllib.request
from html.parser import HTMLParser
import sports_page

class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children, self.parts = tag, dict(attrs), [], []
    def find(self, predicate):
        result=[]
        for child in self.children:
            if predicate(child):result.append(child)
            result.extend(child.find(predicate))
        return result
    def text(self):return ' '.join(' '.join(self.parts).split())

class BoardParser(HTMLParser):
    def __init__(self):
        super().__init__();self.root=Node();self.stack=[self.root]
    def handle_starttag(self, tag, attrs):
        node=Node(tag,attrs);self.stack[-1].children.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(node)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:del self.stack[i:];break
    def handle_data(self, text):
        for node in self.stack:node.parts.append(text)

def has_class(node, name):return name in node.attrs.get('class','').split()
def abbreviation(value):
    value=re.sub(r'[^A-Z0-9]','',value.upper())
    return {'UTA':'UTAH','CWS':'CHW','WSH':'WSH','WAS':'WSH','SFG':'SF','SDP':'SD','KCR':'KC','TBR':'TB','TAM':'TB','NYY':'NYY','LAD':'LAD','SJS':'SJ','LAK':'LA','NJD':'NJ','TBL':'TB'}.get(value,value)

def parse_board(html, league, date):
    parser=BoardParser();parser.feed(html);root=parser.root;metadata={}
    for script in root.find(lambda n:n.tag=='script' and n.attrs.get('type')=='application/ld+json'):
        try:
            item=json.loads(script.text())
            if item.get('@type')=='SportsEvent':metadata[str(item['identifier'])]=item
        except (ValueError,KeyError,TypeError,AttributeError):continue
    games=[]
    for card in root.find(lambda n:has_class(n,'event-card')):
        item=metadata.get(card.attrs.get('id','').split('.')[-1]);rows=card.find(lambda n:n.tag=='tr' and n.attrs.get('data-side') in ('away','home'))
        if not item or len(rows)!=2:continue
        try:
            start=dt.datetime.fromisoformat(item['startDate'].replace('Z','+00:00'))
            if start.astimezone(sports_page.ZoneInfo('America/Toronto')).date()!=date:continue
            teams={side:abbreviation(item[side+'Team']['name'].split()[0]) for side in ('away','home')}
        except (ValueError,KeyError,TypeError):continue
        markets={}
        for row in rows:
            side=row.attrs['data-side'];markets[side]={}
            for cell in row.find(lambda n:n.tag=='td' and n.attrs.get('data-field','').startswith('current-')):
                key=cell.attrs['data-field'].removeprefix('current-')
                values=cell.find(lambda n:has_class(n,'data-value') or has_class(n,'data-moneyline'))
                prices=cell.find(lambda n:has_class(n,'data-odds'))
                value=values[0].text() if values else ''
                price=prices[0].text() if prices else ''
                # Only accept conventional American odds and line values, never page text.
                valid_price=lambda v:bool(re.fullmatch(r'[+-]\d{2,5}|even|EVEN',v))
                if key=='moneyline' and valid_price(value):markets[side][key]=value
                elif key in ('spread','total') and re.fullmatch(r'[ou]?[+-]?\d+(?:\.\d+)?',value) and valid_price(price):
                    markets[side][key]=value+' ('+price+')'
        if any(markets[s] for s in markets):games.append(dict(start=start.isoformat(),teams=teams,markets=markets))
    if not metadata:raise ValueError('Provider board format unavailable')
    return games

def board(league,date):
    def read():
        url='https://www.scoresandodds.com/'+league.lower()+'?date='+date.isoformat()
        req=urllib.request.Request(url,headers={'User-Agent':'INXS-Dashboard/1.0','Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=10) as response:html=response.read(3000000).decode('utf-8')
        return parse_board(html,league,date)
    return sports_page.cached('odds:'+league+':'+date.isoformat(),read,60)

def attach(events,league,date):
    # Finished games retain their normal scorecard; do not relabel closing prices as live.
    if date<sports_page.today() or not any(e['state']!='post' for e in events):return
    feed=board(league,date)
    for event in events:
        if event['state']=='post':continue
        status=dict(source='ScoresAndOdds',url='https://www.scoresandodds.com/'+league.lower()+'?date='+date.isoformat(),updatedAt=feed['updatedAt'],stale=feed['stale'])
        event['odds']=dict(status,markets=None)
        if feed['stale']:continue # Hide outdated prices rather than present them as current.
        away,home=(abbreviation(t['name']) for t in event['teams'])
        start=dt.datetime.fromisoformat(event['date'].replace('Z','+00:00'))
        candidates=[g for g in feed['data'] or [] if g['teams']==dict(away=away,home=home) and abs((dt.datetime.fromisoformat(g['start'])-start).total_seconds())<=2700]
        if len(candidates)==1:event['odds']['markets']=candidates[0]['markets']
