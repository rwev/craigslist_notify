import urllib
from collections import defaultdict, namedtuple

import yaml
import requests
from bs4 import BeautifulSoup
from notifyme import NotifyMeMailer
from pathlib import Path
from os.path import expanduser

FILE_BASE = '~/.craigslist_notify_'
FILE_EXT = '.yaml'
CONFIG_FILE = expanduser(f'{FILE_BASE}config{FILE_EXT}')
STATE_FILE = expanduser(f'{FILE_BASE}state{FILE_EXT}')


def load_yaml(path):
    Path(path).touch()
    with open(path, 'r') as file:
        return yaml.full_load(file)

def save_yaml(path, data):
    with open(path, 'a') as file:
        yaml.dump(data, file)

def sanitize_state(state_obj):
    state_obj = dict(state_obj)
    for region in state_obj:
        state_obj[region] = dict(state_obj[region])
        for query in state_obj[region]:
            state_obj[region][query] = list(state_obj[region][query])
    return state_obj

def get_current_id_set(region, query):
    res = requests.get(f'http://{region}.craigslist.org/search/sss?sort=rel&query={urllib.parse.quote(query)}').text
    soup = BeautifulSoup(res, "lxml")
    listing_items = soup.findAll('a', {'class': 'result-title'})
    return set([i['data-pid'] for i in listing_items])

state = load_yaml(STATE_FILE) or defaultdict(lambda: defaultdict(set))
config = load_yaml(CONFIG_FILE) or {}

for region in config:

    for query in config[region]:
        latest_ids = get_current_id_set(region, query)
        known_ids = set(state[region][query])
        new_ids = latest_ids - known_ids
        print (new_ids)
        known_ids |= new_ids
        state[region][query] = known_ids

save_yaml(STATE_FILE, sanitize_state(state))
