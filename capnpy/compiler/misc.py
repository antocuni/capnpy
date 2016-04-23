from capnpy.schema import Value, Type

@Type.__extend__
class Type:

    def compile_name(self, m):
        if self.is_builtin():
            return '_Types.%s' % self.which()
        elif self.is_struct():
            node = m.allnodes[self.struct.typeId]
            return node.compile_name(m)
        elif self.is_enum():
            node = m.allnodes[self.enum.typeId]
            return node.compile_name(m)
        else:
            raise NotImplementedError

    def runtime_name(self, m):
        if self.is_builtin():
            return '_Types.%s' % self.which()
        elif self.is_struct():
            node = m.allnodes[self.struct.typeId]
            return node.runtime_name(m)
        elif self.is_enum():
            node = m.allnodes[self.enum.typeId]
            return node.runtime_name(m)
        else:
            raise NotImplementedError

    def fasthash_function(self):
        w = self.which()
        if Type.__tag__.int8 <= w <= Type.__tag__.uint32:
            # this can be assimilated to a Python <int>
            return '_hash.inthash'
        elif self.is_uint64():
            # this can be assimilated to a Python <long>
            return '_hash.longhash'
        else:
            # no fast hash, use the "slow" one
            return 'hash'

@Value.__extend__
class Value:

    def as_pyobj(self):
        val_type = str(self.which())
        return getattr(self, val_type)

