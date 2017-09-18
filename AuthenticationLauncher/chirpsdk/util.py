#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2017, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

"""
Utilities and helper functions.
"""

import random
import re

from .constants import *
from .exceptions import *


def is_valid_shortcode(shortcode):
    """ Returns True if `shortcode` is a valid Chirp shortcode. """
    return re.search(CHIRP_SHORTCODE_PATTERN, shortcode) is not None


def is_valid_longcode(longcode):
    """ Returns True if `longcode` is a valid Chirp longcode. """
    return re.search(CHIRP_LONGCODE_PATTERN, longcode) is not None


def char_to_note_index(char):
    return CHIRP_ALPHABET.index(char)


def note_index_to_char(index):
    return CHIRP_ALPHABET[index]


def note_index_to_frequency(note_index, base_frequency, interval):
    if not interval:
        return base_frequency * MIDI_NOTE_RATIO**note_index
    return base_frequency + note_index * interval


def char_to_frequency(char, base_frequency, interval):
    return note_index_to_frequency(
        char_to_note_index(char), base_frequency, interval)
