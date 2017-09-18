#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2017, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

class ChirpException(Exception):
    error_code = 30000
    error_message = 'Generic error'

    def __init__(self, message=None):
        if message is not None:
            self.error_message = message

    def __str__(self):
        return '[{}] {}'.format(self.error_code, self.error_message)


class ChirpInvalidParametersException(ChirpException):
    error_code = 30001
    error_message = 'Invalid parameters for method'


# Credentials errors (1xxxx)
class ChirpCredentialsException(ChirpException):
    pass

# Authentication errors (10xxx)
class ChirpApplicationDisabledException(ChirpCredentialsException):
    error_code = 10000
    error_message = 'Application has been disabled'

class ChirpNoCredentialsException(ChirpCredentialsException):
    error_code = 10001
    error_message = 'No credentials were provided'

class ChirpInvalidCredentialsException(ChirpCredentialsException):
    error_code = 10002
    error_message = 'Credentials provided are invalid'

class ChirpInsufficientPermissionsException(ChirpCredentialsException):
    error_code = 10004
    error_message = 'Insufficient permissions for requested operation/functionality'

# Chirps errors (11xxx)
class ChirpChirpsCreateRequiredException(ChirpCredentialsException):
    error_code = 11000
    error_message = 'Chirps create permission required'

class ChirpChirpsReadRequiredException(ChirpCredentialsException):
    error_code = 11001
    error_message = 'Chirps read permission required'

class ChirpChirpsSayRequiredException(ChirpCredentialsException):
    error_code = 11004
    error_message = 'Chirps say permission required'

class ChirpChirpsEncodeRequiredException(ChirpCredentialsException):
    error_code = 11006
    error_message = 'Chirps encode permission required'

class ChirpChirpsDecodeRequiredException(ChirpCredentialsException):
    error_code = 11007
    error_message = 'Chirps decode permission required'

class ChirpChirpsWavRequiredException(ChirpCredentialsException):
    error_code = 11008
    error_message = 'Chirps wav permission required'

# Analytics errors (14xxx)
class ChirpAnalyticsCreateRequiredException(ChirpCredentialsException):
    error_code = 14000
    error_message = 'Analytics create permission required'

# Protocols errors (15xxx)
class ChirpProtocolsSetRequiredException(ChirpCredentialsException):
    error_code = 15004
    error_message = 'Protocols set permission required'


# Network errors (2xxxx)
class ChirpNetworkException(ChirpException):
    pass

class ChirpAPIException(ChirpNetworkException):
    pass

# Server errors (20xxx)
class ChirpInvalidRequestException(ChirpAPIException):
    error_code = 20400
    error_message = 'Invalid request'

class ChirpUnauthorizedException(ChirpAPIException):
    error_code = 20401
    error_message = 'Unauthorized: Retry with valid authentication token'

class ChirpForbiddenException(ChirpAPIException):
    error_code = 20403
    error_message = 'Forbidden: Well-formed authentication token, but invalid credentials'

class ChirpNotFoundException(ChirpAPIException):
    error_code = 20404
    error_message = 'Not found'

class ChirpServerException(ChirpAPIException):
    error_code = 20500
    error_message = 'Internal server error'

class ChirpUnavailableException(ChirpAPIException):
    error_code = 20503
    error_message = 'Service Unavailable: Back-end server is at capacity'

# Client errors (21xxx)
class ChirpConnectionException(ChirpNetworkException):
    error_code = 21000
    error_message = 'Connection failure reaching API server'

class ChirpIdentityException(ChirpNetworkException):
    error_code = 21001
    error_message = "Could not verify API server's identity"

class ChirpInvalidJSONException(ChirpNetworkException):
    error_code = 21002
    error_message = 'The JSON payload is invalid'

class ChirpJSONTooBigException(ChirpNetworkException):
    error_code = 21003
    error_message = 'The JSON payload specified is too big'


# SDK (Offline) errors (3xxxx)
class ChirpSDKException(ChirpException):
    pass

# Validation errors (32xxx)
class ChirpInvalidIdentifierException(ChirpSDKException):
    error_code = 32000
    error_message = 'Identifier/message is invalid'

class ChirpIdentifierNoIdentifier(ChirpSDKException):
    error_code = 32001
    error_message = 'Identifier/message not specified'

class ChirpNoAlphanumericException(ChirpSDKException):
    error_code = 32002
    error_message = 'Protocol does not support alphanumeric alphabet'

class ChirpInvalidLengthException(ChirpSDKException):
    error_code = 32003
    error_message = 'Identifier/message length is invalid'

class ChirpInvalidEncodedLengthException(ChirpSDKException):
    error_code = 32004
    error_message = 'Encoded length is invalid'

class ChirpUnknownSymbolsException(ChirpSDKException):
    error_code = 32005
    error_message = 'Message contains unknown symbols'

# Protocol errors (33xxx)
class ChirpInvalidProtocolNameException(ChirpSDKException):
    error_code = 33000
    error_message = 'Selected protocol name has not been recognised'
