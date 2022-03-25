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
# Itihāsa
# -------

# text_id = 143  # Rāmāyaṇa
# text_id = 154  # Mahābhārata

# Purāṇa
# ------

# # 01 # Brahmapurāṇa
# # 02 # Padmapurāṇa
# text_id = 400  # 03 # Viṣṇupurāṇa
# text_id = 344  # 04 # Śivapurāṇa
# text_id = 119  # 05 # Bhāgavatapurāṇa
# # 06 # Nāradapurāṇa
# # 07 # Mārkaṇdeyapurāṇa
# text_id = 388  # 08 # Agnipurāṇa
# # 09 # Bhaviṣyapurāṇa
# # 10 # Brahmavaivartapurāṇa
# text_id = 246  # 11 # Liṅgapurāṇa
# text_id = 342  # 12 # Varāhapurāṇa
# text_id = 140  # 13 # Skandapurāṇa
# text_id = 300  # 13 # Skandapurāṇa (Revākhaṇḍa)
# # 14 # Vāmanapurāṇa
# text_id = 350  # 15 # Kūrmapurāṇa
# text_id = 183  # 16 # Matsyapurāṇa
# text_id = 411  # 17 # Garuḍapurāṇa
# # 18 # Brahmāṇḍapurāṇa

# Upapurāṇa
# ---------
# text_id = 455  # Narasiṃhapurāṇa
# text_id = 306  # Kālikāpurāṇa

###############################################################################

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
