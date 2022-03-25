#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 21:41:18 2020

@author: Hrishikesh Terdalkar

Utility Functions to deal with DCS Database (Rewritten as Class)

peewee library's model_to_dict() function from playhouse module is used
to create dictionary from models. It can recursively trace references and
back-links.
`reurse' and `backrefs' options are useful for tracing ForeignKey links.
http://docs.peewee-orm.com/en/latest/peewee/playhouse.html?highlight=model_to_dict
"""

from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict

from models import database_proxy, connection
from models import Texts, Chapters, TextLines, Lexicon, WordReferences
# from models import VerbalDerivation, VerbalFormsFinite, VerbalFormsInfinite

###############################################################################

TYPE_DICT = 'dict'
TYPE_MODEL = 'model'

###############################################################################


class DigitalCorpusSanskrit:
    def __init__(self, db_url, output_type=TYPE_DICT):
        database_proxy.initialize(connect(db_url))
        self.output_type = output_type

    @connection
    def get_lexicon(self, lexicon_id, output_type=None):
        if output_type is None:
            output_type = self.output_type
        lexicon = Lexicon.get_by_id(lexicon_id)
        if output_type == TYPE_DICT:
            return model_to_dict(lexicon)
        if output_type == TYPE_MODEL:
            return lexicon

    # ----------------------------------------------------------------------- #

    @connection
    def get_texts(self, output_type=None):
        if output_type is None:
            output_type = self.output_type
        fields = [Texts.id, Texts.textname, Texts.short]
        if output_type == TYPE_DICT:
            texts = (model_to_dict(text, only=fields) for text in Texts)
        if output_type == TYPE_MODEL:
            texts = Texts.select(*fields)
        return texts

    @connection
    def get_text(self, text_id, recurse=False, output_type=None):
        if output_type is None:
            output_type = self.output_type
        text = Texts.get_by_id(text_id)
        if output_type == TYPE_DICT:
            return model_to_dict(text, recurse=recurse)
        if output_type == TYPE_MODEL:
            return text

    # ----------------------------------------------------------------------- #

    @connection
    def get_chapters_from_text(self, text_id, output_type=None):
        if output_type is None:
            output_type = self.output_type
        text = Texts.get_by_id(text_id)
        if output_type == TYPE_DICT:
            chapters = (
                model_to_dict(chapter, recurse=False)
                for chapter in text.chapters.order_by(Chapters.position)
            )
        if output_type == TYPE_MODEL:
            chapters = text.chapters.order_by(Chapters.position)
        return chapters

    @connection
    def get_chapter(self, chapter_id, recurse=False, output_type=None):
        if output_type is None:
            output_type = self.output_type
        chapter = Chapters.get_by_id(chapter_id)
        if output_type == TYPE_DICT:
            return model_to_dict(chapter, recurse=recurse)
        if output_type == TYPE_MODEL:
            return chapter

    # ----------------------------------------------------------------------- #

    @connection
    def get_lines_from_chapter(self, chapter_id, output_type=None):
        if output_type is None:
            output_type = self.output_type
        chapter = Chapters.get_by_id(chapter_id)
        if output_type == TYPE_DICT:
            lines = (
                model_to_dict(line, recurse=False)
                for line in chapter.lines.order_by(TextLines.verse,
                                                   TextLines.stanza)
            )
        if output_type == TYPE_MODEL:
            lines = chapter.lines.order_by(TextLines.verse, TextLines.stanza)

        return lines

    @connection
    def get_lines_from_text(self, text_id, output_type=None):
        if output_type is None:
            output_type = self.output_type
        for chapter in self.get_chapters_from_text(text_id,
                                                   output_type=TYPE_MODEL):
            yield from self.get_lines_from_chapter(chapter.id, output_type)

    @connection
    def get_line(self, line_id, recurse=False, output_type=None):
        if output_type is None:
            output_type = self.output_type
        line = TextLines.get_by_id(line_id)
        if output_type == TYPE_DICT:
            return model_to_dict(line, recurse=recurse)
        if output_type == TYPE_MODEL:
            return line

    # ----------------------------------------------------------------------- #
    # NOTE: vese == list of lines

    @connection
    def get_verses_from_chapter(self, chapter_id, output_type=None):
        if output_type is None:
            output_type = self.output_type
        lines = self.get_lines_from_chapter(chapter_id, output_type=TYPE_MODEL)
        verse = []

        if output_type == TYPE_DICT:
            for line in lines:
                if not verse or verse[-1]['verse'] == line.verse:
                    verse.append(model_to_dict(line, recurse=False))
                else:
                    yield verse
                    verse = [model_to_dict(line, recurse=False)]
            yield verse

        if output_type == TYPE_MODEL:
            for line in lines:
                if not verse or verse[-1].verse == line.verse:
                    verse.append(line)
                else:
                    yield verse
                    verse = [line]
            yield verse

    @connection
    def get_verses_from_text(self, text_id, output_type=None):
        if output_type is None:
            output_type = self.output_type
        for chapter in self.get_chapters_from_text(text_id,
                                                   output_type=TYPE_MODEL):
            yield from self.get_verses_from_chapter(
                chapter.id, output_type=output_type
            )

    # ----------------------------------------------------------------------- #

    @connection
    def get_words_from_line(self, line_id, fetch_lexicon=False,
                            output_type=None):
        '''
        Get words from a Line

        Parameters
        ----------
        line_id : int
            Line ID
        fetch_lexicon : bool, optional
            If True, the lexcial information from Lexicon table is fetched
            This option is only valid with output_type TYPE_DICT.
            The default is False.
        output_type : str, optional
            Can be TYPE_MODEL or TYPE_DICT.
            If TYPE_MODEL, the "Words" returned are peewee Model objects.
            The default is TYPE_DICT.

        Returns
        -------
        words : list
            List of words (object or dict) from the specified Line
        '''
        if output_type is None:
            output_type = self.output_type
        line = TextLines.get_by_id(line_id)
        words = line.words.order_by(
            WordReferences.absolute_position, WordReferences.inner_position
        )
        if output_type == TYPE_DICT:
            if fetch_lexicon:
                output = []
                for word in words:
                    word_model = model_to_dict(word, False)
                    word_lexicon = self.get_lexicon(word_model['lexicon_id'])
                    word_model['word'] = word_lexicon['word']
                    word_model['grammar'] = word_lexicon['grammar']
                    output.append(word_model)
                return output
            else:
                return [model_to_dict(word, False) for word in words]
        if output_type == TYPE_MODEL:
            return words

    @connection
    def get_words_from_verse(self, lines, fetch_lexicon=False,
                             output_type=None):
        '''
        Get Words from a 'verse'

        A verse is a list of lines.
        In this function, a line is assumed to be in the model format.
        i.e. lines is an iterable of <TextLines: ..> objects
        '''
        if output_type is None:
            output_type = self.output_type
        return [word
                for line in lines
                for word in self.get_words_from_line(
                        line.id,
                        fetch_lexicon=fetch_lexicon,
                        output_type=output_type
                )]

    # ----------------------------------------------------------------------- #

    @connection
    def get_words_from_chapter(self, chapter_id, group_verse=False,
                               fetch_lexicon=False, output_type=None):
        '''
        Get Words from a chapter


        Parameters
        ----------
        chapter_id : int
            Chapter ID
        group_verse : bool, optional
            If True, the words from a verse are grouped together.
            Internally, this implies calling get_words_from_verse() function
            instead of calling get_words_from_line().
            The default is False.
        fetch_lexicon : bool, optional
            Argument is passed as is to the yielding function.
            The default is False.
        output_type : str, optional
            Can be TYPE_MODEL or TYPE_DICT.
            If TYPE_MODEL, the "Words" returned are peewee Model objects.
            The default is TYPE_DICT.

        Yields
        ------
        generator
            Words from chapter, optionally grouped by verse

        '''
        if output_type is None:
            output_type = self.output_type
        if group_verse:
            verses = self.get_verses_from_chapter(chapter_id,
                                                  output_type=TYPE_MODEL)
            for verse in verses:
                yield self.get_words_from_verse(
                    verse,
                    fetch_lexicon=fetch_lexicon,
                    output_type=output_type
                )
        else:
            lines = self.get_lines_from_chapter(chapter_id,
                                                output_type=TYPE_MODEL)
            for line in lines:
                yield self.get_words_from_line(
                    line.id,
                    fetch_lexicon=fetch_lexicon,
                    output_type=output_type
                )

    @connection
    def get_words_from_text(self, text_id, group_verse=False,
                            fetch_lexicon=False, output_type=None):
        '''
        Get words from a text

        Parameters
        ----------
        text_id : int
            Text ID
        group_verse : bool, optional
            If True, the words from a verse are grouped together.
            Internally, this implies calling get_words_from_verse() function
            instead of calling get_words_from_line().
            The default is False.
        fetch_lexicon : bool, optional
            Argument is passed as is to the yielding function.
            The default is False.
        output_type : str, optional
            Can be TYPE_MODEL or TYPE_DICT.
            If TYPE_MODEL, the "Words" returned are peewee Model objects.
            The default is TYPE_DICT.

        Yields
        ------
        generator
            Words from text, optionally grouped by verse
        '''
        if output_type is None:
            output_type = self.output_type
        if group_verse:
            verses = self.get_verses_from_text(text_id, output_type=TYPE_MODEL)
            for verse in verses:
                yield self.get_words_from_verse(
                    verse,
                    fetch_lexicon=fetch_lexicon,
                    output_type=output_type
                )
        else:
            for line in self.get_lines_from_text(text_id,
                                                 output_type=TYPE_MODEL):
                yield self.get_words_from_line(
                    line.id,
                    fetch_lexicon=fetch_lexicon,
                    output_type=output_type
                )

    # ----------------------------------------------------------------------- #

    @connection
    def get_word(self, word_id, recurse=True, output_type=None):
        '''
        Get details about a word from WordReferences

        Parameters
        ----------
        word_id : int
            Word ID as per WordReferences table
        recurse : bool, optional
            Recursively fetch objects from foreign-key links.
            This option makes sense only with the output_type as TYPE_DICT
            The default is True.
        output_type : str, optional
            Can be TYPE_MODEL or TYPE_DICT.
            If TYPE_MODEL, the "Words" returned are peewee Model objects.
            The default is TYPE_DICT.

        Returns
        -------
        word
            Word details (object or dict)
        '''
        if output_type is None:
            output_type = self.output_type
        word = WordReferences.get_by_id(word_id)
        if output_type == TYPE_DICT:
            return model_to_dict(word, recurse=recurse, max_depth=1)

        if output_type == TYPE_MODEL:
            return word

###############################################################################


def main():
    from config import DB_URL
    DCS = DigitalCorpusSanskrit(DB_URL)
    return locals()


###############################################################################


if __name__ == '__main__':
    locals().update(main())
