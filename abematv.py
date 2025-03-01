import base64
import binascii
import functools
import hashlib
import hmac
import io
import json
import os
import re
import time
import urllib.parse
import uuid
import warnings

from .common import InfoExtractor
from ..aes import aes_ecb_decrypt
from ..networking import RequestHandler, Response
from ..networking.exceptions import TransportError
from ..utils import (
    ExtractorError,
    OnDemandPagedList,
    decode_base_n,
    int_or_none,
    time_seconds,
    traverse_obj,
    update_url_query,
)

def get_secret_from_env(key, default=None, encoding='utf-8'):
    """Safely retrieve secrets from environment variables with proper warnings."""
    value = os.environ.get(key)
    if not value and default:
        warnings.warn(
            f"{key} not found in environment variables, using default value. "
            "This is insecure and should only be used for testing.",
            RuntimeWarning
        )
        return default.encode(encoding) if isinstance(default, str) else default
    return value.encode(encoding) if value else None

class AbemaLicenseRH(RequestHandler):
    _SUPPORTED_URL_SCHEMES = ('abematv-license',)
    _SUPPORTED_PROXY_SCHEMES = None
    _SUPPORTED_FEATURES = None
    RH_NAME = 'abematv_license'

    _STRTABLE = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    @property
    def _HKEY(self):
        """Get HKEY from environment variable."""
        return get_secret_from_env(
            'ABEMA_HKEY',
            default='3AF0298C219469522A313570E8583005A642E73EDD58E3EA2FB7339D3DF1597E'
        )

    def __init__(self, *, ie: 'AbemaTVIE', **kwargs):
        super().__init__(**kwargs)
        self.ie = ie

    # ... rest of the AbemaLicenseRH class implementation ...

class AbemaTVBaseIE(InfoExtractor):
    _NETRC_MACHINE = 'abematv'

    _USERTOKEN = None
    _DEVICE_ID = None
    _MEDIATOKEN = None

    @property
    def _SECRETKEY(self):
        """Get secret key from environment variable."""
        return get_secret_from_env(
            'ABEMA_SECRET_KEY',
            default='v+Gjs=25Aw5erR!J8ZuvRrCx*rGswhB&qdHd_SYerEWdU&a?3DzN9BRbp5KwY4hEmcj5#fykMjJ=AuWz5GSMY-d@H7DMEh3M@9n2G552Us$$k9cD=3TxwWe86!x#Zyhe'
        )

    # ... rest of the AbemaTVBaseIE class implementation ...

# ... rest of the file remains unchanged ... 