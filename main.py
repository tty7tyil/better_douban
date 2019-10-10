#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.crawler_requests import Crawler_Requests
from lib.douban_movie_entry_list import Douban_Movie_Entry_List
import os
import pickle

LIST_TYPE_COLLECT = 'collect'
LIST_TYPE_WISH = 'wish'
START_URL = 'https://movie.douban.com/people/{people_id}/{list_type}?start=0&sort=title&rating=all&filter=all&mode=list'

# set up sensitivy personal information
people_id = ''
proxy_list = [
]
from sensitive_info import *
# set up sensitivy personal information

def main():
    list_wish = Douban_Movie_Entry_List(
        start_url = START_URL.format(
            people_id = people_id,
            list_type = LIST_TYPE_WISH
        ),
        requester = Crawler_Requests(
            proxy_list = proxy_list,
            sleep_time_range = (0, 1, ),
        ),
    )
    list_wish_file = open('list_wish.pickle', 'wb')

    list_wish.fill_list()
    pickle.dump(list_wish.list, list_wish_file)
    print(''.join([
        '\n################\n',
        'WISH LIST FILLED\n',
        '################\n'
    ]))

    list_wish.inspect_list()
    pickle.dump(list_wish.list, list_wish_file)
    print(''.join([
        '\n###################\n',
        'WISH LIST INSPECTED\n',
        '###################\n'
    ]))

    list_wish_file.close()

if (__name__ == '__main__'):
    main()
