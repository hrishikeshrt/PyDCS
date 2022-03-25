#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dump details of all texts from DCS

@author: Hrishikesh Terdalkar
"""

###############################################################################

import sys
from pathlib import Path
import pandas as pd

EXAMPLES_DIR = Path(__file__).resolve().parent
BASE_DIR = EXAMPLES_DIR.parent

sys.path.insert(0, str(BASE_DIR))

from dcs import DigitalCorpusSanskrit, model_to_dict, TYPE_MODEL
from config import DB_URL

###############################################################################

DCS = DigitalCorpusSanskrit(DB_URL)
df = pd.DataFrame([
    model_to_dict(text)
    for text in DCS.get_texts(output_type=TYPE_MODEL)
])

# all columns
df.to_csv(EXAMPLES_DIR / "texts_details.csv", index=False)

# important columns
fields = ['id', 'textname', 'short', 'text_completed', 'nr_of_words']
df[fields].to_csv(EXAMPLES_DIR / "texts.csv", index=False)

###############################################################################
