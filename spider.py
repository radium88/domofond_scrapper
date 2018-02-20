#!/usr/bin/env python3

from functions import proceed_page, get_tree, get_link_details, put_in_db, connect
from time import sleep
from update_coords import update_gps_routelen

conn = connect()

url = "https://www.domofond.ru/arenda-odnokomnatnyh-kvartir-sankt_peterburg-c3414?PriceTo=18000&RentalRate=Month&Page={}"
# url = "https://www.domofond.ru/arenda-kvartiry-sankt_peterburg-c3414?PriceTo=20000&RentalRate=Month&Rooms=One,Two&Page={}"
tree = get_tree(url.format(1), "https://domofond.ru")

# get pages count
pages_container = tree.xpath('//div[@class = "b-pager"]/ul/li[last()]')[0]
pages_count = int(pages_container.text_content())

# get current page links
# links = proceed_page(tree)

links = {}

# links.update({
#     url.format(1): proceed_page(tree)
# })

print('Total pages:', pages_count)

# get links from all other pages
for pc in range(1, pages_count + 1):
    print('Gathering links', pc, '\r')
    current_url = url.format(pc)
    current_tree = get_tree(current_url, url.format(1))
    current_links = proceed_page(current_tree)
    current_links = list(set(current_links))
    links.update({
        current_url: current_links
    })

    # sleep(1)
    # break

gathered_info = []

c = 1
cw = 0
for l_url, l_links in links.items():
    print("{}/{}, {}".format(c, len(links), len(l_links)))
    # print(l_url, l_links)
    for l in l_links:
        try:
            # print(l, l_url)
            details = get_link_details("https://www.domofond.ru" + l, l_url)
            # print(details)

            gathered_info.append(details)
        except Exception as e:
            print(e)

        # break

    c += 1

    # sleep(0.5)
    # break

print(gathered_info)
put_in_db(gathered_info)
# update_gps_routelen()

