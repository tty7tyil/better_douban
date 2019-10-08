#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pickle
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List

list_type_collect = 'collect'
list_type_wish = 'wish'
start_url = 'https://movie.douban.com/people/{people_id}/{list_type}?start=0&sort=title&rating=all&filter=all&mode=list'

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
    page = requests.get(start_url.format(people_id = people_id, list_type = list_type))
    page_soup = BeautifulSoup(page.text, 'html.parser')
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
            print('ENTRY ADDED: {}'.format(repr(entry)))
        # check if there is 'next page'
        next_page_link = page_soup.find('span', class_ = 'next').find('a')
        if (next_page_link is not None):
            page = requests.get(urljoin(page.url, next_page_link['href']))
            page_soup = BeautifulSoup(page.text, 'html.parser')
        else:
            break

def inspect_list(list_: List[Douban_Movie_Entry]):
    for entry in list_:
        page = requests.get(entry.link)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        entry_info = page_soup.find('div', id = 'info')
        # TODO: if there exist multiple dates, should first sort them
        entry.release_date = ' / '.join([
            date.string.strip() for date in entry_info.find_all('span', property = 'v:initialReleaseDate')
        ])
        print('ENTRY DETAIL ADDED: {}'.format(repr(entry)))

def main():
    people_id = input('your personal douban id: ')

    list_wish = []
    fill_list(list_wish, list_type_wish, people_id)
    inspect_list(list_wish)

    # list_collect = []
    # fill_list(list_collect, list_type_collect, people_id)
    # inspect_list(list_collect)

    pickle.dumps(list_wish, open('list_wish.pickle', 'wb'))
    # pickle.dumps(list_collect, open('list_collect.pickle', 'wb'))

if (__name__ == '__main__'):
    main()
