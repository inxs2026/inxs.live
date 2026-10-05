"""Shared persistent notice history, acknowledgements, and technical verification."""
import datetime as dt
from pathlib import Path
import sqlite3
from contextlib import contextmanager
DB = Path.home()/'.local/state/inxs-dashboard/acknowledgements.sqlite3'

def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def key(value):
    if not isinstance(value,str) or not value or len(value)>2048 or any(ord(c)<32 for c in value):raise ValueError('Invalid notice identity')
    return value

@contextmanager
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=5)
    db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE IF NOT EXISTS notices (id INTEGER PRIMARY KEY, identity TEXT NOT NULL, text TEXT NOT NULL, url TEXT NOT NULL, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, acknowledged_at TEXT, resolved_at TEXT)')
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS active_notice_identity ON notices(identity) WHERE resolved_at IS NULL')
    db.execute('CREATE TABLE IF NOT EXISTS verifications (identity TEXT PRIMARY KEY, note TEXT NOT NULL, checked_at TEXT NOT NULL)')
    try:
        with db:yield db
    finally:db.close()

def listing():
    with connect() as db:
        keys=[row[0] for row in db.execute('SELECT identity FROM notices WHERE acknowledged_at IS NOT NULL AND resolved_at IS NULL')]
        history=[dict(row) for row in db.execute('SELECT n.*,v.note AS verification,v.checked_at AS verified_at FROM notices n LEFT JOIN verifications v ON n.identity=v.identity ORDER BY n.id DESC LIMIT 100')]
        return dict(keys=keys,history=history)

def observe(notices,complete=False):
    if not isinstance(notices,list) or len(notices)>64:raise ValueError('Invalid notices')
    values=[]
    for n in notices:
        identity=key(n.get('key'))
        text=n.get('text');url=n.get('url')
        if not isinstance(text,str) or not text or len(text)>4096 or not isinstance(url,str) or not url.startswith('/') or url.startswith('//') or len(url)>2048:raise ValueError('Invalid notice')
        values.append((identity,text,url))
    now=stamp()
    with connect() as db:
        active={row[0] for row in db.execute('SELECT identity FROM notices WHERE resolved_at IS NULL')}
        present={v[0] for v in values}
        if complete:
            for identity in active-present:db.execute('UPDATE notices SET resolved_at=? WHERE identity=? AND resolved_at IS NULL',(now,identity))
        for identity,text,url in values:
            db.execute('INSERT OR IGNORE INTO notices(identity,text,url,first_seen,last_seen) VALUES (?,?,?,?,?)',(identity,text,url,now,now))
            db.execute('UPDATE notices SET text=?,url=?,last_seen=? WHERE identity=? AND resolved_at IS NULL',(text,url,now,identity))
    return listing()

def acknowledge(value):
    identity=key(value)
    with connect() as db:
        cursor=db.execute('UPDATE notices SET acknowledged_at=COALESCE(acknowledged_at,?) WHERE identity=? AND resolved_at IS NULL',(stamp(),identity))
        if cursor.rowcount!=1:raise ValueError('Notice is not active')
    return dict(acknowledged=True)

def verify(identity,note):
    key(identity)
    with connect() as db:
        db.execute('INSERT OR REPLACE INTO verifications VALUES (?,?,?)',(identity,note,stamp()))
