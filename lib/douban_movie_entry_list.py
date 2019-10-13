#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  # guess i will just delete this line after python 4.0 ;)
from lib import crawler_requests as cr
from typing import Iterator, List, Tuple
from urllib import parse
import bs4
import requests.exceptions as r_exceptions
import requests.models as r_models

class Douban_Movie_Entry_List(object):
    def __init__(self, start_url: str, requester: cr.Crawler_Requests = None):
        self.start_url = start_url
        self.requester = requester if (requester is not None) else cr.Crawler_Requests()
        self._entry_list: List[Douban_Movie_Entry] = []

    def fill_list(self) -> None:
        page_count = 0
        page = self.requester.get(self.start_url)
        page_soup = bs4.BeautifulSoup(page.text, 'html.parser')
        page_count += 1
        entry_list = []
        while (True):
            # extract the item list in the page
            page_item_count = 0
            for item in page_soup.find_all('li', class_ = 'item'):
                # extract item info from list elements
                entry_property = item.find('a')
                title_list = entry_property.string.strip().split(' / ')
                title_list.reverse()
                entry = Douban_Movie_Entry(
                    title_list = title_list,
                    link = entry_property['href'],
                )
                entry_list.append(entry)
                page_item_count += 1
            # check if there is 'next page'
            print('LIST PAGE #_{} FETCHED, CONTAINS {} ITEM{plural}'.format(
                page_count,
                page_item_count,
                plural = 'S' if (1 < page_item_count) else '',
            ))
            next_page_link = page_soup.find('span', class_ = 'next').find('a')
            if (next_page_link is not None):
                page = self.requester.get(parse.urljoin(page.url, next_page_link['href']))
                page_soup = bs4.BeautifulSoup(page.text, 'html.parser')
                page_count += 1
            else:
                break

        for entry in self._entry_list[:]:
            if entry in entry_list:
                entry_list.remove(entry)
            else:
                self._entry_list.remove(entry)
                print('ENTRY REMOVED: {}'.format(repr(entry)))
        for entry in entry_list:
            print('ENTRY ADDED: {}'.format(repr(entry)))
        self._entry_list.extend(entry_list)

    def inspect_list(self, *, fetch_page_again = False) -> None:
        progress_counter = 0
        for entry in self:
            progress_counter += 1

            # fetch entry web page
            if ((entry.get_page() is None) or fetch_page_again):
                page = self.requester.get(entry.link)
                try:
                    page.raise_for_status()
                except r_exceptions.HTTPError as e:
                    print(''.join([
                        '\n##_{:_>{}}##'.format(progress_counter, len(str(len(self)))),
                        'FETCH ENTRY PAGE FAILED: \'{}\''.format(e),
                        str(entry),
                        '########\n',
                    ]))
                    continue
                else:
                    entry.set_page(page)
                    entry.set_page_soup(bs4.BeautifulSoup(entry.get_page().text, 'html.parser'))

            # check the necessity of extracting title from entry page
            if (len(entry._title_list) == 2):
                original_title_info = (
                    entry
                        .get_page_soup()
                        .find('span', property = 'v:itemreviewed')
                )
                original_title = (
                    original_title_info.string.strip()[len(entry._title_list[1]) + 1:]
                )
                entry._title_list[0] = original_title

            # extract entry info from entry page
            entry_info = entry.get_page_soup().find('div', id = 'info')
            try:
                date_info_list = entry_info.find_all('span', property = 'v:initialReleaseDate')
            except AttributeError as e:
                print(''.join([
                    '\n##_{:_>{}}##'.format(progress_counter, len(str(len(self)))),
                    'PARSE ENTRY INFO FAILED: \'{}\''.format(e),
                    str(entry),
                    '########\n',
                ]))
                continue
            else:
                date_list = []
                for date_info in date_info_list:
                    date_list.append(Douban_Movie_Entry.Release_Date(
                        *date_info.string.strip().replace(')', '').split('(')
                    ))
                date_list.sort()
                entry._release_date_list = date_list
                print('#_{:_>{}} ENTRY DETAIL ADDED: {}'.format(
                    progress_counter, len(str(len(self))),
                    repr(entry))
                )

    def sort_list(self, method = 'time', reverse = False) -> None:
        kwargs = {}
        if (method == 'title'):
            kwargs['key'] = lambda entry: entry._title_list
        self._entry_list.sort(**kwargs, reverse = reverse)

    def __iter__(self) -> Iterator[Douban_Movie_Entry]:
        return self._entry_list.__iter__()

    def __len__(self) -> int:
        return len(self._entry_list)

    def __getitem__(self, key: int) -> Douban_Movie_Entry:
        return self._entry_list[key]

    def __repr__(self) -> str:
        fetched_pages = 0
        for e in self:
            if (e.get_page() is not None):
                fetched_pages += 1

        return ''.join([
            '<{class_}; '.format(class_ = self.__class__.__name__),
            'contains {entry_count} entr{plural}, '.format(
                entry_count = len(self),
                plural = 'ies' if (1 < len(self)) else 'y',
            ),
            'fetched {fetched_pages} page{plural}>'.format(
                fetched_pages = fetched_pages,
                plural = 's' if (1 < fetched_pages) else '',
            ),
        ])

    def __str__(self) -> str:
        self_info = ''.join([
            '\n<{}>\n'.format(repr(self)),
            '-<Start URL: {}>\n'.format(self.start_url),
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
        page: r_models.Response = None,
        page_soup: bs4.BeautifulSoup = None,
    ):
        self._title_list = title_list
        self.link = link
        self.imdb_link = imdb_link
        self._release_date_list = release_date_list
        self.__page = page
        self.__page_soup = page_soup

    def get_title(self) -> str:
        return ' / '.join(self._title_list)

    def get_release_date(self) -> str:
        return ' / '.join([str(e) for e in self._release_date_list])

    def set_page(self, page: r_models.Response) -> None:
        self.__page = page
    def get_page(self) -> r_models.Response:
        return self.__page

    def set_page_soup(self, page_soup: bs4.BeautifulSoup) -> None:
        self.__page_soup = page_soup
    def get_page_soup(self) -> bs4.BeautifulSoup:
        return self.__page_soup

    def __lt__(self, other: Douban_Movie_Entry) -> bool:
        if (len(self._release_date_list) != 0):
            if (len(other._release_date_list) == 0):
                return True
            elif (self._release_date_list[0] < other._release_date_list[0]):
                return True
        else:
            return False

    def __eq__(self, other: Douban_Movie_Entry) -> bool:
        if (self.link == other.link):
            return True
        return False

    def __repr__(self) -> str:
        if (len(self._title_list) != 0):
            title = '\'{}\''.format(self.get_title())
        else:
            title = 'EMPTY'

        if (len(self._release_date_list) != 0):
            release_date = '\'{}\''.format(self.get_release_date())
        else:
            release_date = 'EMPTY'

        return '<{class_}; title: {title}, release_date: {release_date}>'.format(
            class_ = self.__class__.__name__,
            title = title, release_date = release_date,
        )

    def __str__(self) -> str:
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
        
        def __repr__(self) -> str:
            return '<rd(\'{}\', \'{}\')>'.format(self.date, self.territory)

        def __str__(self) -> str:
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
        def __lt__(self, other: Douban_Movie_Entry.Release_Date) -> bool:
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

        def __eq__(self, other: Douban_Movie_Entry.Release_Date) -> bool:
            ss, os = self._split_date(), other._split_date()
            if (len(ss) == len(os)):
                for i in range(len(ss)):
                    if (ss[i] != os[i]):
                        return False
                return True
            return False
