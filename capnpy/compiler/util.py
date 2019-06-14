import six

def as_identifier(s):
    """
    Take a bytes string and make sure that it can be used as an identifier.
    Return bytes on Py2 and unicode on Py3.

    This is needed for Python2/3 compatibility: in the capnproto schema,
    things like field and struct names are of type Text, and they are
    represented as ``bytes`` by schema.py.

    At the same time the compiler uses lots of string literal to emit the
    .py/.pyx sourcecode, which are bytes on Py3 and unicode on Py3:
    as_identifier checks that they have the correct type.

    Moreover, it also checks that the identifier is ASCII-only, the capnproto
    schemas does not seem to support arbitrary unicode identifiers.
    """
    if type(s) is not bytes:
        raise TypeError("Expected a bytes string")
    try:
        # this is needed also on Python2 to ensure that s contains ASCII only
        decoded_s = s.decode('ascii')
    except UnicodeDecodeError:
        uni_s = s.decode('utf-8', errors='replace')
        raise ValueError(u"Non-ASCII identifiers are not supported "
                         u"by capnpy: %s" % uni_s)
    if six.PY3:
        return decoded_s
    else:
        return s
