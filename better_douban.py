#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List
from urllib.parse import urljoin
import pickle
import random
import requests
import time

LIST_TYPE_COLLECT = 'collect'
LIST_TYPE_WISH = 'wish'
START_URL = 'https://movie.douban.com/people/{people_id}/{list_type}?start=0&sort=title&rating=all&filter=all&mode=list'

# set up sensitivy personal information
people_id = ''
proxy_list = [
]
from sensitive_info import *
# set up sensitivy personal information

# web crawler disguise
fua = UserAgent()
def refresh_identity():
    global proxies, headers, cookies
    proxies = random.choice(proxy_list)
    headers = {
        'Referer': 'https://movie.douban.com/',
        'User-Agent': fua.chrome,
    }
    cookies = requests.get(
        headers['Referer'],
        headers = headers, proxies = proxies
    ).cookies
    time.sleep(random.random() * 5 + 3)

proxies = {
}
headers = {
}
cookies = requests.cookies.RequestsCookieJar()

refresh_identity()
# web crawler disguise

class Douban_Movie_Entry(object):
    def __init__(self, *, title = '', link = '', release_date = '', imdb_link = ''):
        self.title = title
        self.link = link
        self.release_date = release_date
        self.imdb_link = imdb_link

    def __repr__(self):
        title = '\'{}\''.format(self.title) if (self.title != '') else 'EMPTY'
        release_date = '\'{}\''.format(self.release_date) if (self.release_date != '') else 'EMPTY'
        return '<\'{class_}\'; title: {title}, release_date: {release_date}>'.format(
            class_ = self.__class__.__name__,
            title = title, release_date = release_date,
        )

    def __str__(self):
        link = '\'{}\''.format(self.link) if (self.link != '') else 'EMPTY'
        imdb_link = '\'{}\''.format(self.imdb_link) if (self.imdb_link != '') else 'EMPTY'
        return ''.join([
            '{}\n'.format(repr(self)),
            'Douban Link: {}\n'.format(link),
            'IMDb Link  : {}\n'.format(imdb_link),
        ])

def fill_list(list_: list, list_type: str, people_id: str):
    page = requests.get(
        START_URL.format(people_id = people_id, list_type = list_type),
        headers = headers, cookies = cookies, proxies = proxies,
    )
    time.sleep(random.random() * 5 + 3)
    page_soup = BeautifulSoup(page.text, 'html.parser')
    counter = 0
    while (True):
        # extract the item list in the page
        for item in page_soup.find_all('li', class_ = 'item'):
            # extract item info from list elements
            entry_property = item.find('a')
            entry = Douban_Movie_Entry(
                title = entry_property.string.strip(),
                link = entry_property['href'],
            )
            list_.append(entry)
            counter += 1
            print('#{:_>4} ENTRY ADDED: {}'.format(counter, repr(entry)))
        # check if there is 'next page'
        next_page_link = page_soup.find('span', class_ = 'next').find('a')
        if (next_page_link is not None):
            page = requests.get(
                urljoin(page.url, next_page_link['href']),
                headers = headers, cookies = cookies, proxies = proxies,
            )
            time.sleep(random.random() * 5 + 3)
            page_soup = BeautifulSoup(page.text, 'html.parser')
        else:
            break

def inspect_list(list_: List[Douban_Movie_Entry]):
    counter = 0
    for entry in list_:
        page = requests.get(
            entry.link,
            headers = headers, cookies = cookies, proxies = proxies,
        )
        time.sleep(random.random() * 5 + 3)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        entry_info = page_soup.find('div', id = 'info')
        # TODO: if there exist multiple dates, should first sort them
        entry.release_date = ' / '.join([
            date.string.strip() for date in entry_info.find_all('span', property = 'v:initialReleaseDate')
        ])
        counter += 1
        print('#{:_>4} ENTRY DETAIL ADDED: {}'.format(counter, repr(entry)))

def main():
    # list_collect = []
    # fill_list(list_collect, LIST_TYPE_COLLECT, people_id)
    # refresh_identity()
    # inspect_list(list_collect)

    list_wish = []
    fill_list(list_wish, LIST_TYPE_WISH, people_id)
    refresh_identity()
    inspect_list(list_wish)

    # pickle.dumps(list_collect, open('list_collect.pickle', 'wb'))
    pickle.dumps(list_wish, open('list_wish.pickle', 'wb'))

if (__name__ == '__main__'):
    main()
