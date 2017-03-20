cdef char* as_cbuf(object buf, Py_ssize_t* length, bint rw=*) except NULL
cpdef unpack_primitive(char ifmt, object buf, int offset)
cpdef long unpack_int64(object buf, int offset)
cpdef long unpack_int16(object buf, int offset)
cpdef long unpack_uint32(object buf, int offset)
cpdef bytes pack_message_header(int segment_count, int segment_size, long p)
cpdef bytes pack_int64(long value)
cpdef object pack_into(char ifmt, object buf, int offset, object value)
cpdef object pack_int64_into(object buf, int offset, long value)
