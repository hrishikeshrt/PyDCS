#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 15:27:51 2021

@author: Hrishikesh Terdalkar
"""

from pathlib import Path

import pandas as pd
from natsort import natsorted, ns
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from utils import CoNLLUParser

###############################################################################

BASE_DIR = Path(__file__).parent
TEXTS_PATH = BASE_DIR / "texts.csv"
TEXTS = pd.read_csv(TEXTS_PATH)

###############################################################################

DCS_CONLLU_CONFIG = {
    "input_scheme": sanscript.IAST,
    "store_scheme": sanscript.DEVANAGARI,
    "input_fields": [
        "id",      # 01
        "form",    # 02 word form or punctuation symbol
        # if it contains multiple words, the annotation
        # follows the proposals for multi-word annotation
        # (URL: format.html#words-tokens-and-empty-nodes)
        "lemma",   # 03 lemma or stem
        "upos",    # 04 universal POS tags
        "xpos",    # 05 language specific POS tags
        "feats",   # 06 key-value
        "head",    # 07
        "deprel",  # 08
        "deps",    # 09
        "misc"     # 10 key-value
    ],
    "relevant_fields": {
        "id": "",
        "form": "",
        "lemma": "",
        "upos": "",
        "xpos": "",
        "feats": {},
        "misc": {}
    },
    # NOTE: data structure is modelled as Verse > Line > Token
    # line id is globally unique identifier (if any)
    # verse id is used to group lines together,
    # i.e., lines with same verse id are grouped together
    "metadata_field_line_text": "text",         # line text
    "metadata_field_line_id": "sent_id",        # line id (unique line id)
    "metadata_field_verse_id": "sent_counter",  # verse id (sentence id)
    "transliterate_metadata_keys": ["text"],
    "transliterate_token_keys": ["form", "lemma", "misc.Unsandhied"],
}


###############################################################################


class CSVData:
    def __init__(
        self,
        csv_path: str or Path,
        separator: str = ",",
        index_column: str = None,
    ):
        self.path = csv_path
        self.separator = separator
        self.data = pd.read_csv(csv_path, sep=separator, keep_default_na=False)
        if index_column:
            self.data = self.data.set_index(index_column)

    def get(self, id: int):
        try:
            return self.data.loc[id]
        except KeyError:
            pass

    def search(self, **kwargs):
        query = " and ".join(
            f"{key}.str.match('{value}')" for key, value in kwargs.items()
        )
        return self.data.query(query)

    def __iter__(self):
        yield from self.data.iterrows()

    def __repr__(self):
        return repr(self.data)


###############################################################################


class DigitalCorpusSanskrit(CoNLLUParser):
    def __init__(self, data_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_dir = Path(data_dir)

        dictionary_path = self.data_dir / "lookup" / "dictionary.csv"
        wordsenses_path = self.data_dir / "lookup" / "word-senses.csv"

        self.dictionary = CSVData(
            dictionary_path, separator="\t", index_column="id"
        )
        self.wordsenses = CSVData(
            wordsenses_path, separator="\t", index_column="id"
        )

    def get_corpus(self, corpus_id_or_name: str):
        for conllu_file in self.get_corpus_files(corpus_id_or_name):
            yield from self.parse_conllu_file(conllu_file)

    def find_corpus(self, corpus_name: str):
        transliterate_name = transliterate(
            corpus_name, self.store_scheme, self.input_scheme
        )
        record = TEXTS.query(
            f"textname.str.contains('(?i){transliterate_name}')",
            engine="python"
        )
        return [(t.id, t.textname) for t in record.itertuples()]

    def get_corpus_files(self, corpus_id_or_name):
        record = TEXTS.query(f"id == {corpus_id_or_name}")
        if record.empty:
            record = TEXTS.query(f"textname == '{corpus_id_or_name}'")

        if record.empty:
            print(f"Corpus not found: id/texname: '{corpus_id_or_name}'.")
            return

        corpus_name = record.iloc[0]["textname"]

        # corpus_file = self.data_dir / "files" / f"{corpus_name}-all.conllu"
        # if corpus_file.is_file():
        #     return [corpus_file]

        corpus_path = self.data_dir / "files" / f"{corpus_name}"
        if corpus_path.is_dir():
            return natsorted(corpus_path.glob("*.conllu"), alg=ns.PATH)


###############################################################################


def main():
    home_dir = Path.home()
    data_dir = home_dir / "git" / "oliverhellwig" / "dcs" / "data" / "conllu"
    scheme = sanscript.DEVANAGARI

    dcs_conllu_config = DCS_CONLLU_CONFIG.copy()
    dcs_conllu_config["store_scheme"] = scheme

    DCS_PARSER = DigitalCorpusSanskrit(data_dir=data_dir, **dcs_conllu_config)
    return locals()


###############################################################################


if __name__ == "__main__":
    locals().update(main())
