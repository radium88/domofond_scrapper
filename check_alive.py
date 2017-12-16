#!/usr/bin/env python3

import requests
import sqlite3
import sys
from datetime import datetime, timedelta

from functions import connect

def check_error(page_content):
    error_text = "Требуемый объект недвижимости был продан либо срок действия объявления истек."
    return error_text in page_content


conn = connect()
cur = conn.cursor()

query = "SELECT id, link FROM rooms WHERE alive = 1 AND link != '' AND update_date < ?"
cur.execute(query, (datetime.now() - timedelta(days=1), ))
res = cur.fetchall()

if not res:
    print("Nothing to do, exiting")
    sys.exit(0)

links_count = len(res)
counter = 1

for r in res:
    id = r[0]
    link = r[1]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
        'Referer': 'https://www.domofond.ru/arenda-kvartiry-sankt_peterburg-c3414?PriceTo=20000&RentalRate=Month&Rooms=One,Two'
    }

    request = requests.get(link)
    is_error = check_error(request.text)

    if request.status_code != 200 or is_error:
        print("{}/{}({:.2f})".format(counter, links_count, counter / links_count * 100),
              link,
              request.status_code,
              "not alive"
              )
        cur.execute("UPDATE rooms SET alive = 0 WHERE id = ?", (id, ))
        conn.commit()
    else:
        print("{}/{}({:.2f})".format(counter, links_count, counter / links_count * 100),
              link,
              request.status_code
              )

    counter += 1