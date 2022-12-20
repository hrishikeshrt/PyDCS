#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility for DCS CoNLL-U Data Parsing

@author: Hrishikesh Terdalkar
"""

from pathlib import Path
from typing import List, Dict

import conllu

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

###############################################################################


def parse_int(text: str) -> int or None:
    try:
        return int(float(text.strip()))
    except Exception:
        pass


###############################################################################


class CoNLLUParser:
    FIELDS = [
        "id",      # 01
        "form",    # 02 word form or punctuation symbol
        # if it contains multiple words, the annotation
        # follows the proposals for multiword annotation
        # (URL: format.html#words-tokens-and-empty-nodes)
        "lemma",   # 03 lemma or stem, lexical id of lemma is in column 10
        "upos",    # 04 universal POS tags
        "xpos",    # 05 language specific POS tags, described in `pos.csv`
        "feats",   # 06
        "head",    # 07
        "deprel",  # 08
        "deps",    # 09
        "misc"     # 10
        # Misc Fields

        # Digital Corpus of Sanskrit Specific Fields
        # LemmaId: matches first column of `dictionary.csv`
        # OccId: id of this occurence of the word
        # Unsandhied: Unsandhied word form (padapāṭha version)
        # WordSem: Ids of word semantic concepts, matches first column of
        #          `word-senses.csv`
        # Punctuation: [`comma`, `fullStop`] not part of original Sanskrit text
        #               but inserted in a separate layer
        # IsMantra: true if this word forms a part of a mantra as recorded in
        #           Bloomfield's Vedic Concordance
    ]
    TRANSLITERATE_METADATA_KEYS = ["text"]
    TRANSLITERATE_TOKEN_KEYS = ["form", "lemma"]
    RELEVANT_FIELDS = {
        "id": "",
        "form": "",
        "lemma": "",
        "upos": "",
        "xpos": "",
        "feats": {},
        "misc": {}
    }

    def __init__(
        self,
        input_scheme: str = sanscript.IAST,
        store_scheme: str = sanscript.DEVANAGARI,
        input_fields: List[str] = None,
        relevant_fields: Dict[str, str] = None,
        transliterate_metadata_keys: List[str] = None,
        transliterate_token_keys: List[str] = None
    ):
        """Corpus of CoNLL-U Files

        Parameters
        ----------
        input_scheme : str, optional
            Input transliteration scheme
            The default is `sanscript.IAST`
        store_scheme : str, optional
            Transliteration scheme used to store the corpus in the database
            The default is `sanscript.DEVANAGARI`
        fields : List[str], optional
            List of CoNLL-U Fields, if not standard
        relevant_fields : Dict[str, str], optional
            List of relevant CoNLL-U Fields to retain and their default  values
            in case they are missing
        transliterate_metadata_keys : List[str], optional
            List of metadata keys to transliterate
        transliterate_token_keys : List[str], optional
            List of token keys to transliterate
        """
        self.input_scheme = input_scheme
        self.store_scheme = store_scheme

        self.fields = self.FIELDS
        self.relevant_fields = self.RELEVANT_FIELDS
        self.transliterate_metadata_keys = self.TRANSLITERATE_METADATA_KEYS
        self.transliterate_token_keys = self.TRANSLITERATE_TOKEN_KEYS

        if input_fields is not None:
            self.fields = input_fields
        if relevant_fields is not None:
            self.relevant_fields = relevant_fields
        if transliterate_metadata_keys is not None:
            self.transliterate_metadata_keys = transliterate_metadata_keys
        if transliterate_token_keys is not None:
            self.transliterate_token_keys = transliterate_token_keys

    # ----------------------------------------------------------------------- #

    def parse_conllu(self, conllu_content: str):
        """
        Parse a CoNLL-U String

        Parameters
        ----------
        conllu_content : str
            Valid string of CoNLL-U Data

        Returns
        -------
        list
            List of lines
        """
        conllu_lines = [
            line
            for line in conllu.parse(conllu_content, fields=self.fields)
            if line
        ]

        # ------------------------------------------------------------------- #

        return self.transliterate_lines(conllu_lines)

    def parse_conllu_file(self, conllu_file: str or Path):
        """
        Parse a CoNLL-U File

        Parameters
        ----------
        conllu_file : str or Path
            Path to the CoNLL-U File

        Returns
        -------
        list
            List of lines
        """

        with open(conllu_file, encoding="utf-8") as f:
            content = f.read()

        return self.parse_conllu(content)

    # ----------------------------------------------------------------------- #

    def transliterate_lines(self, conllu_lines):
        """Transliterate CoNLL-U Data"""
        if self.store_scheme != self.input_scheme:
            for textline in conllu_lines:
                textline.metadata = self.transliterate_metadata(
                    textline.metadata
                )
                for token in textline:
                    token = self.transliterate_token(token)
        return conllu_lines

    def transliterate_metadata(self, metadata):
        """Transliterate Metadata"""
        if self.store_scheme == self.input_scheme:
            return metadata
        for key in self.transliterate_metadata_keys:
            if key not in metadata:
                continue
            metadata[key] = transliterate(
                metadata[key], self.input_scheme, self.store_scheme
            )
        return metadata

    def transliterate_token(self, token):
        """Transliterate Token"""
        if self.store_scheme == self.input_scheme:
            return token

        for key in self.transliterate_token_keys:
            if "." in key:
                _key, _subkey = key.split(".", 1)
            else:
                _key = key
                _subkey = None

            if _key not in token:
                continue

            if token[_key] is None:
                continue

            if _subkey is None:
                token[_key] = transliterate(
                    token[_key], self.input_scheme, self.store_scheme
                )
            else:
                if token[_key][_subkey] is None:
                    continue
                token[_key][_subkey] = transliterate(
                    token[_key][_subkey], self.input_scheme, self.store_scheme
                )
        return token

    # ----------------------------------------------------------------------- #

    # TODO:
    # * Can we remove dependence on sent_id, sent_counter ?
    # * Do we want to?

    def read_conllu_data(self, conllu_data: str):
        """
        Parse a CoNLL-U File
        Prepare it for Data Input (Group Verses etc)

        WARNING: The following metadata fields are required.
        * sent_id : Unique (global), Integer
        * sent_counter : Unique (local), Integer

        Parameters
        ----------
        conllu_data : object
            CoNLL-U Content
        """

        data = self.parse_conllu(conllu_data)
        chapter_lines = []

        for line in data:
            try:
                unit = {
                    "id": int(line.metadata["sent_id"]),
                    "verse_id": int(line.metadata["sent_counter"]),
                    "text": line.metadata["text"],
                    "tokens": [
                        {
                            _name: token.get(_name) or _default
                            for _name, _default in self.relevant_fields.items()
                        }
                        for token in line
                    ]
                }
                chapter_lines.append(unit)
            except Exception as e:
                print(line)
                raise e

        # Group verses
        verses = []
        last_verse_id = None
        for _line in chapter_lines:
            line_verse_id = _line.get("verse_id")
            if line_verse_id is None or line_verse_id != last_verse_id:
                last_verse_id = line_verse_id
                verses.append([])
            verses[-1].append(_line)

        return verses

    # ----------------------------------------------------------------------- #

###############################################################################
