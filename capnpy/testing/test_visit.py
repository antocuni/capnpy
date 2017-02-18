from capnpy import ptr
from capnpy.visit import end_of

class TestEndOf(object):

    def test_struct_data(self):
        buf = ('garbage0'
               'garbage1'
               '\x01\x00\x00\x00\x00\x00\x00\x00'  # 1
               '\x02\x00\x00\x00\x00\x00\x00\x00') # 2
        p = ptr.new_struct(0, data_size=2, ptrs_size=0)
        offset = 16-8 # the struct starts at 16, so the pointer is the word before
        assert end_of(buf, p, offset) == 32
