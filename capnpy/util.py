def extend(original_class):
    def decorator(new_class):
        for key, value in new_class.__dict__.iteritems():
            if key not in ('__dict__', '__doc__'):
                setattr(original_class, key, value)
        return None
    return decorator
