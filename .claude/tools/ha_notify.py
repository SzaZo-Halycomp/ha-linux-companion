#!/usr/bin/env python3
"""Call Home Assistant notify services with the panel's own login.

  ha_notify.py services
  ha_notify.py send <notify_service> <msg> [<msg> ...]

<msg> is a message text, optionally "text::{json}" to merge extra fields into the
service data (e.g. 'command_dnd::{"data":{"dnd":"on"}}'), or "sleepN" to pause N s.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

CONFIG = os.path.expanduser('~/.config/ha-linux-companion/config.json')


_cache = {}


def load():
    if _cache:
        return _cache['url'], _cache['tok']
    cfg = json.load(open(CONFIG))
    url = cfg['url'].rstrip('/')
    tokens = cfg.get('hassTokens') if isinstance(cfg.get('hassTokens'), dict) else {}
    tok = tokens.get('access_token') or cfg['token']
    # The app refreshes its token only while running; when it has expired, refresh it
    # here in memory (same client_id as src/auth.js) without touching config.json
    if tokens.get('refresh_token') and tokens.get('expires', 0) / 1000 < time.time() + 60:
        form = urllib.parse.urlencode({'grant_type': 'refresh_token', 'refresh_token': tokens['refresh_token'],
                                       'client_id': tokens.get('clientId') or url + '/'}).encode()
        with urllib.request.urlopen(urllib.request.Request(url + '/auth/token', data=form), timeout=15) as r:
            tok = json.loads(r.read())['access_token']
    _cache.update(url=url, tok=tok)
    return url, tok


def call(method, path, body=None):
    url, tok = load()
    req = urllib.request.Request(url + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status, json.loads(r.read() or b'null')


def main(argv):
    if len(argv) >= 1 and argv[0] == 'services':
        _, svcs = call('GET', '/api/services')
        print([s for d in svcs if d['domain'] == 'notify' for s in d['services'] if 'mobile_app' in s])
        return
    if len(argv) < 3 or argv[0] != 'send':
        print(__doc__)
        sys.exit(1)
    svc = argv[1]
    for msg in argv[2:]:
        if msg.startswith('sleep'):
            time.sleep(float(msg[5:] or 1))
            continue
        body = {'message': msg}
        if '::' in msg:
            text, extra = msg.split('::', 1)
            body = {'message': text, **json.loads(extra)}
        st, _ = call('POST', '/api/services/notify/' + svc, body)
        print(time.strftime('%H:%M:%S'), body['message'], '->', st)


if __name__ == '__main__':
    main(sys.argv[1:])
