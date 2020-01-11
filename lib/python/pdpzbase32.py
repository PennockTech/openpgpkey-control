# Zooko's Base32 encoding

"""
pdpzbase32: crypto-common base32 encoding variant
"""

# https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt

__author__ = 'phil@pennock-tech.com (Phil Pennock)'

import functools
import binascii

ZOOKO32_ALPHABET = b'ybndrfg8ejkmcpqxot1uwisza345h769'


@functools.lru_cache(maxsize=4)
def _forward_table(alphabet):
    tab = [bytes((i,)) for i in alphabet]
    return [a + b for a in tab for b in tab]


@functools.lru_cache(maxsize=4)
def _reverse_table(alphabet):
    return {v: k for k, v in enumerate(alphabet)}


# _bytes_from_decode_data: From Python 3.7.0 base64.py {{{

bytes_types = (bytes, bytearray)  # Types acceptable as binary data


def _bytes_from_decode_data(s):
    if isinstance(s, str):
        try:
            return s.encode('ascii')
        except UnicodeEncodeError:
            raise ValueError('string argument should contain only ASCII characters')
    if isinstance(s, bytes_types):
        return s
    try:
        return memoryview(s).tobytes()
    except TypeError:
        raise TypeError("argument should be a bytes-like object or ASCII "
                        "string, not %r" % s.__class__.__name__) from None

# From Python 3.7.0 base64.py }}}


def encode(s):
    if not isinstance(s, bytes_types):
        s = memoryview(s).tobytes()
    leftover = len(s) % 5
    if leftover:
        s = s + b'\0' * (5 - leftover)
    encoded = bytearray()
    from_bytes = int.from_bytes
    tab = _forward_table(ZOOKO32_ALPHABET)
    for i in range(0, len(s), 5):
        c = from_bytes(s[i: i + 5], 'big')
        encoded += (
            tab[c >> 30] +
            tab[(c >> 20) & 0x3ff] +
            tab[(c >> 10) & 0x3ff] +
            tab[c & 0x3ff]
        )
    # FIXME: handle padding, still not clear on how, the zooko doc waves it away
    return bytes(encoded)


def decode(s):
    s = _bytes_from_decode_data(s)
    if len(s) % 8:
        raise binascii.Error('Incorrect padding')
    rev = _reverse_table(ZOOKO32_ALPHABET)
    decoded = bytearray()
    for i in range(0, len(s), 8):
        quanta = s[i: i + 8]
        acc = 0
        try:
            for c in quanta:
                acc = (acc << 5) + rev[c]
        except KeyError:
            raise binascii.Error('Non-base32 digit found') from None
        decoded += acc.to_bytes(5, 'big')
    # FIXME: do we need padding handling?
    return bytes(decoded)


def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--encode', action='store_true', help='Encode to zbase32')
    parser.add_argument('-d', '--decode', action='store_true', help='Decode from zbase32')
    parser.add_argument('rest', nargs=argparse.REMAINDER)
    options = parser.parse_args()
    if options.encode:
        for a in options.rest:
            print(encode(a.encode('ASCII')))
    elif options.decode:
        for a in options.rest:
            print(decode(a))
    else:
        raise Exception('need either --encode or --decode')


if __name__ == '__main__':
    _main()

# vim: set sw=4 foldmethod=marker :
