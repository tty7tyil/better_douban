#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

list_type_collect = 'collect'
list_type_wish = 'wish'
start_url = 'https://movie.douban.com/people/{people_id}/{list_type}?start=0&sort=title&rating=all&filter=all&mode=list'

def main():
    people_id = input('your personal douban id: ')
    list_wish = []
    page = requests.get(start_url.format(people_id = people_id, list_type = list_type_wish))
    page_soup = BeautifulSoup(page.text, 'html.parser')
    while (True):
        for e in page_soup.find_all('li', class_ = 'item'):
            entry = e.find('a')
            list_wish.append({
                'title': entry.string.strip(),
                'link': entry['href']
            })
        next_page_link = page_soup.find('span', class_ = 'next').find('a')
        if (next_page_link is not None):
            page = requests.get(urljoin(page.url, next_page_link['href']))
            page_soup = BeautifulSoup(page.text, 'html.parser')
        else:
            break

if (__name__ == '__main__'):
    main()
