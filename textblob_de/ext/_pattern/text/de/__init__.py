#### PATTERN | DE ##################################################################################
# -*- coding: utf-8 -*-
# Copyright (c) 2012 University of Antwerp, Belgium
# Author: Tom De Smedt <tom@organisms.be>
# License: BSD (see LICENSE.txt for details).
# http://www.clips.ua.ac.be/pages/pattern

# Source: https://github.com/clips/pattern/pattern/text/de/__init__.py
# git-commit: 2014-05-10 (eb98cd7)

# Modified: 2014-08-04 Markus Killer <m.killer@langui.ch>

####################################################################################################
# German linguistical tools using fast regular expressions.
from __future__ import absolute_import
import os
import sys

try:
    MODULE = os.path.dirname(os.path.realpath(__file__))
except:
    MODULE = ""

sys.path.insert(0, os.path.join(MODULE, "..", "..", "..", ".."))

from _pattern.compat import text_type, string_types, basestring, imap, unicode

# Import parser base classes.
from _pattern.text import (
    Lexicon, Model, Morphology, Context, Parser as _Parser, ngrams, pprint, commandline,
    PUNCTUATION
)
# Import parser universal tagset.
from _pattern.text import (
    penntreebank2universal,
    PTB, PENN, UNIVERSAL,
    NOUN, VERB, ADJ, ADV, PRON, DET, PREP, ADP, NUM, CONJ, INTJ, PRT, PUNC, X
)
# Import parse tree base classes.
from _pattern.text.tree import (
    Tree, Text, Sentence, Slice, Chunk, PNPChunk, Chink, Word, table,
    SLASH, WORD, POS, CHUNK, PNP, REL, ANCHOR, LEMMA, AND, OR
)
# Import sentiment analysis base classes.
from _pattern.text import (
    Sentiment, NOUN, VERB, ADJECTIVE, ADVERB
)
# Import verb tenses.
from _pattern.text import (
    INFINITIVE, PRESENT, PAST, FUTURE,
    FIRST, SECOND, THIRD,
    SINGULAR, PLURAL, SG, PL,
    INDICATIVE, IMPERATIVE, SUBJUNCTIVE,
    PROGRESSIVE,
    PARTICIPLE, GERUND
)
# Import inflection functions.
from _pattern.text.de.inflect import (
    article, referenced, DEFINITE, INDEFINITE,
    pluralize, singularize, NOUN, VERB, ADJECTIVE,
    grade, comparative, superlative, COMPARATIVE, SUPERLATIVE,
    verbs, conjugate, lemma, lexeme, tenses,
    predicative, attributive,
    gender, MASCULINE, MALE, FEMININE, FEMALE, NEUTER, NEUTRAL, PLURAL, M, F, N, PL,
            NOMINATIVE, ACCUSATIVE, DATIVE, GENITIVE, SUBJECT, OBJECT, INDIRECT, PROPERTY
)
# Import all submodules.
from _pattern.text.de import inflect

sys.path.pop(0)

#--- GERMAN PARSER ---------------------------------------------------------------------------------
# The German parser (accuracy 96% for known words) is based on Schneider & Volk's language model:
# Schneider, G. & Volk, M. (1998). 
# Adding Manual Constraints and Lexical Look-up to a Brill-Tagger for German.
# Proceedings of the ESSLLI workshop on recent advances in corpus annotation. Saarbrucken, Germany.
# http://www.zora.uzh.ch/28579/

