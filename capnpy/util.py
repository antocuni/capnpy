def extend(original_class):
    def decorator(new_class):
        for key, value in new_class.__dict__.iteritems():
            if key not in ('__dict__', '__doc__', '__module__', '__weakref__'):
                setattr(original_class, key, value)
        return original_class
    return decorator
