#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import unicodedata as ucd

# Details about Unicode East Asian Width can be found at:
# [UAX #11: East Asian Width](https://www.unicode.org/reports/tr11/tr11-36.html)

def mixed_unicode_align(
    fill: str, align: str, width: int,
    string: str, *,
    ambiguous_always_wide: bool = False,
    resolve_as_wide: List[str] = [],
) -> str:
    # make sure `fill` and `align` is character
    ord(fill)
    ord(align)

    if (ambiguous_always_wide):
        wide = 'FWA'
    else:
        wide = 'FW'

    fullwidth_or_wide = 0
    for c in string:
        if (ucd.east_asian_width(c) in wide):
            fullwidth_or_wide += 1
        elif (c in resolve_as_wide):
            fullwidth_or_wide += 1

    return '{string:{fill}{align}{width}}'.format(
        fill = fill, align = align,
        width = width - fullwidth_or_wide,
        string = string
    )
