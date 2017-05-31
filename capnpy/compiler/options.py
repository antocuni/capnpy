from capnpy.annotate import BoolOption

class OptionStack(object):

    def __init__(self, opt=None):
        self._stack = []
        if opt:
            self.push(opt)

    def push(self, opt):
        self._stack.append(opt)

    def pop(self):
        self._stack.pop()
        if not self._stack:
            raise ValueError("Too many pop()s")

    def __getattr__(self, name):
        for opt in reversed(self._stack):
            val = getattr(opt, name, None)
            if val not in (None, BoolOption.notset):
                return val
        else:
            raise AttributeError("Option %s does not exists or it is never set"
                                 % name)
