"""Validated ESPN team branding, cached separately from live game scores."""
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
CACHE=Path(__file__).resolve().parent/'.cache/sports-teams'
SLUGS={'hockey/nhl','baseball/mlb','football/nfl'}

def color(value):return '#'+value.lower().lstrip('#') if isinstance(value,str) and re.fullmatch(r'#?[0-9a-fA-F]{6}',value) else None

def logo(value):
    try:
        url=urllib.parse.urlsplit(value)
        return value if url.scheme=='https' and url.hostname=='a.espncdn.com' and not url.username and not url.password else None
    except (ValueError,TypeError):return None

def branding(team):
    logos=team.get('logos') or []
    dark=next((logo(l.get('href')) for l in logos if 'dark' in l.get('rel',[]) and 'scoreboard' not in l.get('rel',[]) and logo(l.get('href'))),None)
    image=dark or logo(team.get('logo')) or next((logo(l.get('href')) for l in logos if logo(l.get('href'))),None)
    return dict(displayName=team.get('displayName'),logo=image,color=color(team.get('color')),alternateColor=color(team.get('alternateColor')))

def registry(slug):
    if slug not in SLUGS:raise ValueError('Unsupported league')
    path=CACHE/(slug.replace('/','-')+'.json');saved={}
    try:
        saved=json.loads(path.read_text())
        if time.time()-path.stat().st_mtime<86400:return saved
    except (OSError,ValueError):pass
    try:
        url='https://site.api.espn.com/apis/site/v2/sports/'+slug+'/teams?limit=100'
        request=urllib.request.Request(url,headers={'User-Agent':'INXS/1.0 (personal scoreboard)'})
        with urllib.request.urlopen(request,timeout=12) as response:data=json.loads(response.read(2000000))
        teams=data['sports'][0]['leagues'][0]['teams']
        result={str(entry['team']['id']):branding(entry['team']) for entry in teams}
        if not result:raise ValueError('Empty team registry')
        CACHE.mkdir(parents=True,exist_ok=True);temp=path.with_suffix('.tmp');temp.write_text(json.dumps(result));temp.replace(path)
        return result
    except Exception:return saved

def competitor(value,teams):
    team=value.get('team',{});saved=teams.get(str(team.get('id')),{});own=branding(team)
    brand={field:own.get(field) or saved.get(field) for field in own}
    # Prefer a dark-background official variant from the complete team registry.
    brand['logo']=saved.get('logo') or own['logo']
    return dict(name=team.get('abbreviation') or team.get('displayName') or 'Team',score=value.get('score','0'),home=value.get('homeAway')=='home',**brand)
