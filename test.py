#!/usr/bin/env python3

from functions import proceed_page, get_tree, get_link_details, put_in_db, connect

url = "https://www.domofond.ru/arenda-odnokomnatnyh-kvartir-sankt_peterburg-c3414?PriceTo=16000&RentalRate=Month&Page={}"

tree = get_tree(url.format(1), "https://domofond.ru")

current_links = proceed_page(tree)

first_link = current_links[0]


# print(first_link)

d = get_link_details("https://www.domofond.ru" + first_link, url.format(1))

print(d)