from lxml import html, etree
import requests
from time import sleep
import sqlite3

s = requests.session()

def connect():
    conn = sqlite3.connect("database.db")
    return conn

def proceed_page(page_tree):
    links = []

    listing_results = page_tree.xpath('//div[@id = "listingResults"]')[0]
    for x in listing_results:
        # print(etree.tostring(x))
        href = x.xpath('.//a/@href')
        if href:
            # get link
            links.append(href[0])

    return links


def get_tree(url):
    global s
    r = s.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'
    })
    page_content = r.text

    if r.status_code != 200:
        print(url, r.status_code)
        if r.status_code == 404:
            return None

        sleep(3600)
        return get_tree(url)


    return html.fromstring(page_content)


def get_link_details(url):
    tree = get_tree(url)
    if tree is None:
        return {}

    description = tree.xpath('//div[@class = "b-listing-details"]/p[@class = "m-listing-description"]')[0].text_content().strip()
    address = tree.xpath('//div[@class = "e-listing-address"]/span')[0].text_content().strip()

    details = {
        'description': description,
        'address': address
    }

    table = tree.xpath('//div[@class = "b-details-table"]/div[@class = "e-table-column"]/ul/li')

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
        'Бытовая техника': 'appliances'
    }

    details_tmp = {}

    for t in table:
        list = t.text_content().strip().replace('\r\n', '').replace('\xa0', ' ').split(':')
        if len(list) > 1:
            details_tmp[list[0]] = list[1].replace('РУБ.', '').replace('м²', '').strip()

    details.update({replace_keys[k]: v for k, v in details_tmp.items() if k in replace_keys})

    details['price'] = details['price'].replace(' ', '')
    details['deposit'] = details['deposit'].replace(' ', '')

    return details


def put_in_db(data: list):
    conn = connect()
    cur = conn.cursor()

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
            values = ", ".join("=".join((k, "'" + v + "'")) for k, v in e.items())
            cur.execute("UPDATE rooms SET {} WHERE domofond_id = {}}".format(values, e['domofond_id']))
            conn.commit()
        else:
            # insert new record
            keys_str = ", ".join(e.keys())
            placeholders = ":" + ", :".join(e.keys())

            cur.execute("INSERT INTO rooms ({}) VALUES ({})".format(keys_str, placeholders), e)
            conn.commit()
