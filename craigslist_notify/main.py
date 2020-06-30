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
    for identifier in state_obj:
        state_obj[identifier] = list(state_obj[identifier])
    return state_obj


@dataclass(frozen=True)
class Search:
    region: str
    query: str
    by: str
    identifier: str


def to_search_data(yaml_dict) -> Search:
    return Search(
        region=yaml_dict['region'],
        query=yaml_dict['query'],
        by=yaml_dict['by'],
        identifier=''.join(sorted(yaml_dict.values()))
    )


@dataclass(frozen=True)
class Listing:
    url: str
    id: int
    title: str
    region: str
    query: str


BY_ROUTES = {
    'all': 'sss',
    'owner': 'sso',
    'dealer': 'ssq'
}


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


def termux_schedule():
    job_id = 2566843  # CLNOTIF
    subprocess.call([
        'termux-job-scheduler',
        '--script', '$(which craigslist_notify)',
        '--period-ms', '900000',
        '--job-id', f'{job_id}',
        '--persisted', 'true'
    ])


def get_current_listings(search: Search) -> List[Listing]:
    res = requests.get(
        f'http://{search.region}.craigslist.org/search/{BY_ROUTES[search.by]}?sort=rel&query={urllib.parse.quote(search.query)}',
    ).text

    soup = BeautifulSoup(res, "lxml")
    elements = soup.findAll('a', {'class': 'result-title'})

    return [
        Listing(url=e['href'], id=e['data-id'], title=e.text, query=search.query, region=search.region)
        for e in elements
    ]


def filter_out_known_listings(state, search: Search, listings: List[Listing]) -> List[Listing]:
    current_ids = set(map(lambda l: l.id, listings))
    new_ids = current_ids - state[search.identifier]
    return list(filter(lambda x: x.id in new_ids, listings))


def notify_new_and_update_state(state, search: Search):
    current_listings = get_current_listings(search)
    new_listings = filter_out_known_listings(state, search, current_listings)

    for listing in new_listings:
        termux_notification(listing)

    state[search.identifier] |= set(map(lambda l: l.id, new_listings))


def main():
    state = load_yaml(STATE_FILE) or defaultdict(set)
    config = load_yaml(CONFIG_FILE) or {}

    for search_dict in config:

        search: Search = to_search_data(search_dict)

        if search.identifier in state:  # handle new query
            state[search.identifier] = set(state[search.identifier])
        else:
            state[search.identifier] = set()

        notify_new_and_update_state(state, search)

    save_yaml(STATE_FILE, sanitize_state(state))
    termux_schedule()


if __name__ == '__main__':
    main()
