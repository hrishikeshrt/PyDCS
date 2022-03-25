from re import U


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dump words from text

@author: Hrishikesh Terdalkar
"""

###############################################################################

import sys
import json
from pathlib import Path

from tqdm import tqdm

###############################################################################

EXAMPLES_DIR = Path(__file__).resolve().parent
BASE_DIR = EXAMPLES_DIR.parent

sys.path.insert(0, str(BASE_DIR))

from dcs import DigitalCorpusSanskrit, TYPE_MODEL, model_to_dict
from config import DB_URL

###############################################################################

text_id = 154  # Mahābhārata
text_id = 143  # Rāmāyaṇa

###############################################################################

DCS = DigitalCorpusSanskrit(DB_URL, output_type=TYPE_MODEL)
chapters = DCS.get_chapters_from_text(text_id)
words = [
    [word.lexicon_id.word for word in line]
    for chapter in tqdm(chapters)
    for line in DCS.get_words_from_chapter(chapter, group_verse=True)
]

with open(EXAMPLES_DIR / f"words_{text_id}.json", "w") as f:
    json.dump(words, f, ensure_ascii=False)


###############################################################################