# The lexicon uses the Stuttgart/Tubinger Tagset (STTS):
# https://files.ifi.uzh.ch/cl/tagger/UIS-STTS-Diffs.html
STTS = "stts"
stts = tagset = {
      "ADJ": "JJ",
     "ADJA": "JJ",   # das große Haus
     "ADJD": "JJ",   # er ist schnell
      "ADV": "RB",   # schon
     "APPR": "IN",   # in der Stadt
  "APPRART": "IN",   # im Haus
     "APPO": "IN",   # der Sache wegen
     "APZR": "IN",   # von jetzt an
      "ART": "DT",   # der, die, eine
   "ARTDEF": "DT",   # der, die
   "ARTIND": "DT",   # eine
     "CARD": "CD",   # zwei
  "CARDNUM": "CD",   # 3
     "KOUI": "IN",   # [um] zu leben
     "KOUS": "IN",   # weil, damit, ob
      "KON": "CC",   # und, oder, aber
    "KOKOM": "IN",   # als, wie
     "KONS": "IN",   # usw.
       "NN": "NN",   # Tisch, Herr
      "NNS": "NNS",  # Tischen, Herren
       "NE": "NNP",  # Hans, Hamburg
      "PDS": "DT",   # dieser, jener
     "PDAT": "DT",   # jener Mensch
      "PIS": "DT",   # keiner, viele, niemand
     "PIAT": "DT",   # kein Mensch
    "PIDAT": "DT",   # die beiden Brüder
     "PPER": "PRP",  # ich, er, ihm, mich, dir
     "PPOS": "PRP$", # meins, deiner
   "PPOSAT": "PRP$", # mein Buch, deine Mutter
    "PRELS": "WDT",  # der Hund, [der] bellt
   "PRELAT": "WDT",  # der Mann, [dessen] Hund bellt
      "PRF": "PRP",  # erinnere [dich]
      "PWS": "WP",   # wer
     "PWAT": "WP",   # wessen, welche
     "PWAV": "WRB",  # warum, wo, wann
      "PAV": "RB",   # dafur, dabei, deswegen, trotzdem
    "PTKZU": "TO",   # zu gehen, zu sein
   "PTKNEG": "RB",   # nicht
    "PTKVZ": "RP",   # pass [auf]!
   "PTKANT": "UH",   # ja, nein, danke, bitte
     "PTKA": "RB",   # am schönsten, zu schnell 
    "VVFIN": "VB",   # du [gehst], wir [kommen] an
    "VAFIN": "VB",   # du [bist], wir [werden]
    "VVINF": "VB",   # gehen, ankommen
    "VAINF": "VB",   # werden, sein
    "VVIZU": "VB",   # anzukommen
    "VVIMP": "VB",   # [komm]!
    "VAIMP": "VB",   # [sei] ruhig!
     "VVPP": "VBN",  # gegangen, angekommen
     "VAPP": "VBN",  # gewesen
    "VMFIN": "MD",   # dürfen
    "VMINF": "MD",   # wollen
     "VMPP": "MD",   # gekonnt
     "SGML": "SYM",  #
       "FM": "FW",   #
      "ITJ": "UH",   # ach, tja
       "XY": "NN",   #
       "XX": "NN",   #
    "LINUM": "LS",   # 1.
        "C": ",",    # ,
       "Co": ":",    # :
       "Ex": ".",    # ! 
       "Pc": ")",    # )
       "Po": "(",    # (
        "Q": ".",    # ?
      "QMc": "\"",   # "
      "QMo": "\"",   # "
        "S": ".",    # .
       "Se": ":",    # ;
}

def stts2penntreebank(token, tag):
    """ Converts an STTS tag to a Penn Treebank II tag.
        For example: ohne/APPR => ohne/IN
    """
    return (token, stts.get(tag, tag))
    
def stts2universal(token, tag):
    """ Converts an STTS tag to a universal tag.
        For example: ohne/APPR => ohne/PREP
    """
    if tag in ("KON", "KOUI", "KOUS", "KOKOM"):
        return (token, CONJ)
    if tag in ("PTKZU", "PTKNEG", "PTKVZ", "PTKANT"):
        return (token, PRT)
    if tag in ("PDF", "PDAT", "PIS", "PIAT", "PIDAT", "PPER", "PPOS", "PPOSAT"): 
        return (token, PRON)
    if tag in ("PRELS", "PRELAT", "PRF", "PWS", "PWAT", "PWAV", "PAV"):
        return (token, PRON)
    return penntreebank2universal(*stts2penntreebank(token, tag))

#let's add some legal abbreviations, too
#let's also completely rule out at least simple ordinals
#let's also rule out anything that could be a date
ABBREVIATIONS = set((
    "Abs.", "Abt.", "Ass.", "Br.", "Ch.", "Chr.", "Cie.", "Co.", "Dept.", "Diff.", 
    "Dr.", "Eidg.", "Exp.", "Fam.", "Fr.", "Hrsg.", "Inc.", "Inv.", "Jh.", "Jt.", "Kt.", 
    "Mio.", "Mrd.", "Mt.", "Mte.", "Nr.", "Nrn.", "Ord.", "Ph.", "Phil.", "Pkt.", 
    "Prof.", "Pt.", " S.", "St.", "Stv.", "Tit.", "VII.", "al.", "begr.","bzw.", 
    "chem.", "dent.", "dipl.", "e.g.", "ehem.", "etc.", "excl.", "exkl.", "gem.", "hum.", 
    "i.e.", "incl.", "ing.", "inkl.", "int.", "iur.", "lic.", "med.", "no.", "oec.", 
    "phil.", "phys.", "pp.", "psych.", "publ.", "rer.", "sc.", "soz.", "spez.", "stud.", 
    "theol.", "usw.", "v.", "vet.", "vgl.", "vol.", "wiss.",
    "d.h.", "h.c.", u"o.ä.", "u.a.", "z.B.", "z.T.", "z.Zt.", "z. B.", "d. h.", "h. c.", 
    u"o. ä.", "u. a.", "z. B.", "z. T.", "z. Zt.",
    "BGBl.", "ABl.", "Bundesgesetzbl.", "BAnz.", "Dipl.-Ing.", "Ing.", "grad.", "bzgl.",
    "0.", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.", "13.",
    "14.", "15.", "16.", "17.", "18.", "19.", "20.", "21.", "22.", "23.", "24.", "25.", "26.",
    "27.", "28.", "29.", "30.", "31."
    
))

