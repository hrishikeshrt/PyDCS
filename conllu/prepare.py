#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 04 09:33:52 2023

@author: Hrishikesh Terdalkar
"""

###############################################################################

from bs4 import BeautifulSoup
from pathlib import Path


def prepare_texts_csv(path_to_chapter_info, path_to_texts_csv):
    content = Path(path_to_chapter_info).read_text()
    soup = BeautifulSoup(content, "html.parser")
    chapters = soup.find_all("chapter")
    texts = [["id", "textname"]] + sorted(
        set(
            (
                chapter.find("textid").get_text(),
                chapter.find("textname").get_text(),
            )
            for chapter in chapters
        ),
        key=lambda x: int(x[0]),
    )
    Path(path_to_texts_csv).write_text(
        "\n".join(",".join(row) for row in texts)
    )


###############################################################################
