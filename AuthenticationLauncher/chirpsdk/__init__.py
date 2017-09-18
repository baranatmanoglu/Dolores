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
The Chirp Python SDK enables the user to create, send and query chirps,
using the Chirp audio protocol.

Usage:

    >>> import chirpsdk
    >>> sdk = chirpsdk.ChirpSDK(YOUR_APP_KEY, YOUR_APP_SECRET)
    >>> chirp = sdk.create_chirp({'key': 'value'})
    >>> print chirp.shortcode
    vb38c0qrr2

To send this chirp via the inbuilt speaker:

    >>> chirp.chirp()

To construct and send a new chirp:

    >>> chirp = sdk.create_chirp('parrotbill')
    >>> chirp.chirp()
    >>> chirp.save_wav()

To query an existing chirp:

    >>> chirp = sdk.get_chirp('parrotbill')
    >>> print chirp.longcode
    >>> print chirp.data

"""

__title__ = 'chirpsdk'
__version__ = '2.0.1'
__author__ = 'Asio Ltd.'
__license__ = 'Apache 2.0 for non-commercial use only, commercial licences apply for commercial usage.'
__copyright__ = 'Copyright 2011-2017, Asio Ltd.'


from .chirpsdk import *
# from .audio import *
from .api import *
from .chirp import *
from .constants import *
from .util import *
from .exceptions import *
