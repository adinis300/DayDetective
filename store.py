"""
Persistent storage — uses Android SharedPreferences via Kivy's JsonStore
on device, plain JSON file on desktop.
"""
import json, os, datetime
from kivy.storage.jsonstore import JsonStore

BASE  = os.path.dirname(os.path.abspath(__file__))
_store = JsonStore(os.path.join(BASE, 'data.json'))

LB_KEYS = {'standard': 'lb_standard', 'time': 'lb_time'}

def load_lb(mode):
    key = LB_KEYS[mode]
    try:
        return _store.get(key)['entries']
    except Exception:
        return []

def add_score(mode, score):
    key     = LB_KEYS[mode]
    entries = load_lb(mode)
    today   = datetime.date.today().strftime('%d %b %Y')
    entries.append({'score': score, 'date': today})
    entries.sort(key=lambda x: x['score'], reverse=True)
    entries = entries[:5]
    _store.put(key, entries=entries)
    return entries

def get_best(mode):
    entries = load_lb(mode)
    return entries[0]['score'] if entries else 0
