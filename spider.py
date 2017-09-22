from functions import proceed_page, get_tree, get_link_details
from lxml.etree import fromstring

url = "https://www.domofond.ru/arenda-kvartiry-sankt_peterburg-c3414?PriceTo=16000&RentalRate=Month&Rooms=One&Page={}"
tree = get_tree(url.format(1))

# get pages count
pages_container = tree.xpath('//div[@class = "b-pager"]/ul/li[last()]')[0]
pages_count = int(pages_container.text_content())

# get current page links
links = proceed_page(tree)

print('Total pages:', pages_count)

# get links from all other pages
# for pc in range(2, pages_count + 1):
#     print('Gathering ', pc, '\r')
#     current_url = url.format(pc)
#     current_tree = get_tree(current_url)
#     current_links = proceed_page(current_tree)
#     links += current_links

links = list(set(links))

gathered_info = []

c = 1
for l in links:
    print(c, '/', len(links), l)
    details = get_link_details("https://www.domofond.ru" + l)
    gathered_info.append(details)

    c += 1


print(gathered_info)