from lxml import html, etree
import requests


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
    r = requests.get(url)
    page_content = r.text
    return html.fromstring(page_content)


def get_link_details(url):

    r = requests.get(url)
    page_content = r.text
    tree = html.fromstring(page_content)

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
