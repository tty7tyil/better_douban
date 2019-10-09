#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple
from bs4 import BeautifulSoup
from lib.crawler_requests import Crawler_Requests
from requests.exceptions import HTTPError
from requests.models import Response
from urllib.parse import urljoin

class Douban_Movie_Entry_List(object):
    def __init__(self, start_url, requester: Crawler_Requests = None):
        self.start_url = start_url
        self.requester = requester if (requester is not None) else Crawler_Requests()
        self.list: List[Douban_Movie_Entry] = []

    def fill_list(self):
        page = self.requester.get(self.start_url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        counter = 0
        while (True):
            # extract the item list in the page
            for item in page_soup.find_all('li', class_ = 'item'):
                # extract item info from list elements
                entry_property = item.find('a')
                title = entry_property.string.strip().split(' / ')
                title.reverse()
                entry = Douban_Movie_Entry(
                    title = title,
                    link = entry_property['href'],
                )
                self.list.append(entry)
                counter += 1
                print('#{:_>4} ENTRY ADDED: {}'.format(counter, repr(entry)))
            # check if there is 'next page'
            next_page_link = page_soup.find('span', class_ = 'next').find('a')
            if (next_page_link is not None):
                page = self.requester.get(urljoin(page.url, next_page_link['href']))
                page_soup = BeautifulSoup(page.text, 'html.parser')
            else:
                break

    def inspect_list(self):
        counter = 0
        for entry in self.list:
            counter += 1
            page = self.requester.get(entry.link)
            try:
                page.raise_for_status()
            except HTTPError as e:
                print(''.join([
                    '\n##{:_>4}## FETCH ENTRY PAGE FAILED: \'{}\''.format(counter, e),
                    str(entry),
                    '########\n',
                ]))
                continue
            else:
                entry.set_page(page)
                entry.set_page_soup(BeautifulSoup(entry.get_page().text, 'html.parser'))

            entry_info = entry.get_page_soup().find('div', id = 'info')
            try:
                date_info_list = entry_info.find_all('span', property = 'v:initialReleaseDate')
            except AttributeError as e:
                print(''.join([
                    '\n##{:_>4}## PARSE ENTRY INFO FAILED: \'{}\''.format(counter, e),
                    str(entry),
                    '########\n',
                ]))
                continue
            else:
                date_list = []
                for date in date_info_list:
                    date_list.append(
                        tuple(date.string.strip().replace(')', '').split('('))
                    )
                date_list.sort()
                entry.release_date = date_list
                print('#{:_>4} ENTRY DETAIL ADDED: {}'.format(counter, repr(entry)))
    
    def sort_list(self):
        pass

class Douban_Movie_Entry(object):
    def __init__(
        self, *,
        title: List[str] = [],
        link = '', imdb_link = '',
        release_date: List[Tuple[str, str]] = [],
        page: Response = None,
        page_soup: BeautifulSoup = None,
    ):
        self.title = title
        self.link = link
        self.imdb_link = imdb_link
        self.release_date = release_date
        self.__page = page
        self.__page_soup = page_soup

    def format_title(self) -> str:
        return ' / '.join(self.title)

    def format_release_date(self) -> str:
        return ' / '.join(
            [' '.join(date) for date in self.release_date]
        )

    def set_page(self, page: Response):
        self.__page = page
    def get_page(self) -> Response:
        return self.__page

    def set_page_soup(self, page_soup: BeautifulSoup):
        self.__page_soup = page_soup
    def get_page_soup(self) -> BeautifulSoup:
        return self.__page_soup

    def __repr__(self):
        if (len(self.title) != 0):
            title = '\'{}\''.format(self.format_title())
        else:
            title = 'EMPTY'

        if (len(self.release_date) != 0):
            release_date = '\'{}\''.format(self.format_release_date())
        else:
            release_date = 'EMPTY'

        return '<\'{class_}\'; title: {title}, release_date: {release_date}>'.format(
            class_ = self.__class__.__name__,
            title = title, release_date = release_date,
        )

    def __str__(self):
        link = '\'{}\''.format(self.link) if (self.link != '') else 'EMPTY'
        imdb_link = '\'{}\''.format(self.imdb_link) if (self.imdb_link != '') else 'EMPTY'
        page_status_code = self.__page.status_code if (self.__page is not None) else 'PAGE NOT FETCHED'
        return ''.join([
            '\n<{}>\n'.format(repr(self)),
            '-<Douban Link: {}>\n'.format(link),
            '-<IMDb Link  : {}>\n'.format(imdb_link),
            '-<Page Status: {}>\n'.format(page_status_code),
        ])
