#!/usr/bin/env python3

import subprocess
import urllib
from pathlib import Path
from os.path import expanduser
import yaml
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from dataclasses import dataclass
from typing import List

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


@dataclass
class Listing:
    url: str
    id: int
    title: str
    region: str
    query: str


def get_current_listings(r, q) -> List[Listing]:
    res = requests.get(f'http://{r}.craigslist.org/search/sss?sort=rel&query={urllib.parse.quote(q)}').text
    soup = BeautifulSoup(res, "lxml")
    elements = soup.findAll('a', {'class': 'result-title'})
    return [Listing(url=e['href'], id=e['data-id'], title=e.text, query=q, region=r) for e in elements]


def termux_notification(listing: Listing):
    """
    https://wiki.termux.com/wiki/Termux-notification
    """

    subprocess.call([
        'termux-notification',
        '--title', f'New \'{listing.query}\' listing in \'{listing.region}\'',
        '--content', f'{listing.title}',
        '--action', f'termux-open-url {listing.url}',
        '--group', 'craigslist_notify'
    ])


def filter_out_known_listings(s, r, q, listings) -> List[Listing]:
    current_ids = set(map(lambda l: l.id, listings))
    new_ids = current_ids - s[r][q]
    return list(filter(lambda x: x.id in new_ids, listings))


def notify_new_and_update_state(s, r, q):
    current_listings = get_current_listings(r, q)
    new_listings = filter_out_known_listings(s, r, q, current_listings)

    list(map(lambda l: termux_notification(l), new_listings))

    s[r][q] |= set(map(lambda l: l.id, new_listings))


def main():
    state = load_yaml(STATE_FILE) or defaultdict(lambda: defaultdict(set))
    config = load_yaml(CONFIG_FILE) or {}

    for region in config:

        if region not in state:  # handle new query
            state[region] = defaultdict(set)

        for query in config[region]:
            state[region][query] = set(state[region][query])
            notify_new_and_update_state(state, region, query)

    save_yaml(STATE_FILE, sanitize_state(state))


if __name__ == '__main__':
    main()
