#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 15:27:51 2021

@author: Hrishikesh Terdalkar
"""

from pathlib import Path

import conllu
import pandas as pd
from natsort import natsorted, ns

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

###############################################################################

TEXTS_PATH = "texts.csv"
TEXTS = pd.read_csv(TEXTS_PATH)

###############################################################################


class DigitalCorpusSanskrit:
    INTERNAL_SCHEME = sanscript.IAST
    FIELDS = [
        "id",  # 01
        "form",  # 02 word form or punctuation symbol
        # if it contains multiple words, the annotation
        # follows the proposals for multiword annotation
        # (URL: format.html#words-tokens-and-empty-nodes)
        "lemma",  # 03 lemma or stem, lexical id of lemma is in column 11
        "upos",  # 04
        "xpos",  # 05 language specific POS, described in `pos.csv`
        "feats",  # 06
        "head",  # 07
        "deprel",  # 08
        "deps",  # 09
        "misc",  # 10
        "lemma_id",  # 11 numeric, matches first column of `dictionary.csv`
        "unsandhied",  # 12
        "sense_id",  # 13 numeric, matches first column of `word-senses.csv`
    ]

    def __init__(self, data_dir, scheme=sanscript.DEVANAGARI):
        self.data_dir = Path(data_dir)
        self.scheme = scheme

    def get_corpus(self, corpus_id_or_name):
        for conllu_file in self.get_corpus_files(corpus_id_or_name):
            yield from self.read_conllu(conllu_file)

    def get_corpus_files(self, corpus_id_or_name):
        record = TEXTS.query(f"id == {corpus_id_or_name}")
        if record.empty:
            record = TEXTS.query(f"textname == {corpus_id_or_name}")

        if record.empty:
            print(f"Corpus not found: id/texname: '{corpus_id_or_name}'.")
            return

        corpus_name = record.iloc[0]["textname"]
        corpus_file = self.data_dir / "files" / f"{corpus_name}-all.conllu"
        corpus_path = self.data_dir / "files" / f"{corpus_name}"

        if corpus_file.is_file():
            return [corpus_file]

        if corpus_path.is_dir():
            return natsorted(corpus_path.glob("*.conllu"), alg=ns.PATH)

    def read_conllu(self, conllu_file, transliterate=False):
        with open(conllu_file, encoding="utf-8") as f:
            lines = conllu.parse(f.read(), fields=self.FIELDS)

        if transliterate:
            for line in lines:
                for token in line:
                    token = self.transliterate(token)
        return lines

    def transliterate(self, token):
        transliterate_keys = ["form", "lemma"]
        for key in transliterate_keys:
            token[key] = transliterate(
                token[key], self.INTERNAL_SCHEME, self.scheme
            )
        return token


###############################################################################


def main():
    home_dir = Path.home()
    data_dir = home_dir / "git" / "oliverhellwig" / "dcs" / "data" / "conllu"
    DCS = DigitalCorpusSanskrit(data_dir=data_dir)
    return locals()


###############################################################################


if __name__ == "__main__":
    locals().update(main())
