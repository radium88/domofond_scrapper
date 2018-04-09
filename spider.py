#!/usr/bin/env python3.6

import multiprocessing.dummy as dmp

from datetime import datetime
from functions import get_entries_links, get_tree, get_link_details, put_in_db
from update_coords import update_gps_routelen

url = "https://www.domofond.ru/arenda-odnokomnatnyh-kvartir-sankt_peterburg-c3414" \
      "?PriceTo=20000&RentalRate=Month&Page={}"


def get_pages_count(url):
    tree = get_tree(url.format(1), "https://domofond.ru")

    # get total pages count
    pages_container = tree.xpath('//div[@class = "b-pager"]/ul/li[last()]')[0]
    return int(pages_container.text_content())


def _gld_wrapper(params):
    return get_link_details(*params)


if __name__ == '__main__':
    # tree = get_tree(url.format(1), "https://domofond.ru")

    pages_count = get_pages_count(url)
    print(f'Pages count: {pages_count}')

    pages_links = [url.format(x) for x in range(1, pages_count + 1)]

    pool = dmp.Pool()

    # measuring gathering time
    _now = datetime.now()

    # gathering links
    entries_links = {}
    counter = 1

    link_prefix = 'https://www.domofond.ru'

    # will get list of lists, set of entries per page
    for i in pool.imap(get_entries_links, pages_links):
        print(f'\rGathering links for page {counter} of {pages_count}, {counter / pages_count * 100:.2f}%', end='')
        entries_links[i[0]] = [link_prefix + x for x in i[1]]
        counter += 1

    links_count = len([y for x in entries_links.values() for y in x])
    print(f'\nGathered {links_count} links in {(datetime.now() - _now)} sec')

    # gathering entries full info
    sleep_delay = 0.25

    counter = 1
    pages_counter = 1
    gathered_info = []
    for k, v in entries_links.items():
        print(f'Processing page {pages_counter}/{pages_count}')

        iter_data = [(l, k, sleep_delay) for l in v]
        for i in pool.imap(_gld_wrapper, iter_data):
            print(f'Processing entry {counter}/{links_count}, {counter / links_count * 100:.2f}%')
            gathered_info.append(i)
            counter += 1
        pages_counter += 1

    # print(gathered_info)
    put_in_db(gathered_info)
    update_gps_routelen()

    print(f'Total elapsed time: {datetime.now() - _now}')
