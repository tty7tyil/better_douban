#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# guess i will just delete this line after python 4.0 ;)
from __future__ import annotations
from typing import List, Tuple
import bs4
import requests.models as r_models


class Douban_Movie_Entry(object):
    def __init__(
        self, *,
        title_list: List[str] = [],
        link: str = None, imdb_link: str = None,
        release_date_list: List[Douban_Movie_Entry.Release_Date] = [],
        douban_page: r_models.Response = None,
        douban_page_soup: bs4.BeautifulSoup = None,
    ):
        self._title_list = title_list
        self.link = link
        self.imdb_link = imdb_link
        self._release_date_list = release_date_list
        self.__douban_page = douban_page
        self.__douban_page_soup = douban_page_soup

    def get_title(self) -> str:
        return ' / '.join(self._title_list)

    def get_release_date(self) -> str:
        return ' / '.join([str(e) for e in self._release_date_list])

    def set_page(self, douban_page: r_models.Response) -> None:
        self.__douban_page = douban_page

    def get_page(self) -> r_models.Response:
        return self.__douban_page

    def set_page_soup(self, douban_page_soup: bs4.BeautifulSoup) -> None:
        self.__douban_page_soup = douban_page_soup

    def get_page_soup(self) -> bs4.BeautifulSoup:
        return self.__douban_page_soup

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

        return ''.join([
            '<{class_}; '.format(class_=self.__class__.__name__),
            'title: {title}, '.format(title=title),
            'release_date: {release_date}>'.format(release_date=release_date),
        ])

    def __str__(self) -> str:
        link = '\'{}\''.format(self.link) if (self.link != '') else 'EMPTY'
        imdb_link = '\'{}\''.format(self.imdb_link) if (
            self.imdb_link != '') else 'EMPTY'
        page_status_code = self.__douban_page.status_code if (
            self.__douban_page is not None) else 'PAGE NOT FETCHED'
        return ''.join([
            '\n<{}>\n'.format(repr(self)),
            '-<Douban Link: {}>\n'.format(link),
            '-<IMDb Link  : {}>\n'.format(imdb_link),
            '-<Page Status: {}>\n'.format(page_status_code),
        ])

    class Release_Date(object):
        class Territory(object):
            def __init__(self, territory: str):
                self.territory = territory

            def __repr__(self) -> str:
                return self.territory

            def classify(self) -> int:
                # WEB
                # Blu-ray
                # 首映
                # 点映
                # 电影节
                if ('中国' in self.territory):
                    return 0
                elif (
                    ('WEB' in self.territory)
                    or ('网络' in self.territory)
                ):
                    return 1
                elif ('Blu-ray' in self.territory):
                    return 2
                elif ('首映' in self.territory):
                    return 4
                elif ('点映' in self.territory):
                    return 5
                elif ('电影节' in self.territory):
                    return 6
                else:
                    return 3

            def __lt__(
                self,
                other: Douban_Movie_Entry.Release_Date.Territory
            ) -> bool:
                return self.classify() < other.classify()

            def __eq__(
                self,
                other: Douban_Movie_Entry.Release_Date.Territory
            ) -> bool:
                return self.classify() == other.classify()

        def __init__(
            self,
            date: str,
            territory: Douban_Movie_Entry.Release_Date.Territory = None
        ):
            self.date = date
            if (territory is not None):
                self.territory = (
                    Douban_Movie_Entry
                    .Release_Date
                    .Territory(territory)
                )
            else:
                self.territory = ''

        def __repr__(self) -> str:
            return '<rd(\'{}\', \'{}\')>'.format(self.date, self.territory)

        def __str__(self) -> str:
            if (str(self.territory) != ''):
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
        # if one of the two is missing some part and the rest has same value,
        # like `1111-22-33` and `1111-22`, **the one with missing parts is at
        # back**.
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
