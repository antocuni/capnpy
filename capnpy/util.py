from json import dumps as text_repr

def extend(cls):
    def decorator(new_class):
        for key, value in new_class.__dict__.iteritems():
            if key not in ('__dict__', '__doc__', '__module__', '__weakref__'):
                setattr(cls, key, value)
        return cls
    return decorator
