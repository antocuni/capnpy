import os
import sys
import re
import operator
import json
import py
from dotmap import DotMap
import pygal

class GroupedBarChart(object):
    """
    Helper class to build a pygal Bar chart with groups.
    Each data point has two property:

      - series_name: each series gets a different color and it's shown in the
        legend

      - group: the bars belonging to each group are located together, and the
        name of the group is shown on the X axis
    """

    def __init__(self, title):
        self.title = title
        self.all_series = set()
        self.all_groups = set()
        self.data = {} # [(series_name, group)] -> point

    def add(self, series_name, group, point):
        self.all_series.add(series_name)
        self.all_groups.add(group)
        self.data[(series_name, group)] = point

    def build(self):
        chart = pygal.Bar(pretty_print=True)
        chart.title = self.title
        series_names = sorted(self.all_series)
        groups = sorted(self.all_groups)
        chart.x_labels = groups
        for name in series_names:
            series = [self.data.get((name, group), None)
                      for group in groups]
            chart.add(name, series)
        return chart


def display(chart):
    # for development
    if isinstance(chart, GroupedBarChart):
        chart = chart.build()
    chart.render_to_png('/tmp/chart.png')
    os.system('feh /tmp/chart.png')


class PyQuery(list):
    """
    Extend a list with an API which is vaguely inspired by jQuery to filter
    and interact with the data.
    """

    def filter(self, predicate):
        new_items = [item for item in self if predicate(item)]
        return self.__class__(new_items)

    def getattr(self, attr, strict=False):
        getter = operator.attrgetter(attr)
        new_items = []
        for item in self:
            try:
                new_items.append(getter(item))
            except (AttributeError, KeyError):
                if strict:
                    raise
                pass
        return self.__class__(new_items)

    def __getattr__(self, attr):
        return self.getattr(attr, strict=True)

    def __call__(self, *args, **kwds):
        return self.__class__([item(*args, **kwds) for item in self])

    def pp(self):
        from pprint import pprint
        for item in self:
            if isinstance(item, DotMap):
                item.pprint()
            else:
                pprint(item)


class Charter(object):
    """
    Chart-maker --> Charter :)
    """

    def __init__(self, dir):
        self.dir = dir
        self.all_benchmarks = self.load_many(self.find_latest())

    def find_latest(self):
        latest = []
        for subdir in self.dir.listdir():
            if subdir.check(dir=False) or subdir.basename == '.git':
                continue
            allfiles = subdir.listdir('*.json')
            allfiles.sort()
            if allfiles:
                latest.append(allfiles[-1])
        return latest

    @classmethod
    def load_one(cls, f):
        s = f.read()
        if s == '':
            return []
        d = json.loads(s)
        info = DotMap(d, _dynamic=False)
        #
        # reverse the relationship between info and benchmarks: each benchmark
        # has a pointer to the info (which has no longer a list of benhmarks)
        benchmarks = info.pop('benchmarks')
        for b in benchmarks:
            b.filename = str(f)
            b.info = info
        return benchmarks

    @classmethod
    def load_many(cls, files):
        benchmarks = PyQuery()
        for f in files:
            benchmarks += cls.load_one(f)
        return benchmarks

    def get_point(self, b):
        return {
            'value': b.stats.mean,
            'ci': {
                'type': 'continuous',
                'sample_size': b.stats.rounds,
                'stddev': b.stats.stddev
            }
        }

    @classmethod
    def extract_test_name(cls, name):
        m = re.match(r'test_([^\[]+)(\[.*\])?', name)
        assert m
        return m.group(1)

    def get_chart(self, impl, title, filter, series, group):
        benchmarks = self.all_benchmarks.filter(filter)
        if impl:
            benchmarks = benchmarks.filter(
                lambda b: b.info.machine_info.python_implementation == impl)
        #
        chart = GroupedBarChart(title)
        for b in benchmarks:
            series_name = series(b)
            group_name = group(b)
            chart.add(series_name, group_name, self.get_point(b))
        return chart.build()
