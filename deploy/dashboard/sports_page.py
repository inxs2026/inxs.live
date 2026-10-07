"""Date-specific scoreboards and explicitly selected season standings."""
import datetime as dt
import json
import threading
import time
import urllib.request
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
    return cached('scores:'+date.isoformat(),lambda:reader(date),60 if date==today() else 600)

def season_year(league,date):
    if league=='NHL':return date.year+1 if date.month>=7 else date.year
    if league=='NFL':return date.year-1 if date.month<3 else date.year
    return date.year

def normalize_standings(league,data,brands):
    groups=[]
    def walk(group,parent=''):
        entries=group.get('standings',{}).get('entries',[])
        if entries:
            rows=[]
            for entry in entries:
                team=entry.get('team',{});brand=sports_teams.branding(team);saved=brands.get(str(team.get('id')), {})
                brand={k:saved.get(k) or v for k,v in brand.items()}
                stats={s['name']:s.get('displayValue',str(s.get('value','—'))) for s in entry.get('stats',[]) if s.get('name')}
                rows.append({'team':dict(name=team.get('abbreviation') or team.get('displayName','Team'),**brand),'stats':stats})
            groups.append({'name':group.get('name') or parent or league,'rows':rows})
        for child in group.get('children',[]):walk(child,group.get('name',parent))
    walk(data)
    if not groups:raise ValueError('Standings missing')
    return {'league':league,'season':data.get('season',{}).get('displayName'),'groups':groups,'source':'ESPN'}

def standings(league):
    if league not in SLUGS:raise ValueError('Unsupported league')
    def read():
        year=season_year(league,today());slug=SLUGS[league]
        url=f'https://site.api.espn.com/apis/v2/sports/{slug}/standings?season={year}'
        req=urllib.request.Request(url,headers={'User-Agent':'INXS/1.0 (personal sports page)'})
        with urllib.request.urlopen(req,timeout=12) as response:data=json.loads(response.read(4000000))
        return normalize_standings(league,data,sports_teams.registry(slug))
    return cached('standings:'+league+':'+str(season_year(league,today())),read,600)
