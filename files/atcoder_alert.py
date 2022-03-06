#!/usr/bin/env python3

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup, Tag

WEBHOOK = os.environ['WEBHOOK']
DB_PATH = 'task_db.json'


@dataclass(frozen=True)
class Contest:
    timestamp: int
    url: str
    title: str

    @classmethod
    def from_tr(cls, tr: Tag):
        tds = tr.select('td')
        time_text = re.sub(r'\+.*', '', tds[0].text.strip())
        link = tds[1].select_one('a')
        timestamp = int(datetime.fromisoformat(time_text).timestamp())
        url = urljoin('https://atcoder.jp/', link['href'])
        title = link.text.strip()
        return cls(timestamp, url, title)


def register(con: Contest):
    dt = datetime.fromtimestamp(con.timestamp - 30 * 60)
    date, time = dt.strftime('%Y-%m-%d %H:%M').split()
    body = {
        'content': f'<@&936589677132124160> あと30分で {con.title} が始まります\\r{con.url}'
    }
    command = ' '.join([
        'curl',
        '-X POST',
        '-H "Content-Type: application/json"',
        f"-d '{json.dumps(body)}'",
        WEBHOOK
    ])
    subprocess.run(['at', time, date], input=command, text=True)


def load_db():
    if not Path(DB_PATH).exists():
        return set()
    data_list = json.loads(Path(DB_PATH).read_text())
    now = datetime.now().timestamp()
    db = {Contest(*d) for d in data_list if d['timestamp'] > now}
    return db


def save_db(db):
    data_list = [asdict(d) for d in db]
    Path(DB_PATH).write_text(json.dumps(data_list))


def main():
    res = requests.get('https://atcoder.jp/contests/?lang=ja')
    soup = BeautifulSoup(res.content, 'lxml')
    db = load_db()
    for tr in soup.select('#contest-table-upcoming tbody tr'):
        try:
            con = Contest.from_tr(tr)
            if con not in db and 'Beginner' in con.title:
                register(con)
                db.add(con)
        except:
            continue
    save_db(db)


if __name__ == '__main__':
    main()