def find_lemmata(tokens):
    """ Annotates the tokens with lemmata for plural nouns and conjugated verbs,
        where each token is a [word, part-of-speech] list.
    """
    for token in tokens:
        word, pos, lemma = token[0], token[1], token[0]
        if pos.startswith(("DT", "JJ")):
            lemma = predicative(word)  
        if pos == "NNS":
            lemma = singularize(word)
        if pos.startswith(("VB", "MD")):
            lemma = conjugate(word, INFINITIVE) or word
        token.append(lemma.lower())
    return tokens
    
class Parser(_Parser):
    
    def find_tokens(self, tokens, **kwargs):
        kwargs.setdefault("abbreviations", ABBREVIATIONS)
        kwargs.setdefault("replace", {})
        return _Parser.find_tokens(self, tokens, **kwargs)
        
    def find_lemmata(self, tokens, **kwargs):
        return find_lemmata(tokens)
        
    def find_tags(self, tokens, **kwargs):
        if kwargs.get("tagset") in (PENN, None):
            kwargs.setdefault("map", lambda token, tag: stts2penntreebank(token, tag))
        if kwargs.get("tagset") == UNIVERSAL:
            kwargs.setdefault("map", lambda token, tag: stts2universal(token, tag))
        if kwargs.get("tagset") is STTS:
            kwargs.setdefault("map", lambda token,tag: (token, tag))
        # The lexicon uses Swiss spelling: "ss" instead of "ß".
        # We restore the "ß" after parsing.
        tokens_ss = [t.replace(u"ß", "ss") for t in tokens]
        tokens_ss = _Parser.find_tags(self, tokens_ss, **kwargs)
        return [[w] + tokens_ss[i][1:] for i, w in enumerate(tokens)]

parser = Parser(
     lexicon = os.path.join(MODULE, "de-lexicon.txt"),
   frequency = os.path.join(MODULE, "de-frequency.txt"),
  morphology = os.path.join(MODULE, "de-morphology.txt"),
     context = os.path.join(MODULE, "de-context.txt"),
     default = ("NN", "NE", "CARDNUM"),
    language = "de"
)

lexicon = parser.lexicon # Expose lexicon.

def tokenize(s, *args, **kwargs):
    """ Returns a list of sentences, where punctuation marks have been split from words.
    """
    return parser.find_tokens(s, *args, **kwargs)

def parse(s, *args, **kwargs):
    """ Returns a tagged Unicode string.
    """
    return parser.parse(s, *args, **kwargs)

def parsetree(s, *args, **kwargs):
    """ Returns a parsed Text from the given string.
    """
    return Text(parse(s, *args, **kwargs))

def tree(s, token=[WORD, POS, CHUNK, PNP, REL, LEMMA]):
    """ Returns a parsed Text from the given parsed string.
    """
    return Text(s, token)
    
def tag(s, tokenize=True, encoding="utf-8", **kwargs):
    """ Returns a list of (token, tag)-tuples from the given string.
    """
    tags = []
    for sentence in parse(s, tokenize, True, False, False, False, encoding, **kwargs).split():
        for token in sentence:
            tags.append((token[0], token[1]))
    return tags
    
def keywords(s, top=10, **kwargs):
    """ Returns a sorted list of keywords in the given string.
    """
    return parser.find_keywords(s, top=top, frequency=parser.frequency)

split = tree # Backwards compatibility.

#---------------------------------------------------------------------------------------------------
# python -m pattern.de xml -s "Ein Unglück kommt selten allein." -OTCL

if __name__ == "__main__":
    commandline(parse)
