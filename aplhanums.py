#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import Counter


def aplhanum_check(segments):
    '''
    Function for checking for missing reference numbers which often
    appear in Japanese patent texts, such as '100a' and '240B'.
    '''

    # Extract reference numbers from Japanese and English text
    segments = collect_Jap_aplhanums(segments)
    segments = collect_Eng_aplhanums(segments)

    # Look for missing and extra reference numbers
    for segment in segments:

        # Identifies number of instances of each reference number
        jap_aplhanums = Counter(segment.jap_aplhanums)
        eng_aplhanums = Counter(segment.eng_aplhanums)

        # Compares reference number instances between Jap and Eng
        segment.missing_aplhanums = jap_aplhanums - eng_aplhanums
        segment.extra_aplhanums = eng_aplhanums - jap_aplhanums

        # Raise error flag if necessary
        if segment.missing_aplhanums:
            segment.error_found = True
        if segment.extra_aplhanums:
            segment.error_found = True

    return segments


def collect_Jap_aplhanums(segments):
    '''
    Function for extracting reference numbers from Japanese text.
    '''

    # Units to be ignored
    units = ['km', 'm', 'cm', 'mm', 'nm', 'mg', 'ml', 'kw', 'kwh',
             'kg', 'kl', 'km', 'µg', 'µm', 'mm2', 'm2', 'cm2',
             'mm3', 'm3', 'cm3', 'kb', 'gb', 'mb', 'pm', 'ns',
             'ms', 'mw', 'mwh', 'gw', 'gwh']

    # Break Japanese text down into substrings
    for segment in segments:
        jap_text = strip_Japanese_chars(segment.jap_text)
        jap_text = clean_string(jap_text)
        jap_subs = jap_text.split()

        # Extract reference numbers from substrings
        for sub in jap_subs:
            # If contains at least one alphabet letter and at least one number
            if aplhanum_identify(sub):
                # Ignore digits followed by measurement units
                includes_unit = False
                for unit in units:
                    if sub.endswith(unit):
                        includes_unit = True
                if not includes_unit:
                    segment.jap_aplhanums.append(sub)

    return segments


def collect_Eng_aplhanums(segments):
    '''
    Function for extracting reference numbers from English text.
    '''

    # Ordinals are to be ignored
    ordinals = ['1st', '2nd', '3rd', '4th', '5th',
                '6th', '7th', '8th', '9th', '10th',
                '11th', '12th', '13th', '14th', '15th',
                '16th', '17th', '18th', '19th', '20th']

    for segment in segments:
        eng_text = clean_string(segment.eng_text)
        eng_words = eng_text.split()
        for word in eng_words:
            if aplhanum_identify(word):
                if word not in ordinals:
                    segment.eng_aplhanums.append(word)

    return segments


def aplhanum_identify(substring):
    '''
    BUG - some reference numbers don't include digits, such as 'BP'
    '''
    '''
    Function for identifying substrings that contain at least one letter
    and at least one number. These are treated as reference numbers.
    '''
    letter_present = False
    number_present = False
    for letter in substring:
        if letter.isalpha():
            letter_present = True
        if letter.isdigit():
            number_present = True
    if letter_present and number_present:
        return True
    else:
        return False

'''
CHECK WORDCOUNT_ANNOTATED.PY IS_ASIAN() AND FILTER_JCHARS() FOR A BETTER WAY

def is_asian(char):
    ideographic_space = 0x3000
    return ord(char) > ideographic_space

def filter_jchars(char):
    if is_asian(char):
        return ' '
    return char
'''
def strip_Japanese_chars(jap_text):
    '''
    Function for removing Japanese characters from a string.
    Japanese typically contains no whitespace as word delimiters,
    so, in order to extract reference number substrings, all of the
    Japanese characters have to be removed first.

    Based on jp_regex.py.
    https://github.com/olsgaard/Japanese_nlp_scripts/blob/master/jp_regex.py
    Copyright (c) 2014-2015, Mads Sørensen Ølsgaard
    All rights reserved. Released under BSD3 License.

    Regular expression unicode blocks collected from:
    http://www.localizingjapan.com/blog/2012/01/20/regular-expressions-for-japanese-text/
    '''

    # Regular expression unicode blocks
    hiragana_full_width = r'[\u3040-\u309F]'
    katakana_full_width = r'[\u30A0-\u30FF]'
    katakana_half_width = r'[\uFF5F-\uFF9F]'
    kanji = r'[\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A]'
    radicals = r'[\u2E80-\u2FD5]'
    alphanum_full_width = r'[\uFF01-\uFF5E]'
    symbols_punct = r'[\u3000-\u303F]'
    misc_symbols = r'[\u31F0-\u31FF\u3220-\u3243\u3280-\u337F]'

    # Strip Japanese segment of characters included in the above blocks
    jap_text = re.sub(kanji, ' ', jap_text)
    jap_text = re.sub(hiragana_full_width, ' ', jap_text)
    jap_text = re.sub(katakana_full_width, ' ', jap_text)
    jap_text = re.sub(katakana_half_width, ' ', jap_text)
    jap_text = re.sub(radicals, ' ', jap_text)
    jap_text = re.sub(symbols_punct, ' ', jap_text)
    jap_text = re.sub(misc_symbols, ' ', jap_text)
    jap_text = re.sub(alphanum_full_width, ' ', jap_text)

    return jap_text


def clean_string(text):
    '''
    Function for removing punctuation, math symbols, etc. from a string.
    '''
    symbols = r'[,.;:?!"_@#$£%^&+-/x*=<>≤≥≦≧()\[\]{}\\]'
    clean_text = re.sub(symbols, ' ', text)

    return clean_text