#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  # guess i will just delete this line after python 4.0 ;)
from lib import crawler_requests as cr
from lib import douban_movie_entry as dme
from typing import Iterator, List
from urllib import parse
import bs4
import requests.exceptions as r_exceptions

class Douban_Movie_Entry_List(object):
    def __init__(self, start_url: str, requester: cr.Crawler_Requests = None):
        self.start_url = start_url
        self.requester = requester if (requester is not None) else cr.Crawler_Requests()
        self._entry_list: List[dme.Douban_Movie_Entry] = []

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
                entry = dme.Douban_Movie_Entry(
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
                    date_list.append(dme.Douban_Movie_Entry.Release_Date(
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

    def __iter__(self) -> Iterator[dme.Douban_Movie_Entry]:
        return self._entry_list.__iter__()

    def __len__(self) -> int:
        return len(self._entry_list)

    def __getitem__(self, key: int) -> dme.Douban_Movie_Entry:
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
