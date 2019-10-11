#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  # guess i will just delete this line after python 4.0 ;)
from bs4 import BeautifulSoup
from lib.crawler_requests import Crawler_Requests
from requests.exceptions import HTTPError
from requests.models import Response
from typing import List, Tuple
from urllib.parse import urljoin

class Douban_Movie_Entry_List(object):
    def __init__(self, start_url: str, requester: Crawler_Requests = None):
        self.start_url = start_url
        self.requester = requester if (requester is not None) else Crawler_Requests()
        self.entry_list: List[Douban_Movie_Entry] = []

    def fill_list(self):
        page = self.requester.get(self.start_url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        progress_counter = 0
        while (True):
            # extract the item list in the page
            for item in page_soup.find_all('li', class_ = 'item'):
                # extract item info from list elements
                entry_property = item.find('a')
                title_list = entry_property.string.strip().split(' / ')
                title_list.reverse()
                entry = Douban_Movie_Entry(
                    title_list = title_list,
                    link = entry_property['href'],
                )
                self.entry_list.append(entry)
                progress_counter += 1
                print('#_{} ENTRY ADDED: {}'.format(progress_counter, repr(entry)))
            # check if there is 'next page'
            next_page_link = page_soup.find('span', class_ = 'next').find('a')
            if (next_page_link is not None):
                page = self.requester.get(urljoin(page.url, next_page_link['href']))
                page_soup = BeautifulSoup(page.text, 'html.parser')
            else:
                break

    def inspect_list(self, *, fetch_page_again = False):
        progress_counter = 0
        for entry in self:
            progress_counter += 1
            if ((entry.get_page() is None) or fetch_page_again):
                page = self.requester.get(entry.link)
                try:
                    page.raise_for_status()
                except HTTPError as e:
                    print(''.join([
                        '\n##_{:_>{}}##'.format(progress_counter, len(str(len(self)))),
                        'FETCH ENTRY PAGE FAILED: \'{}\''.format(e),
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
                    '\n##_{:_>{}}}##'.format(progress_counter, len(str(len(self)))),
                    'PARSE ENTRY INFO FAILED: \'{}\''.format(e),
                    str(entry),
                    '########\n',
                ]))
                continue
            else:
                date_list = []
                for date in date_info_list:
                    date_list.append(Douban_Movie_Entry.Release_Date(
                        *date.string.strip().replace(')', '').split('(')
                    ))
                date_list.sort()
                entry.release_date_list = date_list
                print('#_{:_>{}} ENTRY DETAIL ADDED: {}'.format(
                    progress_counter, len(str(len(self))),
                    repr(entry))
                )

    def sort_list(self, method = 'time', reverse = False):
        kwargs = {}
        if (method == 'title'):
            kwargs['key'] = lambda entry: entry.title_list
        self.entry_list.sort(**kwargs, reverse = reverse)

    def __iter__(self):
        return self.entry_list.__iter__()

    def __len__(self):
        return len(self.entry_list)

    def __getitem__(self, key: int):
        return self.entry_list[key]

    def __repr__(self):
        fetched_pages = 0
        for e in self:
            if (e.get_page() is not None):
                fetched_pages += 1

        return ''.join([
            '<{class_}; '.format(class_ = self.__class__.__name__),
            'contain {entry_count} entry(s), '.format(entry_count = len(self)),
            'fetched {fetched_pages} page(s)>'.format(fetched_pages = fetched_pages),
        ])

    def __str__(self):
        self_info = ''.join([
            '\n<{}>\n'.format(repr(self)),
            '-<Start URL    : {}>\n'.format(self.start_url),
        ])
        entry_list_info = ''
        progress_counter = 0
        for e in self:
            progress_counter += 1
            entry_info = repr(e).split('; ')[1].split(', r')
            entry_list_info = ''.join([
                entry_list_info,
                '--<#_{:_>{}} {}\n'.format(
                    progress_counter, len(str(len(self))),
                    entry_info[0]
                ),
                '-- r{}\n'.format(entry_info[1]),
            ])

        return ''.join([self_info, entry_list_info])

class Douban_Movie_Entry(object):
    def __init__(
        self, *,
        title_list: List[str] = [],
        link: str = None, imdb_link: str = None,
        release_date_list: List[Douban_Movie_Entry.Release_Date] = [],
        page: Response = None,
        page_soup: BeautifulSoup = None,
    ):
        self.title_list = title_list
        self.link = link
        self.imdb_link = imdb_link
        self.release_date_list = release_date_list
        self.__page = page
        self.__page_soup = page_soup

    def format_title(self) -> str:
        return ' / '.join(self.title_list)

    def format_release_date_list(self) -> str:
        return ' / '.join([str(e) for e in self.release_date_list])

    def set_page(self, page: Response):
        self.__page = page
    def get_page(self) -> Response:
        return self.__page

    def set_page_soup(self, page_soup: BeautifulSoup):
        self.__page_soup = page_soup
    def get_page_soup(self) -> BeautifulSoup:
        return self.__page_soup

    def __lt__(self, other: Douban_Movie_Entry):
        if (len(self.release_date_list) != 0):
            if (len(other.release_date_list) == 0):
                return True
            elif (self.release_date_list[0] < other.release_date_list[0]):
                return True
        else:
            return False

    def __eq__(self, other: Douban_Movie_Entry):
        if (self.link == other.link):
            return True
        return False

    def __repr__(self):
        if (len(self.title_list) != 0):
            title = '\'{}\''.format(self.format_title())
        else:
            title = 'EMPTY'

        if (len(self.release_date_list) != 0):
            release_date = '\'{}\''.format(self.format_release_date_list())
        else:
            release_date = 'EMPTY'

        return '<{class_}; title: {title}, release_date: {release_date}>'.format(
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

    class Release_Date(object):
        def __init__(self, date: str, territory: str = None):
            self.date = date
            self.territory = territory
        
        def __repr__(self):
            return '<rd(\'{}\', \'{}\')>'.format(self.date, self.territory)

        def __str__(self):
            if (self.territory is not None):
                return '{} ({})'.format(self.date, self.territory)
            else:
                return self.date

        def _split_date(self) -> Tuple[int, int, int]:
            return tuple([int(e) for e in self.date.split('-')])

        # date_string format: `yyyy-mm-dd`,
        # day or month and day can be missing.
        #
        # comparison rule (ascending):
        # compare numerical value form y to m to d, **greater is at back**.
        # if one of the two is missing some part and the rest has same value, like
        # `1111-22-33` and `1111-22`, **the one with missing parts is at back**.
        def __lt__(self, other: Douban_Movie_Entry.Release_Date):
            ss, os = self._split_date(), other._split_date()
            less_than_by_length = True
            for i in range(min(len(ss), len(os))):
                if (ss[i] < os[i]):
                    return True
                elif (ss[i] > os[i]):
                    return False
            if (len(ss) <= len(os)):
                less_than_by_length = False
            return less_than_by_length

        def __eq__(self, other: Douban_Movie_Entry.Release_Date):
            ss, os = self._split_date(), other._split_date()
            if (len(ss) == len(os)):
                for i in range(len(ss)):
                    if (ss[i] != os[i]):
                        return False
                return True
            return False
