#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib import crawler_requests as cr
from lib import douban_movie_entry_list as dmel
from lib import mixed_unicode_align as mua

LIST_TYPE_COLLECT = 'collect'
LIST_TYPE_WISH = 'wish'
START_URL = 'https://movie.douban.com/people/{people_id}/{list_type}?start=0&sort=title&rating=all&filter=all&mode=list'

# set up sensitivy personal information
import sensitive_info
# set up sensitivy personal information

def main():
    list_wish = dmel.Douban_Movie_Entry_List(
        start_url = START_URL.format(
            people_id = sensitive_info.people_id,
            list_type = LIST_TYPE_WISH
        ),
        requester = cr.Crawler_Requests(
            proxy_list = sensitive_info.proxy_list,
            allow_request_without_proxy = True,
            sleep_time_range = (1, 2),
        ),
    )

    list_wish.fill_list()
    list_wish.inspect_list()

    for e in list_wish:
        print('{}{}'.format(
            mua.mixed_unicode_align('.', '<', 80,
            e.get_title(), resolve_as_wide = ['\u2026']
        ),
            e.get_release_date()
        ))

if (__name__ == '__main__'):
    main()
