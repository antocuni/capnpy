import py

def extend(cls):
    def decorator(new_class):
        for key, value in new_class.__dict__.iteritems():
            if key not in ('__dict__', '__doc__', '__module__', '__weakref__'):
                setattr(cls, key, value)
        return cls
    return decorator

def extend_module_maybe(filename, globals):
    # /path/to/foo.py --> /path/to/foo_extended.py
    filename = py.path.local(filename)
    extname = filename.purebasename + '_extended'
    extmod = filename.new(purebasename=extname, ext='.py')
    if extmod.check(file=False):
        return
    src = extmod.read()
    code = compile(src, extname, 'exec')
    exec code in globals


def text_repr(s):
    # abuse the python string repr algo: make sure that the string contains at
    # least one single quote and one double quote (which we will remove
    # later); this way python returns a repr inside single quotes, and escapes
    # non-ascii chars and single quotes. Then, we manually escape the double
    # quotes and put everything inside double quotes
    #
    s = s + "'" + '"'
    s = repr(s)[1:-4] # remove the single quotes around the string, plus the
                      # extra quotes we added above
    s = s.replace('"', r'\"')
    return '"%s"' % s

try:
    from capnpy.floatrepr import float32_repr, float64_repr
except ImportError:
    float32_repr = float64_repr = repr
