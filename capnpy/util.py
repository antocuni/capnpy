import sys
import py
import imp
import capnpy
try:
    from capnpy._util import setattr_builtin
except ImportError:
    setattr_builtin = None

Py_TPFLAGS_HEAPTYPE = (1<<9)  # from object.h

def magic_setattr(cls, attr, value):
    if cls.__flags__ & Py_TPFLAGS_HEAPTYPE:
        # normal case
        setattr(cls, attr, value)
    else:
        if setattr_builtin:
            setattr_builtin(cls, attr, value)
        else:
            raise TypeError("Cannot set attributes on C types. "
                            "Run setup.py to compile capnpy._utils and enable the hack")


def extend(cls):
    def decorator(new_class):
        for key, value in new_class.__dict__.iteritems():
            if key not in ('__dict__', '__doc__', '__module__', '__weakref__'):
                magic_setattr(cls, key, value)
        return cls
    return decorator


def find_module(path, modname, extension='.py'):
    """
    Scan ``path`` to search for the file corresponding for the given ``modname``.
    For example, if ``modname`` is foo.bar.baz, it searches for foo/bar/baz.py.
    """
    relpath = modname.replace('.', '/') + extension
    for dirpath in path:
        dirpath = py.path.local(dirpath)
        f = dirpath.join(relpath)
        if f.check(file=True):
            return f
    return None

def extend_module_maybe(globals, filename=None, modname=None):
    if filename is not None:
        # /path/to/foo.py --> /path/to/foo_extended.py
        filename = py.path.local(filename)
        extname = filename.purebasename + '_extended'
        extmod = filename.new(purebasename=extname, ext='.py')
        if extmod.check(file=False):
            return
    elif modname is not None:
        extname = modname + '_extended'
        extmod = find_module(sys.path, extname)
        if extmod is None:
            return
    else:
        raise ValueError('You must pass either filename or modname')
    #
    src = extmod.read()
    code = compile(src, str(extmod), 'exec')
    exec code in globals

def check_version(version):
    if version != capnpy.__version__:
        msg = ('Version mismatch: the module has been compiled with capnpy '
               '{v1}, but the current version of capnpy is {v2}. '
               'Please recompile.').format(v1=version, v2=capnpy.__version__)
        raise ImportError(msg)

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
