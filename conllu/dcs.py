#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 15:27:51 2021

@author: Hrishikesh Terdalkar
"""

from pathlib import Path
from typing import Dict, Tuple

import conllu
import pandas as pd
from natsort import natsorted, ns

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

from utils import parse_int

###############################################################################

BASE_DIR = Path(__file__).parent
TEXTS_PATH = BASE_DIR / "texts.csv"
TEXTS = pd.read_csv(TEXTS_PATH)

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


class DigitalCorpusSanskrit:
    INTERNAL_SCHEME = sanscript.IAST
    FIELDS = [
        "id",  # 01
        "form",  # 02 word form or punctuation symbol
        # if it contains multiple words, the annotation
        # follows the proposals for multiword annotation
        # (URL: format.html#words-tokens-and-empty-nodes)
        "lemma",  # 03 lemma or stem, lexical id of lemma is in column 11
        "upos",  # 04 universal POS tags
        "xpos",  # 05 language specific POS tags, described in `pos.csv`
        "feats",  # 06
        "head",  # 07
        "deprel",  # 08
        "deps",  # 09
        "misc",  # 10
        "lemma_id",  # 11 numeric, matches first column of `dictionary.csv`
        "unsandhied",  # 12
        "sense_id",  # 13 numeric, matches first column of `word-senses.csv`
    ]
    METADATA_INFO = {
        "text_line": "text",
        "text_line_id": "line_id",
        "text_line_counter": "chapter_verse_id",
        "text_line_subcounter": "verse_line_id",
    }

    def __init__(self, data_dir, scheme=sanscript.DEVANAGARI):
        self.data_dir = Path(data_dir)
        self.scheme = scheme

        dictionary_path = self.data_dir / "lookup" / "dictionary.csv"
        wordsenses_path = self.data_dir / "lookup" / "word-senses.csv"
        pos_path = self.data_dir / "lookup" / "pos.csv"

        self.dictionary = CSVData(
            dictionary_path, separator="\t", index_column="id"
        )
        self.wordsenses = CSVData(
            wordsenses_path, separator="\t", index_column="id"
        )
        self.pos = CSVData(pos_path, separator="\t", index_column="POS")

    def get_corpus(self, corpus_id_or_name: str):
        for conllu_file in self.get_corpus_files(corpus_id_or_name):
            yield from self.parse_conllu(conllu_file)

    def get_corpus_files(self, corpus_id_or_name):
        record = TEXTS.query(f"id == {corpus_id_or_name}")
        if record.empty:
            record = TEXTS.query(f"textname == '{corpus_id_or_name}'")

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

    def parse_conllu(self, dcs_conllu_file: str or Path):
        """Parse a DCS CoNLL-U File

        Parameters
        ----------
        dcs_conllu_file : str or Path
            Path to the DCS CoNLL-U File

        Returns
        -------
        list
            List of lines
        """

        with open(dcs_conllu_file, encoding="utf-8") as f:
            content = f.read()

        conllu_lines = [
            line
            for line in conllu.parse(
                content,
                fields=self.FIELDS,
                metadata_parsers={"__fallback__": self._metadata_parser}
            )
            if line
        ]

        if self.scheme != self.INTERNAL_SCHEME:
            for textline in conllu_lines:
                for token in textline:
                    token = self.transliterate_token(token)

        # ------------------------------------------------------------------- #

        return conllu_lines

    def transliterate_token(self, token):
        """Transliterate Token"""
        if self.scheme == self.INTERNAL_SCHEME:
            return token

        transliterate_keys = ["form", "lemma", "unsandhied"]
        for key in transliterate_keys:
            if key not in token:
                continue
            token[key] = transliterate(
                token[key], self.INTERNAL_SCHEME, self.scheme
            )
        return token

    def _metadata_parser(self, k: str, v: str) -> Tuple[str, str]:
        """Metadata Parser for `conllu.parse()`"""
        parts = k.split(":", 1)

        key = parts[0].strip()
        value = parts[1].strip()

        key = self.METADATA_INFO.get(key, key)

        if key == "text" and self.scheme != self.INTERNAL_SCHEME:
            value = transliterate(value, self.INTERNAL_SCHEME, self.scheme)

        if key in ["line_id", "chapter_verse_id", "verse_line_id"]:
            value = parse_int(value)

        return key, value

    def parse_metadata(self, content: str) -> Dict:
        """Parse Metadata from Comments

        Deprecated: Parse metadata with `conllu.parse()` by defining a custom
        parser (See: `_metadata_parser()`)

        Parameters
        ----------
        content : str
            Entire Content of DCS CoNLL-U File

        Returns
        -------
        Dict
            Metadata in a nested dictionary
        """

        # ------------------------------------------------------------------- #
        # Parse Metadata from Comments

        metadata = {}
        chapters = []
        chapter = None
        line = None

        for textline in content.split("\n"):
            # --------------------------------------------------------------- #
            # Chapter

            if textline.startswith("## chapter:"):
                if chapter:
                    chapters.append(chapter)

                chapter_title = textline.split(":", 1)[1].strip()
                chapter = {
                    "id": None,
                    "title": chapter_title,
                    "lines": []
                }

            if textline.startswith("## chapter_id:"):
                chapter["id"] = parse_int(textline.split(":", 1)[1])

            # --------------------------------------------------------------- #
            # Lines

            if textline.startswith("# text_line:"):
                line = {}
                line["text"] = textline.split(":", 1)[1].strip()
                if self.scheme != self.INTERNAL_SCHEME:
                    line["text"] = transliterate(
                        line["text"],
                        self.INTERNAL_SCHEME,
                        self.scheme
                    )
            if textline.startswith("# text_line_id:"):
                line_id = parse_int(textline.split(":", 1)[1])
                line["line_id"] = line_id
            if textline.startswith("# text_line_counter:"):
                verse_id = parse_int(textline.split(":", 1)[1])
                line["chapter_verse_id"] = verse_id
            if textline.startswith("# text_line_subcounter:"):
                verse_line_id = parse_int(textline.split(":", 1)[1])
                line["verse_line_id"] = verse_line_id
                chapter["lines"].append(line)

        # Append Final Chapter
        chapters.append(chapter)

        # ------------------------------------------------------------------- #

        metadata["chapters"] = chapters
        return metadata

###############################################################################


def main():
    home_dir = Path.home()
    data_dir = home_dir / "git" / "oliverhellwig" / "dcs" / "data" / "conllu"
    DCS = DigitalCorpusSanskrit(data_dir=data_dir)
    return locals()


###############################################################################


if __name__ == "__main__":
    locals().update(main())
