#!/usr/bin/env python3.6

import lxml
import multiprocessing.dummy as dmp

from datetime import datetime

from functions import get_entries_links, get_tree, get_link_details, put_in_db

url = "https://www.domofond.ru/arenda-odnokomnatnyh-kvartir-sankt_peterburg-c3414" \
      "?PriceTo=20000&RentalRate=Month&Page={}"


def get_pages_count(url):
    tree = get_tree(url.format(1), "https://domofond.ru")

    # get total pages count
    pages_container = tree.xpath('//div[@class = "b-pager"]/ul/li[last()]')[0]
    return int(pages_container.text_content())

#
# links = {}
#
# print('Total pages:', pages_count)
#
# # get links from all other pages
# for pc in range(1, pages_count + 1):
#     print('Gathering links', pc, '\r')
#     current_url = url.format(pc)
#     current_tree = get_tree(current_url, url.format(1))
#     current_links = proceed_page(current_tree)
#     current_links = list(set(current_links))
#     links.update({
#         current_url: current_links
#     })
#
#     # sleep(1)
#     # break
#
# gathered_info = []
#
# c = 1
# cw = 0
# for l_url, l_links in links.items():
#     print("{}/{}, {}".format(c, len(links), len(l_links)))
#     # print(l_url, l_links)
#     for l in l_links:
#         try:
#             # print(l, l_url)
#             details = get_link_details("https://www.domofond.ru" + l, l_url)
#             # print(details)
#
#             gathered_info.append(details)
#         except Exception as e:
#             print(e)
#
#         break
#
#     c += 1
#
#     # sleep(0.5)
#     # break
#
# print(gathered_info)
# # put_in_db(gathered_info)
# # update_gps_routelen()


if __name__ == '__main__':
    # tree = get_tree(url.format(1), "https://domofond.ru")

    pages_count = get_pages_count(url)
    print(f'Pages count: {pages_count}')

    pages_links = [url.format(x) for x in range(1, pages_count + 1)]

    # print(get_entries_links(pages_links[0]))

    pool = dmp.Pool()

    # measuring gathering time
    _now = datetime.now()

    # gathering links
    entries_links = []
    counter = 1

    # will get list of lists, set of entries per page
    for i in pool.imap(get_entries_links, pages_links):
        print(f'\rGathering links for page {counter} of {pages_count}, {counter / pages_count * 100:.2f}%', end='')
        entries_links.append(i)
        counter += 1

    # making flat list of entries list
    entries_links = [y for x in entries_links for y in x]

    print(f'\nGathered {len(entries_links)} links in {(datetime.now() - _now)} sec')


    # get current page links
    # links = get_entries_links(tree)

    # print(links)