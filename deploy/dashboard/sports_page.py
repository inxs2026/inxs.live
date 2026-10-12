"""Date-specific scoreboards and explicitly selected season standings."""
import datetime as dt
import json
import re
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo
import sports_teams
SLUGS={'NHL':'hockey/nhl','MLB':'baseball/mlb','NFL':'football/nfl'}
CACHE={};LOCK=threading.Lock();KEY_LOCKS={}
def today():return dt.datetime.now(ZoneInfo('America/Toronto')).date()
def date_value(value):
    try: date=dt.date.fromisoformat(value) if value else today()
    except (ValueError,TypeError):raise ValueError('Choose a valid date')
    if date<dt.date(2000,1,1) or date>dt.date(2099,12,31):raise ValueError('Choose a date between 2000 and 2099')
    return date

def cached(key,reader,ttl):
    with LOCK: lock=KEY_LOCKS.setdefault(key,threading.Lock())
    with lock:
        saved=CACHE.get(key)
        if saved and time.monotonic()-saved[0]<ttl:return saved[1]
        try:
            result={'data':reader(),'updatedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'stale':False,'error':None}
            CACHE[key]=(time.monotonic(),result)
            # Bound arbitrary past-date requests.
            if len(CACHE)>100:
                oldest=min(CACHE,key=lambda k:CACHE[k][0]);CACHE.pop(oldest,None)
            return result
        except Exception:
            if saved:return dict(saved[1],stale=True,error='Update unavailable. Showing the last confirmed reading.')
            return {'data':None,'updatedAt':None,'stale':True,'error':'Temporarily unavailable. Please retry.'}

def scoreboard(value,reader):
    date=date_value(value)
    return cached('scores:'+date.isoformat(),lambda:reader(date),60 if date>=today() else 600)

def season_year(league,date):
    if league=='NHL':return date.year+1 if date.month>=7 else date.year
    if league=='NFL':return date.year-1 if date.month<3 else date.year
    return date.year

def rank_key(league,row):
    values=row.get('values',{})
    seed=values.get('playoffSeed') or 999
    if league=='NHL':return (-values.get('points',0),seed)
    if league=='NFL':return (seed,-values.get('winPercent',0))
    return (-values.get('winPercent',0),seed)

def normalize_standings(league,data,brands):
    groups=[]
    def walk(group,parent='',conference=''):
        name=group.get('name') or parent or league
        if group.get('isConference') or name in ('American League','National League','Eastern Conference','Western Conference','American Football Conference','National Football Conference'):
            conference=name
        entries=group.get('standings',{}).get('entries',[])
        if entries:
            rows=[]
            for entry in entries:
                team=entry.get('team',{});brand=sports_teams.branding(team);saved=brands.get(str(team.get('id')), {})
                brand={k:saved.get(k) or v for k,v in brand.items()}
                stats={s['name']:s.get('displayValue',str(s.get('value','—'))) for s in entry.get('stats',[]) if s.get('name')}
                values={s['name']:s['value'] for s in entry.get('stats',[]) if s.get('name') and isinstance(s.get('value'),(int,float))}
                rows.append({'team':dict(id=str(team.get('id','')),name=team.get('abbreviation') or team.get('displayName','Team'),**brand),'stats':stats,'values':values})
            rows.sort(key=lambda row:rank_key(league,row))
            groups.append({'name':name,'conference':conference or parent,'rows':rows})
        for child in group.get('children',[]):walk(child,name,conference)
    walk(data)
    if not groups:raise ValueError('Standings missing')
    return {'league':league,'season':data.get('season',{}).get('displayName'),'groups':groups,'source':'ESPN'}

def standings_views(result):
    league=result['league'];groups=result['groups'];views={}
    conferences=list(dict.fromkeys(g['conference'] for g in groups))
    for index,conference in enumerate(conferences):
        key={'NHL':['eastern','western'],'MLB':['american','national'],'NFL':['afc','nfc']}[league][index]
        views[key]=[g for g in groups if g['conference']==conference]
    views['expanded']=groups
    wild=[];seeding=[]
    for conference in conferences:
        divisions=[g for g in groups if g['conference']==conference]
        places=3 if league=='NHL' else 1
        leaders=[row for g in divisions for row in g['rows'][:places]]
        remaining=sorted([row for g in divisions for row in g['rows'][places:]],key=lambda row: (row['values'].get('playoffSeed') or 999,-row['values'].get('winPercent',0)))
        leaders=sorted(leaders,key=lambda row:row['values'].get('playoffSeed') or 999)
        slots=2 if league=='NHL' else 3
        wild.append({'name':conference+' · '+('Top three in each division' if league=='NHL' else 'Division leaders'),'rows':leaders})
        contender_rows=[]
        for index,row in enumerate(remaining):
            copy=dict(row,stats=dict(row['stats']),position=index+1,inSpot=index<slots)
            if league=='MLB' and len(remaining)>=slots:
                cutoff=remaining[slots-1]['values'];v=row['values']
                gap=((cutoff.get('wins',0)-v.get('wins',0))+(v.get('losses',0)-cutoff.get('losses',0)))/2
                copy['stats']['wildCardBehind']=('+'+str(-gap).rstrip('0').rstrip('.') if gap<0 else '—' if gap==0 else str(gap).rstrip('0').rstrip('.'))
            contender_rows.append(copy)
        wild.append({'name':conference+' · Wild card race','rows':contender_rows,'cutoff':slots})
        seeding.append({'name':conference+' · Current playoff picture','rows':leaders+remaining[:slots]})
    views['wildcard']=wild;views['playoffs']=seeding
    result['views']=views
    result['wildCardNote']='Current positions, not confirmed playoff qualification. Provider rankings resolve tied records.'
    return result

def postseason(league,year,brands):
    # An upcoming calendar year's postseason has no confirmed games yet.
    calendar_year=year+1 if league=='NFL' else year
    if calendar_year>today().year:return []
    slug=SLUGS[league]
    months={'MLB':(9,10,11),'NHL':(4,5,6,7),'NFL':(1,2)}[league]
    def read_month(month):
        req=urllib.request.Request(f'https://site.api.espn.com/apis/site/v2/sports/{slug}/scoreboard?dates={calendar_year}{month:02d}&limit=1000',headers={'User-Agent':'INXS/1.0'})
        with urllib.request.urlopen(req,timeout=12) as response:return json.loads(response.read(16000000))
    # Fetch only postseason months, rather than truncating a full-season feed.
    with ThreadPoolExecutor(max_workers=4) as pool:
        events=[event for data in pool.map(read_month,months) for event in data.get('events',[])]
    games=[]
    for event in events:
        if event.get('season',{}).get('type')!=3 or event.get('season',{}).get('year')!=year:continue
        for competition in event.get('competitions',[]):
            teams=sorted(competition.get('competitors',[]),key=lambda c:c.get('homeAway')=='home')
            if len(teams)!=2:continue
            status=event.get('status',{}).get('type',{})
            round_name=next((n.get('headline') for n in competition.get('notes',[]) if n.get('headline')),'Postseason')
            round_name=re.sub(r'\s*-?\s*Game \d+.*$','',round_name).strip()
            games.append({'id':event['id'],'league':league,'date':event['date'],'state':status.get('state','pre'),'status':status.get('shortDetail','Scheduled'),'seriesSummary':playoff_series(competition),'round':round_name,'teams':[sports_teams.competitor(t,brands) for t in teams]})
    return games

def standings(league,view=''):
    if league not in SLUGS:raise ValueError('Unsupported league')
    def read():
        year=season_year(league,today());slug=SLUGS[league]
        url=f'https://site.api.espn.com/apis/v2/sports/{slug}/standings?season={year}&level=3'
        req=urllib.request.Request(url,headers={'User-Agent':'INXS/1.0 (personal sports page)'})
        with urllib.request.urlopen(req,timeout=12) as response:data=json.loads(response.read(4000000))
        brands=sports_teams.registry(slug)
        result=standings_views(normalize_standings(league,data,brands))
        if view=='playoffs':result['postseason']=postseason(league,year,brands)
        return result
    return cached('standings:'+league+':'+str(season_year(league,today()))+(':'+view if view=='playoffs' else ''),read,600)


def playoff_series(competition):
    """Use provider playoff status only; regular-season series are not playoffs."""
    series=competition.get('series') or {}
    if series.get('type')!='playoff':return None
    summary=series.get('summary')
    if not isinstance(summary,str) or not summary.strip():return None
    for competitor in competition.get('competitors',[]):
        team=competitor.get('team') or {}
        abbreviation=team.get('abbreviation')
        name=team.get('shortDisplayName') or team.get('displayName')
        if abbreviation and name:
            summary=re.sub(r'\b'+re.escape(abbreviation)+r'\b',lambda _:name,summary)
    return summary.strip()
