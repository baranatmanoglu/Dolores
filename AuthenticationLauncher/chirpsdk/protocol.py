#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2017, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

from os import path as osp
import re
import json
import random

from bitstring import BitArray, CreationError

from .constants import CHIRP_SAMPLERATE, CHIRP_ALPHABET
from .util import note_index_to_frequency, note_index_to_char, char_to_note_index
from .exceptions import *


class Protocol(object):
    """ Protocol: Represents a protocol object

        This will define all the audio parameters to generate a Chirp
    """
    def __init__(self, name='standard'):
        fpath = name
        if not osp.exists(fpath):
            fpath = osp.join(osp.dirname(osp.abspath(__file__)), 'protocols', '{}.json'.format(name))

        try:
            with open(fpath) as proto:
                params = json.load(proto)
        except IOError:
            raise ChirpInvalidProtocolNameException()

        name = params.pop('name')
        encoding = params.pop('encoding')
        acoustic = params.pop('acoustic')

        self.name = name

        self.symbol_bits = encoding.get('symbol_bits', 5)
        self.message_length = encoding.get('message_length', 10)
        self.parity_length = encoding.get('parity_length', 8)

        self.base_frequency = acoustic.get('base_frequency', 1760)
        self.interval = acoustic.get('interval', 0)
        self.fft_size = acoustic.get('fft_size', 2048)

        self.frontdoor_note_length = acoustic.get('frontdoor_note_length', 0.0872)
        self.message_note_length = acoustic.get('message_note_length', 0.0872)
        self.envelope_attack = acoustic.get('envelope_attack', 0.015)
        self.envelope_release = acoustic.get('envelope_release', 0.015)
        self.portamento = acoustic.get('portamento', 0.002)
        self.frontdoor_silence_length = acoustic.get('frontdoor_silence_length', 0.0)
        self.message_silence_length = acoustic.get('message_silence_length', 0.0)

        self.frontdoor = acoustic.get('frontdoor', [17, 19])

    @property
    def frontdoor_note_length_samples(self):
        return int(self.frontdoor_note_length * CHIRP_SAMPLERATE)

    @property
    def message_note_length_samples(self):
        return int(self.message_note_length * CHIRP_SAMPLERATE)

    @property
    def envelope_attack_samples(self):
        return int(self.envelope_attack * CHIRP_SAMPLERATE)

    @property
    def envelope_release_samples(self):
        return int(self.envelope_release * CHIRP_SAMPLERATE)

    @property
    def portamento_samples(self):
        return int(self.portamento * CHIRP_SAMPLERATE)

    @property
    def message_silence_length_samples(self):
        return int(self.message_silence_length * CHIRP_SAMPLERATE)

    @property
    def frontdoor_silence_length_samples(self):
        return int(self.frontdoor_silence_length * CHIRP_SAMPLERATE)

    def note_index_to_frequency(self, note):
        return note_index_to_frequency(
                note, self.base_frequency, self.interval)

    def generate_random_array(self):
        return tuple(random.randint(0, 2**self.symbol_bits - 1) for n in range(self.message_length))

    # Validation methods
    @property
    def supports_alphanumeric(self):
        return 2**self.symbol_bits <= len(CHIRP_ALPHABET)

    def validate_identifier(self, identifier, total_length):
        alphabet = '0-9a-fA-F'
        total_bits = self.symbol_bits * total_length
        hex_length = total_bits / 4 + bool(total_bits % 4)
        length = hex_length + hex_length % 2
        if self.supports_alphanumeric:
            alphabet = CHIRP_ALPHABET[:2**self.symbol_bits]
            length = total_length

        if len(identifier) != length:
            raise ChirpInvalidLengthException()
        if re.search('^[{}]{{{}}}$'.format(alphabet, length), identifier) is None:
            raise ChirpInvalidIdentifierException()

    def validate_message(self, message, total_length):
        if len(message) != total_length:
            raise ChirpInvalidLengthException()
        if 2**self.symbol_bits <= max(message):
            raise ChirpInvalidIdentifierException()

    # Transformation methods
    def _convert_str(self, identifier, length):
        if not self.supports_alphanumeric:
            raise ChirpUnknownSymbolsException()

        self.validate_identifier(identifier, length)
        try:
            return tuple(char_to_note_index(char) for char in identifier)
        except ValueError:
            raise ChirpUnknownSymbolsException()

    def convert_identifier(self, identifier):
        return self._convert_str(identifier, self.message_length)

    def convert_identifier_encoded(self, identifier):
        return self._convert_str(identifier, self.message_length + self.parity_length)

    def _convert_tuple(self, message, length):
        if not self.supports_alphanumeric:
            raise ChirpNoAlphanumericException()

        self.validate_message(message, length)
        try:
            return ''.join(note_index_to_char(note) for note in message)
        except IndexError:
            raise ChirpNoAlphanumericException()

    def convert_message(self, message):
        return self._convert_tuple(message, self.message_length)

    def convert_encoded(self, message):
        return self._convert_tuple(message, self.message_length + self.parity_length)

    def pack_bits(self, message):
        padding = ((self.symbol_bits *
                    self.message_length) % 8)

        try:
            bits = [BitArray(uint=i, length=self.symbol_bits) for i in message]
        except CreationError:
            raise ChirpUnknownSymbolsException()

        if padding:
            bits.insert(0, BitArray(uint=0, length=8 - padding))
        return BitArray().join(bits).hex

    def unpack_bits(self, hex_id):
        pass
