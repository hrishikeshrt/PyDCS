#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility for DCS CoNLL-U Data Parsing

@author: Hrishikesh Terdalkar
"""

###############################################################################


def parse_int(text: str) -> int or None:
    try:
        return int(float(text.strip()))
    except Exception:
        pass
