from lxml import html, etree
import requests
from time import sleep
import sqlite3
import geocoder
from xml.etree import ElementTree
from datetime import datetime
import random

random.seed()

s = requests.Session()

replace_keys = {
        'Номер в каталоге': 'domofond_id',
        'Этаж': 'floor',
        'Комнаты': 'rooms',
        'Дополнительно': 'additional_info',
        'Площадь кухни (м²)': 'kitchen_space',
        'Жилая площадь (м²)': 'live_space',
        'Площадь': 'total_space',
        'Дата публикации объявления': 'publish_date',
        'Дата обновления объявления': 'refresh_date',
        'Тип': 'type',
        'Залог': 'deposit',
        'Цена': 'price',
        'Материал здания': 'building_material',
        'Комфорт': 'comfort',
        'Цена за м²': 'cost_per_meter',
        'Комиссия': 'comission',
        'Бытовая техника': 'appliances',
    }


def connect():
    conn = sqlite3.connect("database.db")
    return conn


def get_entries_links(url, referer='https://domofond.ru'):
    page_tree = get_tree(url.format(1), referer)

    if page_tree is None:
        print('WARN: Empty tree!')
        return []

    links = []

    try:
        fake_pages = page_tree.xpath('//div[@id = "resultsPageDiv"]/style')[0]
        fake_pages = fake_pages.text_content().strip().replace('.', '').split('\r\n')
        fake_pages = [x.strip() for x in fake_pages]
        fake_pages = set([x.split('{')[0].strip() for x in fake_pages])

        listing_results = page_tree.xpath('//div[@id = "listingResults"]')[0]
        for x in listing_results:
            page_class = x.get('class')
            if 'b-dfp-ad' in page_class:
                continue

            if set(page_class.split(' ')).intersection(fake_pages):
                continue

            href = x.xpath('.//a/@href')
            if href and 'javascript' not in href[0]:
                # get link
                links.append(href[0])
    except IndexError as e:
        print(e)
        print(etree.tostring(page_tree))

    return url, links


def get_tree(url, referer, sleep_delay=0.5):
    global s

    sleep_delay = random.uniform(sleep_delay - (sleep_delay * 0.25), sleep_delay + (sleep_delay * 0.25)) \
        if sleep_delay else 0


    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/61.0.3163.91 Safari/537.36',
            'Referer': referer
        }

    retry_counter = 0

    while True:
        # cookies = s.cookies
        r = s.get(url, headers=headers, cookies=s.cookies)
        page_content = r.text

        # print(r.text)

        if r.status_code == 200:
            if sleep_delay > 0:
                sleep(sleep_delay)

            return html.fromstring(page_content)
        elif r.status_code == 503:
            print(url, "503, Waiting for 3600 sec")

            sleep(3600)
        elif r.status_code == 404:
            if retry_counter > 3:
                return None

        retry_counter += 1


def get_link_details(url, referer, sleep_delay=0.5):
    tree = get_tree(url, referer)
    if tree is None:
        print('WARN: Empty tree!')
        return {}

    sleep_delay = random.uniform(sleep_delay - (sleep_delay * 0.25), sleep_delay + (sleep_delay * 0.25)) \
        if sleep_delay else 0

    description = tree.xpath('//div[@class = "b-listing-details"]/div[contains(@class, "e-listing-description")]')

    if description:
        description = description[0].text_content().strip()
    else:
        description = ""

    address = tree.xpath('//a[@class = "e-listing-address-line"]')

    if address:
        address = address[0].text_content().strip()
    else:
        # without address entry is useless
        return {}

    details = {
        'description': description,
        'address': address
    }

    table = tree.xpath('//div[@class = "b-details-table"]/div[@class = "e-table-column"]/ul/li')

    details_tmp = {}

    for t in table:
        t_list = t.text_content().strip().replace('\r\n', '').replace('\xa0', ' ').split(':')
        if len(t_list) > 1:
            details_tmp[t_list[0]] = t_list[1].replace('РУБ.', '').replace('м²', '').strip()

    details.update({replace_keys[k]: v for k, v in details_tmp.items() if k in replace_keys})

    details['price'] = details['price'].replace(' ', '')
    details['deposit'] = details['deposit'].replace(' ', '')
    details['link'] = url
    details['update_date'] = str(datetime.now())

    if sleep_delay > 0:
        sleep(sleep_delay)

    return details


def put_in_db(data: list):
    conn = connect()
    cur = conn.cursor()

    ins_cnt = 0
    upd_cnt = 0

    for e in data:
        if not e:
            continue

        if not 'domofond_id' in e.keys():
            print(e)
            continue

        cur.execute("SELECT id FROM rooms WHERE domofond_id = ?", (e['domofond_id'],))
        res = cur.fetchall()

        if res:
            # that id exists in db. updating info
            values = ", ".join("=".join((k, ":"+k)) for k in e.keys())

            cur.execute("UPDATE rooms SET {} WHERE domofond_id = '{}'".format(values, e['domofond_id']), e)
            conn.commit()

            upd_cnt += 1
        else:
            # insert new record
            keys_str = ", ".join(e.keys())
            placeholders = ":" + ", :".join(e.keys())

            cur.execute("INSERT INTO rooms ({}) VALUES ({})".format(keys_str, placeholders), e)
            conn.commit()

            ins_cnt += 1

    print("Processed {}, I:{}, U:{}".format(upd_cnt + ins_cnt, ins_cnt, upd_cnt))


def get_coords_from_address(address: str):
    g = geocoder.yandex(address)

    return g.latlng


def get_route_length(s_coord, t_coord):
    r = requests.get(
        "http://www.yournavigation.org/api/dev/route.php?flat={}&flon={}&tlat={}&tlon={}&v=cycleroute&fast=1".format(
            s_coord[0], s_coord[1], t_coord[0], t_coord[1])
    )

    if r.status_code != 200:
        return 0.0

    tree = etree.XML(r.content)
    el = tree.find('{http://earth.google.com/kml/2.0}Document')
    for x in el:
        if x.tag == '{http://earth.google.com/kml/2.0}distance':
            return x.text

    return 0.0


def check_alive_links():
    pass
