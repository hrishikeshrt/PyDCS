#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 01 19:48:37 2022

@author: Hrishikesh Terdalkar


SQLAlchhemy Models for DCS Access

Models have been auto-generated using `sqlacodegen`
ForeignKey constraints are added manually on the relevant columns.
"""

###############################################################################

from sqlalchemy import Column, Integer, String, Text, text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref

# from sqlalchemy.ext.declarative import declarative_base

###############################################################################
# loading strategy

backref_lazy = "joined"

###############################################################################

Base = declarative_base()
metadata = Base.metadata

###############################################################################


class Lexicon(Base):
    __tablename__ = "lexicon"
    id = Column(
        Integer, primary_key=True, comment="= Access.Wortliste.ID, permanent"
    )
    word = Column(String(255), nullable=False, index=True)
    grammar = Column(String(20), nullable=False)
    sortkey = Column(Integer, nullable=False, index=True)
    first_letter = Column(String(5), index=True)
    first_two_letters = Column(String(5), index=True)
    language_id = Column(Integer, nullable=False)
    frequency = Column(Integer)


###############################################################################


class Texts(Base):
    __tablename__ = "texts"
    id = Column("ID", Integer, primary_key=True)
    textname = Column("Textname", String(255), nullable=False, index=True)
    author = Column("Verfasser", String(255))
    subtitle = Column("Untertitel", String(255))
    short = Column("Kuerzel", String(255))
    comment = Column("Kommentar", Integer)
    editor = Column("Herausgeber", String(255))
    publishing_place = Column("Erscheinungsort", String(255))
    publishing_year = Column("Erscheinungsjahr", Integer)
    publishing_company = Column("Verlag", String(255))
    line = Column("Reihe", String(255))
    digitizer = Column("Digitalisierer", String(255))
    language_id = Column("LanguageID", Integer, nullable=False, index=True)
    time_slot = Column("HabilEtym_TimeSlot", Integer)
    text_completed = Column("TextCompleted", Integer)
    nr_of_words = Column(
        "NrOfWords", Integer, comment="How many words in this text?"
    )
    managed_by = Column("ManagedBy", String(255))
    filename = Column("Filename", String(255))
    subject_id = Column("SubjectID", Integer)
    secondary_literature = Column(Integer)


class Chapters(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    text_id = Column(
        Integer, ForeignKey("texts.id"), nullable=False, index=True
    )
    name = Column(String(255), index=True)
    position = Column(Integer, nullable=False)
    nrevisions = Column(Integer)
    date_lower = Column(Integer)
    date_upper = Column(Integer)

    text = relationship(
        "Texts", backref=backref("chapters", lazy=backref_lazy)
    )


class TextLines(Base):
    __tablename__ = "text_lines"
    id = Column(Integer, primary_key=True)
    chapter_id = Column(
        Integer, ForeignKey("chapters.id"), nullable=False, index=True
    )
    line = Column(Text)
    stanza = Column(Integer, index=True)
    verse = Column("strophe", Integer, index=True)
    unsupervised = Column("Unsupervised", Integer)

    chapter = relationship(
        "Chapters", backref=backref("lines", lazy=backref_lazy)
    )


class VerbalDerivation(Base):
    __tablename__ = "verbal_derivation"
    id = Column(Integer, nullable=False, index=True, comment="not permanent")
    lexicon_id_parent = Column(
        Integer,
        nullable=False,
        index=True,
        comment="= Wortliste.ID of the parent verb",
    )
    lexicon_id_child = Column(
        Integer,
        nullable=False,
        index=True,
        comment="= Wortliste.ID of the derived verb",
    )
    derivation_type = Column(String(255), nullable=False)
    prefixes = Column(String(255))
    dummy = Column(Integer, primary_key=True)


class VerbalFormsFinite(Base):
    __tablename__ = "verbal_forms_finite"
    id = Column(
        Integer,
        primary_key=True,
        comment="permanent, = WortlisteVerbenVerbalformen.ID",
    )
    lexicon_id = Column(
        Integer,
        ForeignKey("lexicon.id"),
        nullable=False,
        index=True,
        comment="permanent, = dcs.lexicon.id",
    )
    form = Column(String(255), index=True)
    tense_mode = Column(Integer, index=True)
    person_number = Column(Integer)

    lexicon = relationship(
        "Lexicon", backref=backref("verbal_forms_finite", lazy=backref_lazy)
    )


class VerbalFormsInfinite(Base):
    __tablename__ = "verbal_forms_infinite"
    id = Column(
        Integer,
        primary_key=True,
        comment="permanent, = WortlisteVerbenVerbalformen.ID",
    )
    lexicon_id = Column(
        Integer,
        ForeignKey("lexicon.id"),
        nullable=False,
        index=True,
        comment="permanent, = dcs.lexicon.id",
    )
    form = Column(String(255), index=True)
    stem = Column(String(255))
    tense_mode = Column(Integer, index=True)
    noun_category = Column(Integer, nullable=False, index=True)

    lexicon = relationship(
        "Lexicon", backref=backref("verbal_forms_infinite", lazy=backref_lazy)
    )


class WordReferences(Base):
    __tablename__ = "word_references"
    id = Column(
        Integer,
        primary_key=True,
        comment="= Access.TexteintragAufloesung.ID, permanent",
    )
    lexicon_id = Column(
        Integer,
        ForeignKey("lexicon.id"),
        nullable=False,
        index=True,
        comment="= Access.Wortliste.ID, permanent",
    )
    sentence_id = Column(
        Integer,
        ForeignKey("text_lines.id"),
        nullable=False,
        index=True,
        comment="= dcs.sentences.id",
    )
    position = Column(Integer)
    inner_position = Column(Integer)
    verbal_form_finite_id = Column(
        Integer, ForeignKey("verbal_forms_finite.id"), index=True
    )
    verbal_form_infinite_id = Column(
        Integer, ForeignKey("verbal_forms_infinite.id"), index=True
    )
    absolute_position = Column(Integer, index=True)
    case_number_gender = Column(
        "CaseNumberGender",
        Integer,
        index=True,
        comment="c,n,g as a single number",
    )
    case = Column("cas", Integer, index=True, comment="case of a nominal form")
    nummber = Column(
        "num", Integer, index=True, comment="number of a nominal form"
    )
    gender = Column(
        "gen", Integer, index=True, comment="gender of a nominal form"
    )
    punctuation = Column(
        Integer,
        nullable=False,
        index=True,
        server_default=text("0"),
        comment="0=none,1=comma,2=full stop",
    )

    line = relationship(
        "TextLines", backref=backref("words"), lazy=backref_lazy
    )
    lexicon = relationship(
        "Lexicon", backref=backref("occurrences", lazy=backref_lazy)
    )
    verbal_form_finite = relationship(
        "VerbalFormsFinite", backref=backref("occurrences", lazy=backref_lazy)
    )
    verbal_form_infinite = relationship(
        "VerbalFormsInfinite",
        backref=backref("occurrences", lazy=backref_lazy),
    )


###############################################################################


class Meanings(Base):
    __tablename__ = "meanings"
    id = Column(Integer, primary_key=True)
    lexicon_id = Column(
        Integer, ForeignKey("lexicon.id"), nullable=False, index=True
    )
    meaning = Column(String(255), index=True)

    lexicon = relationship(
        "Lexicon", backref=backref("meanings", lazy=backref_lazy)
    )


class MeaningSource(Base):
    __tablename__ = "meaning_source"
    id = Column(Integer, primary_key=True)
    meaning_id = Column(Integer, nullable=False, index=True)
    text_id = Column(Integer, nullable=False, index=True)
    page_number = Column(String(255))

    # TODO: Consider if we need to add ForeignKey.


###############################################################################


class Headlines(Base):
    __tablename__ = "headlines"
    id_set = Column("IDSatz", Integer, nullable=False, index=True)
    headline = Column(String(255))
    dummy = Column(Integer, primary_key=True)


class Phrasesxtflags(Base):
    __tablename__ = "phrasesxtflags"
    id_phrase = Column("IDPhrase", Integer, nullable=False, index=True)
    position = Column("Position", Integer)
    flag = Column("Flag", Integer)
    dummy = Column(Integer, primary_key=True)


class Topics(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, comment="=Themen.ID")
    parent_id = Column(Integer, index=True)
    topic = Column(String(255), index=True)
    added_manually = Column(Integer, nullable=False, server_default=text("0"))


class TopicsReferences(Base):
    __tablename__ = "topics_references"
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, index=True)
    chapter_id = Column(Integer, index=True)
    added_manually = Column(Integer, nullable=False, server_default=text("0"))


###############################################################################
