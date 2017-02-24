from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from hashlib import sha256
import re


def decode_base58(bc, length):
    digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')


def validate_bc(value):
    '''Validate that the address informed is a valid bit coin address
    Adapted from https://rosettacode.org/wiki/Bitcoin/address_validation#Python
    Using length 26-35, according to http://bitcoin.stackexchange.com/a/36948
    '''

    p = re.compile(
        "^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{26,35}$"
    )

    if not p.match(value):
        raise ValidationError(
            _('%(value)s has invalid characters for a valid bit coin address'),
            params={'value': value},
        )

    bcbytes = decode_base58(value, 25)
    if not bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]:
        raise ValidationError(
            _('%(value)s is not a valid bit coin address'),
            params={'value': value},
        )
