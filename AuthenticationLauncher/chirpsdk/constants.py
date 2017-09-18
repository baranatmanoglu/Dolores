#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2017, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

# Chirp
CHIRP_ALPHABET = '0123456789abcdefghijklmnopqrstuv'
CHIRP_LENGTH = 10
CHIRP_SYMBOL_BITS = 5
CHIRP_REED_SOLOMON_LENGTH = 8
CHIRP_LONGCODE_LENGTH = CHIRP_LENGTH + CHIRP_REED_SOLOMON_LENGTH
CHIRP_SHORTCODE_PATTERN = '^[%s]{%d}$' % (CHIRP_ALPHABET, CHIRP_LENGTH)
CHIRP_LONGCODE_PATTERN = '^[%s]{%d}$' % (CHIRP_ALPHABET, CHIRP_LONGCODE_LENGTH)

# API
API_HOST = 'api.chirp.io'
API_ENDPOINT_ROOT = '/v1'
API_ENDPOINT_AUTHENTICATE = '/authenticate'
API_ENDPOINT_CHIRP = '/chirps'
API_ENDPOINT_CHIRP_ENCODE = '/chirps/encode'
API_ENDPOINT_CHIRP_DECODE = '/chirps/decode'
API_ENDPOINT_DATA = '/data'

# Audio
CHIRP_SAMPLERATE = 44100.0
MIDI_NOTE_RATIO = 1.0594630943591

# Attack and release as a percent of total note length
ENV_SUSTAIN = 1.0
