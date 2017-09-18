#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2017, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

from .exceptions import *


class Chirp(object):
    """ Chirp: Represents a chirp object, featuring:

    data -- a dict of key-value pairs
    shortcode -- a string representation using the protocol's alphabet
    created_at -- a datetime representing the Chirp's creation date
    """
    def __init__(self, chirpsdk, data=None, shortcode=None, created_at=None,
                 longcode=None, public=True):
        self.chirpsdk = chirpsdk
        self.data = data
        self.created_at = created_at

        if isinstance(shortcode, (str, unicode)):
            self.message = self.chirpsdk.protocol.convert_identifier(shortcode)
        else:
            self.message = tuple(shortcode)

        if longcode and isinstance(longcode, (str, unicode)):
            self.encoded = self.chirpsdk.protocol.convert_identifier_encoded(longcode)
        elif longcode:
            self.encoded = longcode
        elif self.message:
            self.encoded = self.chirpsdk.encode(self.message)

        self.public = public

    @staticmethod
    def generate(chirpsdk):
        """ Generates a random Chirp object and returns it."""
        return Chirp(chirpsdk, shortcode=chirpsdk.protocol.generate_random_array())

    @property
    def shortcode(self):
        """ Returns the string representation of a Chirp using the protocol's alphabet."""
        if self.message:
            return self.chirpsdk.protocol.convert_message(self.message)
        return None

    @property
    def longcode(self):
        """ Returns the full string representation of a Chirp using the protocol's alphabet.
        Including the error correction bits."""
        if self.encoded:
            return self.chirpsdk.protocol.convert_encoded(self.encoded)
        return None

    @property
    def hex(self):
        """ Returns the hexadecimal representation of a Chirp."""
        return self.chirpsdk.protocol.pack_bits(self.message)

    @property
    def identifier(self):
        """ Returns the string representation of a Chirp,
        using the protocol's alphabet if possible."""
        return self.shortcode if self.chirpsdk.protocol.supports_alphanumeric else self.hex

    def chirp(self):
        """ Plays a Chirp."""
        self.chirpsdk.chirp(self)

    def save_wav(self, filename=None, offline=False):
        """ Saves the Chirp as a local wav file.

        Set offline to True if you want to generate the file locally
        instead of fetching it from our servers."""
        self.chirpsdk.save_wav(self, filename, offline)
