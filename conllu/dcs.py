#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 15:27:51 2021

@author: Hrishikesh Terdalkar
"""

from pathlib import Path

import conllu

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

###############################################################################


class DigitalCorpusSanskrit:
    def __init__(self, data_dir, scheme=sanscript.DEVANAGARI):
        self.data_dir = Path(data_dir)
        self.scheme = scheme

    def get_corpus(self):
        pass

    def get_chapter(self):
        pass

    def read_conllu(self, conllu_file):
        with open(conllu_file) as f:
            lines = conllu.parse(f.read())

        for line in lines:
            for token in line:
                token['form'] = transliterate(
                    token['form'], 'iast', self.scheme
                )
                token['lemma'] = transliterate(
                    token['lemma'], 'iast', self.scheme
                )
        return lines

###############################################################################


def main():
    home_dir = Path.home()
    data_dir = home_dir / 'git' / 'oliverhellwig' / 'dcs' / 'data' / 'conllu'
    DCS = DigitalCorpusSanskrit(data_dir=data_dir)

###############################################################################


if __name__ == '__main__':
    main()
