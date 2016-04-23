import sys

def pytest_addoption(parser):
    group = parser.getgroup('pyx', 'enable pyx test')
    group.addoption('--pyx', action='store_true', default=False, dest='pyx')
    group.addoption('--annotate', action='store_true', default=False, dest='annotate')
