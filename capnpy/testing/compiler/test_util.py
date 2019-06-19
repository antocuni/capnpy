# -*- encoding: utf-8 -*-

import pytest
import six
from capnpy.compiler.util import as_identifier

def test_as_identifier():
    assert as_identifier(b'hello') == 'hello'
    t = type(as_identifier(b'hello'))
    assert t is str # bytes on Py2, unicode on Py3
    with pytest.raises(TypeError):
        as_identifier(u'hello')
    #
    unicode_identifier = u'hellò'.encode('utf-8')
    with pytest.raises(ValueError) as exc:
        as_identifier(unicode_identifier)
    assert six.text_type(exc.value) == (u'Non-ASCII identifiers are not '
                                        u'supported by capnpy: hellò')

