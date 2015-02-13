import re

# http://stackoverflow.com/a/1176023/1046372
A = re.compile('(.)([A-Z][a-z]+)')
B = re.compile('([a-z0-9])([A-Z])')
def from_camel_case(name):
    s1 = A.sub(r'\1_\2', name)
    return B.sub(r'\1_\2', s1).lower()

