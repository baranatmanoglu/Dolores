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
Core class bridging between chirp.audio and chirp.api components.
A ChirpSDK object can take arbitrary dictionaries (of any JSON-serialisable data)
and generate a Chirp "shortcode" identifier to play as audio.
"""

from datetime import datetime
from threading import Thread
from time import sleep

from .api import API
# from .audio import AudioSession, AudioGenerator
from .chirp import Chirp
from .protocol import Protocol
from .exceptions import *


class ChirpSDK(object):
    _is_streaming = False;
    _streaming_interval = 1000;
    __last_played = None

    def __init__(self, app_key, app_secret, api_host=None):
        self.api = API(app_key, app_secret, api_host)
        # self.audio_session = AudioSession()
        # self.audio_generator = AudioGenerator()
        self.set_protocol()

    def set_protocol(self, name='standard'):
        self.protocol = Protocol(name)
        # self.audio_session.set_protocol(self.protocol)
        # self.audio_generator.set_protocol(self.protocol)

    def create_chirp(self, payload=None):
        """ Creates a Chirp object that encapsulates the given payload.

        If payload is None, creates a random chirp for the protocol attached to the sdk;
        if payload is a 10-character string (or a tuple of integers), creates an audio-only chirp;
        if it is a dict, generates an identifier that encapsulates the data."""
        if payload is None:
            return Chirp.generate(chirpsdk=self)
        if isinstance(payload, dict):
            data = self.api.create_chirp(payload)
            return Chirp(chirpsdk=self, **data)
        return Chirp(chirpsdk=self, shortcode=payload)

    def get_chirp(self, shortcode):
        """ Queries the Chirp API server for a given shortcode, and returns
        the Chirp object associated."""
        data = self.api.get_chirp(shortcode)
        return Chirp(chirpsdk=self, **data)

    def chirp(self, chirp):
        """ Takes an identifier or Chirp object, and plays it via audio hardware
        (if supported). Requires pyaudio for playback."""
        if not isinstance(chirp, Chirp):
            chirp = self.create_chirp(chirp)
        self.audio_session.play(chirp.encoded)
        if self.__last_played != chirp.encoded:
            self.api.post_analytics(chirp, status='SUCCESS', operation='say',
                                    created_at=datetime.utcnow().isoformat())
        self.__last_played = chirp.encoded

    def _stream(self, chirp):
        while self._is_streaming:
            self.chirp(chirp)
            # sleep only accepts seconds, but can deal with floats
            sleep(self._streaming_interval / 1000.0)

    def start_streaming(self, chirp):
        """ Takes an identifier or Chirp object and plays it repeatedly

        This will run in a separate thread with a pause of `self.streaming_interval`
        between each one.
        Set `self.streaming_interval` to change the default.
        Call `self.stop_streaming()` to break the loop."""
        self._is_streaming = True
        self.__stream = Thread(target=self._stream, args=(chirp,))
        self.__stream.daemon = True
        self.__stream.start()

    def stop_streaming(self):
        """ Stops the chirping loop started with `self.start_streaming()`."""
        if self._is_streaming:
            self._is_streaming = False
            self.__stream.join()
        self.__last_played = None

    @property
    def streaming_interval(self):
        """ Gets or sets the interval in milliseconds to wait between
        each Chirp while streaming."""
        return self._streaming_interval

    @streaming_interval.setter
    def streaming_interval(self, interval):
        """ Sets the interval in milliseconds to wait between
        each Chirp while streaming."""
        self._streaming_interval = max(interval, 0)

    def save_wav(self, chirp, filename=None, offline=False):
        """ Takes a Chirp object, translates it into audio,
        and saves the output as a .wav file."""

        if not filename:
            filename = '{}.wav'.format(chirp.shortcode)

        if not offline:
            self.api.save_wav(chirp.shortcode, filename)
        else:
            self.audio_generator.save_wav(list(chirp.encoded), filename)
        return filename

    def encode(self, message):
        """ Encodes a shortcode to a longcode by adding error-correction bits."""
        if isinstance(message, (tuple, list)):
            return tuple(self.api.encode_message(message, self.protocol)['encoded'])
        try:
            return self.api.encode(message)['longcode']
        except ChirpSDKException:
            return self.protocol.convert_encoded(
                tuple(self.api.encode_message(
                    self.protocol.convert_identifier(message),
                    self.protocol)['encoded']))

    def decode(self, encoded):
        """ Decodes a longcode to shortcode."""
        if isinstance(encoded, (tuple, list)):
            return tuple(self.api.decode_message(encoded, self.protocol)['message'])
        try:
            return self.api.decode(encoded)['shortcode']
        except ChirpSDKException:
            return self.protocol.convert_message(
                tuple(self.api.decode_message(
                    self.protocol.convert_identifier_encoded(encoded),
                    self.protocol)['message']))

