"""Read-only Codex allowance telemetry. No inference turns or credential output."""
import datetime as dt
import json
import math
import selectors
import subprocess
import threading
import time

LOCK = threading.Lock()
SNAPSHOT = None
CHECKED = 0
TTL = 120

def normalize(result):
    buckets = result.get('rateLimitsByLimitId')
    if not isinstance(buckets, dict) or not buckets:
        legacy = result.get('rateLimits')
        buckets = {legacy.get('limitId') or 'codex': legacy} if isinstance(legacy, dict) else {}
    rows = []
    for key, bucket in buckets.items():
        if not isinstance(bucket, dict): continue
        for slot in ['primary', 'secondary']:
            window = bucket.get(slot)
            if not isinstance(window, dict): continue
            used = window.get('usedPercent')
            valid = isinstance(used, (int, float)) and not isinstance(used, bool) and math.isfinite(used)
            minutes = window.get('windowDurationMins')
            reset = window.get('resetsAt')
            rows.append(dict(bucket=str(key), name=str(bucket.get('limitName') or 'Codex'), slot=slot,
                             usedPercent=max(0,min(100,used)) if valid else None,
                             remainingPercent=max(0,min(100,100-used)) if valid else None,
                             windowDurationMins=minutes if isinstance(minutes,int) and minutes>0 else None,
                             resetsAt=reset if isinstance(reset,(int,float)) and math.isfinite(reset) else None))
    return rows

def read_limits():
    proc = subprocess.Popen(['/usr/local/bin/codex','app-server','--listen','stdio://'], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
    selector=selectors.DefaultSelector();selector.register(proc.stdout,selectors.EVENT_READ)
    deadline=time.monotonic()+25
    def rpc(i, method, params=None):
        proc.stdin.write(json.dumps(dict(id=i,method=method,params=params))+'\n');proc.stdin.flush()
        while time.monotonic()<deadline:
            if selector.select(min(1,max(0,deadline-time.monotonic()))):
                line=proc.stdout.readline()
                if not line: raise RuntimeError('Usage connection closed')
                msg=json.loads(line)
                if msg.get('id')==i:return msg
        raise TimeoutError('Usage request timed out')
    try:
        if 'error' in rpc(1,'initialize',{'clientInfo':{'name':'inxs_usage','title':'INXS usage meter','version':'1.0'}}):
            raise RuntimeError('Usage connection unavailable')
        proc.stdin.write('{"method":"initialized"}\n');proc.stdin.flush()
        response=rpc(2,'account/rateLimits/read')
        if 'error' in response:
            error=str(response['error'].get('message','')).lower()
            if '401' in error or 'unauthorized' in error or 'not logged' in error:
                return dict(state='signin-required',windows=[],note='Sign in to Codex on the Linux machine to connect your usage meter.')
            return dict(state='unavailable',windows=[],note='Codex usage could not be checked. Retrying automatically.')
        windows=normalize(response.get('result') or {})
        return dict(state='current' if windows else 'unavailable',windows=windows,
                    note='Account-wide allowance, shared across Codex devices.' if windows else 'No usage windows were supplied for this account.')
    finally:
        selector.close();proc.terminate()
        try:proc.wait(timeout=3)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()

def usage():
    global SNAPSHOT,CHECKED
    with LOCK:
        if SNAPSHOT is not None and time.monotonic()-CHECKED<TTL:return dict(SNAPSHOT)
        stamp=dt.datetime.now(dt.timezone.utc).isoformat()
        try: result=read_limits()
        except Exception: result=dict(state='unavailable',windows=[],note='Codex usage could not be checked. Retrying automatically.')
        if result['state']=='unavailable' and SNAPSHOT and SNAPSHOT.get('windows'):
            result=dict(SNAPSHOT,state='cached',note='Usage check unavailable. Showing the last confirmed reading; retrying automatically.')
        elif result['state']=='current':result['fetchedAt']=stamp
        result.update(checkedAt=stamp,refreshSeconds=TTL)
        SNAPSHOT=result;CHECKED=time.monotonic()
        return dict(result)
