#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:27:12 2020

@author: Hrishikesh Terdalkar

Models have been auto-generated using
$ python -m pwiz -e mysql -u dcs_user -P dcs_dbname >> models.py

ForeignKey constraints are added manually by converting the relevant
fields from IntegerField to ForeignKeyField

Fields are re-ordered for visual consistency with database.

SanskritCharField and SanskritTextField have been manually defined.
These extend CharField and TextField respectively.
The python_value() function enables us to display relevant fields from search
results in Devanagari.
Similarly, the db_value() function enables us to search relevant fields in
Devanagari.
"""

import functools
from peewee import (DatabaseProxy, Model, SQL,
                    IntegerField, CharField, TextField,
                    AutoField, ForeignKeyField)
from indic_transliteration.sanscript import transliterate

database_proxy = DatabaseProxy()

###############################################################################


def connection(func):
    '''Connect to a database before function call and exit afterwards'''

    # ----------------------------------------------------------------------- #
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        database_proxy.obj.close()
        database_proxy.obj.connect()
        try:
            result = func(*args, **kwargs)
        finally:
            database_proxy.obj.close()
        return result
    # ----------------------------------------------------------------------- #
    return wrapper

###############################################################################


class BaseModel(Model):
    class Meta:
        database = database_proxy

###############################################################################


class SanskritCharField(CharField):
    def db_value(self, value):
        return transliterate(value, 'devanagari', 'iast')

    def python_value(self, value):
        return transliterate(value, 'iast', 'devanagari')


class SanskritTextField(TextField):
    def db_value(self, value):
        return transliterate(value, 'devanagari', 'iast')

    def python_value(self, value):
        return transliterate(value, 'iast', 'devanagari')

###############################################################################


class Lexicon(BaseModel):
    word = SanskritCharField(index=True)
    grammar = CharField()
    sortkey = IntegerField(index=True)
    first_letter = CharField(index=True, null=True)
    first_two_letters = CharField(index=True, null=True)
    language_id = IntegerField()
    frequency = IntegerField(null=True)

    class Meta:
        table_name = 'lexicon'

###############################################################################


class Texts(BaseModel):
    id = AutoField(column_name='ID')
    textname = CharField(column_name='Textname', index=True)
    author = CharField(column_name='Verfasser', null=True)
    subtitle = CharField(column_name='Untertitel', null=True)
    short = CharField(column_name='Kuerzel', null=True)
    comment = IntegerField(column_name='Kommentar', null=True)
    editor = CharField(column_name='Herausgeber', null=True)
    publishing_place = CharField(column_name='Erscheinungsort', null=True)
    publishing_year = IntegerField(column_name='Erscheinungsjahr', null=True)
    publishing_company = CharField(column_name='Verlag', null=True)
    line = CharField(column_name='Reihe', null=True)
    digitizer = CharField(column_name='Digitalisierer', null=True)
    language_id = IntegerField(column_name='LanguageID', index=True)
    habil_etym_time_slot = IntegerField(
        column_name='HabilEtym_TimeSlot', null=True
    )
    text_completed = IntegerField(column_name='TextCompleted', null=True)
    nr_of_words = IntegerField(column_name='NrOfWords', null=True)
    managed_by = CharField(column_name='ManagedBy', null=True)
    filename = CharField(column_name='Filename', null=True)
    subject_id = IntegerField(column_name='SubjectID', null=True)
    secondary_literature = IntegerField(null=True)

    class Meta:
        table_name = 'texts'


class Chapters(BaseModel):
    text_id = ForeignKeyField(Texts, backref='chapters', index=True)
    name = CharField(index=True, null=True)
    position = IntegerField()
    nrevisions = IntegerField(null=True)
    date_lower = IntegerField(null=True)
    date_upper = IntegerField(null=True)

    class Meta:
        table_name = 'chapters'


class TextLines(BaseModel):
    chapter_id = ForeignKeyField(Chapters, backref='lines', index=True)
    line = SanskritTextField(null=True)
    stanza = IntegerField(index=True, null=True)
    verse = IntegerField(column_name='strophe', index=True, null=True)
    unsupervised = IntegerField(column_name='Unsupervised', null=True)

    class Meta:
        table_name = 'text_lines'


class VerbalDerivation(BaseModel):
    id = IntegerField(index=True)
    lexicon_id_parent = IntegerField(index=True)
    lexicon_id_child = IntegerField(index=True)
    derivation_type = CharField()
    prefixes = SanskritCharField(null=True)

    class Meta:
        table_name = 'verbal_derivation'
        primary_key = False


class VerbalFormsFinite(BaseModel):
    # lexicon_id = IntegerField(index=True)
    lexicon_id = ForeignKeyField(Lexicon, backref='finite_forms', index=True)
    form = SanskritCharField(index=True, null=True)
    tense_mode = IntegerField(index=True, null=True)
    person_number = IntegerField(null=True)

    class Meta:
        table_name = 'verbal_forms_finite'


class VerbalFormsInfinite(BaseModel):
    # lexicon_id = IntegerField(index=True)
    lexicon_id = ForeignKeyField(Lexicon, backref='finite_forms', index=True)
    form = SanskritCharField(index=True, null=True)
    stem = SanskritCharField(null=True)
    tense_mode = IntegerField(index=True, null=True)
    noun_category = IntegerField(index=True)

    class Meta:
        table_name = 'verbal_forms_infinite'


class WordReferences(BaseModel):
    lexicon_id = ForeignKeyField(Lexicon, backref='occurences', index=True)
    # lexicon_id = IntegerField(index=True)
    sentence_id = ForeignKeyField(TextLines, backref='words', index=True)
    position = IntegerField(null=True)
    inner_position = IntegerField(null=True)
    # verbal_form_finite_id = IntegerField(index=True, null=True)
    verbal_form_finite_id = ForeignKeyField(
        VerbalFormsFinite, backref='occurences', index=True, null=True
    )
    # verbal_form_infinite_id = IntegerField(index=True, null=True)
    verbal_form_infinite_id = ForeignKeyField(
        VerbalFormsInfinite, backref='occurences', index=True, null=True
    )
    absolute_position = IntegerField(index=True, null=True)
    case_number_gender = IntegerField(
        column_name='CaseNumberGender', index=True, null=True
    )
    case = IntegerField(index=True, column_name='cas', null=True)
    gender = IntegerField(index=True, column_name='gen', null=True)
    number = IntegerField(index=True, column_name='num', null=True)
    punctuation = IntegerField(constraints=[SQL("DEFAULT 0")], index=True)

    class Meta:
        table_name = 'word_references'


###############################################################################


class Meanings(BaseModel):
    lexicon_id = ForeignKeyField(Lexicon, backref='meanings', index=True)
    meaning = CharField(index=True, null=True)

    class Meta:
        table_name = 'meanings'


class MeaningSource(BaseModel):
    meaning_id = IntegerField(index=True)
    text_id = IntegerField(index=True)
    page_number = CharField(null=True)

    class Meta:
        table_name = 'meaning_source'

###############################################################################


class Headlines(BaseModel):
    id_set = IntegerField(column_name='IDSatz', index=True)
    headline = CharField(null=True)

    class Meta:
        table_name = 'headlines'
        primary_key = False


class Phrasesxtflags(BaseModel):
    id_phrase = IntegerField(column_name='IDPhrase', index=True)
    position = IntegerField(column_name='Position', null=True)
    flag = IntegerField(column_name='Flag', null=True)

    class Meta:
        table_name = 'phrasesxtflags'
        primary_key = False


class Topics(BaseModel):
    parent_id = IntegerField(index=True, null=True)
    topic = CharField(index=True, null=True)
    added_manually = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'topics'


class TopicsReferences(BaseModel):
    topic_id = IntegerField(index=True, null=True)
    chapter_id = IntegerField(index=True, null=True)
    added_manually = IntegerField(constraints=[SQL("DEFAULT 0")])

    class Meta:
        table_name = 'topics_references'

###############################################################################
