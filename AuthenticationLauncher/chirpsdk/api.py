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
Handles connections to the Chirp API server.
"""
import json
import logging
import requests
from uuid import getnode

from .util import is_valid_shortcode, is_valid_longcode
from .exceptions import *
from .constants import *

log = logging.getLogger(__name__)


def generate_device_id():
    """ Returns the mac address of the host as a valid device_id. """
    return '-'.join(('%012x' % getnode())[i:i+2] for i in range(0, 12, 2))


def check_valid_code(check):
    def wrapped(func):
        def wrapper(cls, code, *args, **kwargs):
            if not check(code):
                raise ChirpInvalidIdentifierException()
            return func(cls, code, *args, **kwargs)
        return wrapper
    return wrapped
check_valid_shortcode = check_valid_code(is_valid_shortcode)
check_valid_longcode = check_valid_code(is_valid_longcode)


def check_access_permission(key, value, exc):
    def wrapped(func):
        def wrapper(cls, *args, **kwargs):
            if value not in cls.access_matrix.get(key, []):
                raise exc()
            return func(cls, *args, **kwargs)
        return wrapper
    return wrapped


def execute_api_query(func):
    def wrapper(cls, endpoint, *args, **kwargs):
        args = (cls._make_headers(),) + args
        args = (cls._make_url(endpoint),) + args

        try:
            response = func(cls, *args, **kwargs)
        except requests.ConnectionError:
            raise ChirpConnectionException()

        if response.headers.get('X-Chirp-API', '0') != '1':
            raise ChirpIdentityException()

        if response.status_code == 400:
            raise ChirpInvalidRequestException()
        if response.status_code == 401:
            raise ChirpUnauthorizedException()
        if response.status_code == 403:
            raise ChirpForbiddenException()
        if response.status_code == 404:
            raise ChirpNotFoundException()
        if response.status_code == 500:
            raise ChirpServerException()
        if response.status_code == 503:
            raise ChirpUnavailableException()

        try:
            return response.json()
        except ValueError:
            return response
    return wrapper


class API(object):
    access_token = ''
    access_matrix = {}

    def __init__(self, app_key, app_secret, api_host=None):
        self.api_host = api_host if api_host else API_HOST
        self.api_root = API_ENDPOINT_ROOT
        self.authenticate(app_key, app_secret)

    def _make_url(self, endpoint):
        """ Construct an absolute URL."""
        return 'https://{}{}{}'.format(self.api_host, self.api_root, endpoint)

    def _make_headers(self):
        """ Construct the header required by the API."""
        if not self.access_token:
            return {}
        return {
            'X-Auth-Token': self.access_token,
            'Content-type': 'application/json',
        }

    @execute_api_query
    def get(self, url, headers, stream=False):
        """ Make a GET request to an endpoint URL (relative to /v1). """
        return requests.get(url, headers=headers, stream=stream)

    @execute_api_query
    def post(self, url, headers, payload):
        """ Make a POST request to a URL (relative to /v1). """
        return requests.post(url, data=json.dumps(payload), headers=headers)

    # Authentication
    def authenticate(self, app_key, app_secret):
        if not app_key or not app_secret:
            raise ChirpNoCredentialsException()

        data = {
            'app_key': app_key,
            'app_secret': app_secret,
            'device_id': generate_device_id(),
        }
        try:
            response = self.post(API_ENDPOINT_AUTHENTICATE, data)
        except ChirpAPIException:
            raise ChirpInvalidCredentialsException()

        if response['access']['enabled'] is False:
            raise ChirpApplicationDisabledException()

        self.access_token = response['access_token']
        self.access_matrix = response['access']

    # Create/query chirps
    @check_valid_shortcode
    @check_access_permission('chirps', 'read', ChirpChirpsReadRequiredException)
    def get_chirp(self, shortcode):
        """ Retrieves a chirp associated with a given shortcode.
        Returns the dictionary of JSON returned by the server. """
        return self.get('{}/{}'.format(API_ENDPOINT_CHIRP, shortcode))

    @check_access_permission('chirps', 'create', ChirpChirpsCreateRequiredException)
    def create_chirp(self, payload):
        """ Creates a chirp based on the given dictionary payload.
        Returns the dictionary of JSON returned by the server. """
        data = {
            'data': payload,
        }
        return self.post(API_ENDPOINT_CHIRP, data)

    @check_valid_shortcode
    @check_access_permission('chirps', 'read_wav', ChirpChirpsWavRequiredException)
    def save_wav(self, shortcode, filename):
        response = self.get('{}/{}.wav'.format(API_ENDPOINT_CHIRP, shortcode), stream=True)
        with open(filename, 'wb') as wav:
            for chunk in response.iter_content(1024):
                wav.write(chunk)
        return filename

    @check_valid_shortcode
    @check_access_permission('chirps', 'encode', ChirpChirpsEncodeRequiredException)
    def encode(self, shortcode):
        """ Encodes a shortcode to a longcode. """
        endpoint = '{}/{}'.format(API_ENDPOINT_CHIRP_ENCODE, shortcode)
        return self.get(endpoint)

    @check_valid_longcode
    @check_access_permission('chirps', 'decode', ChirpChirpsDecodeRequiredException)
    def decode(self, longcode):
        """ Decodes a longcode to a shortcode. """
        endpoint = '{}/{}'.format(API_ENDPOINT_CHIRP_DECODE, longcode)
        return self.get(endpoint)

    @check_access_permission('chirps', 'encode', ChirpChirpsEncodeRequiredException)
    def encode_message(self, message, protocol):
        data = {
            'message': message,
            'symbol_bits': protocol.symbol_bits,
            'message_length': protocol.message_length,
            'parity_length': protocol.parity_length,
        }
        return self.post(API_ENDPOINT_CHIRP_ENCODE, data)

    @check_access_permission('chirps', 'decode', ChirpChirpsDecodeRequiredException)
    def decode_message(self, encoded, protocol):
        data = {
            'encoded': encoded,
            'symbol_bits': protocol.symbol_bits,
            'message_length': protocol.message_length,
            'parity_length': protocol.parity_length,
        }
        return self.post(API_ENDPOINT_CHIRP_DECODE, data)

    def post_analytics(self, chirp, **data):
        data['shortcode'] = chirp.identifier
        return self.post(API_ENDPOINT_DATA, data)
