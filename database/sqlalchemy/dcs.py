#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DCS Class with utility methods to access various objects from DCS database

Created on Thu Sep 10 21:41:18 2020

@author: Hrishikesh Terdalkar
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from indic_transliteration import sanscript

from utils import model_to_dict, search_model
from models import BaseModel
from models import Texts, Chapters, TextLines, Lexicon, WordReferences

# from models import VerbalDerivation, VerbalFormsFinite, VerbalFormsInfinite

###############################################################################

TYPE_DICT = "dict"
TYPE_MODEL = "model"

DEFAULT_INPUT_SCHEME = sanscript.DEVANAGARI
DEFAULT_INTERNAL_SCHEME = sanscript.IAST

###############################################################################


class DigitalCorpusSanskrit:
    def __init__(
        self,
        db_url,
        base_model=BaseModel,
        input_scheme=DEFAULT_INPUT_SCHEME,
        internal_scheme=DEFAULT_INTERNAL_SCHEME,
        output_type=TYPE_DICT,
    ):
        self.engine = create_engine(db_url)
        self.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        self.base_model = base_model
        self.base_model.set_session(self.session)

        self.output_type = output_type

###############################################################################


def main():
    from config import DB_URL

    DCS = DigitalCorpusSanskrit(DB_URL)
    return locals()


###############################################################################


if __name__ == "__main__":
    locals().update(main())
