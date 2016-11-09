import os
import sys
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


class ChartGenerator(object):

    def __init__(self, dir):
        self.dir = dir

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
        with f.open() as fobj:
            d = json.load(fobj)
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

    def save(self, chart, name):
        if isinstance(chart, GroupedBarChart):
            chart = chart.build()
        f = self.dir.join(name)
        chart.render_to_file(str(f))
        print 'Chart saved to', f

    def get_point(self, b):
        return {
            'value': b.stats.mean,
            'ci': {
                'type': 'continuous',
                'sample_size': b.stats.rounds,
                'stddev': b.stats.stddev
            }
        }

    def generate_latest(self, impl):
        benchmarks = self.load_many(self.find_latest())
        benchmarks = benchmarks.filter(
            lambda b: b.info.machine_info.python_implementation == impl)
        self.gen_getattr(impl, benchmarks)

    def gen_getattr(self, impl, benchmarks):
        chart = GroupedBarChart('%s: get attribute' % impl)
        benchmarks = benchmarks.filter(lambda b: b.group == 'getattr')
        for b in benchmarks:
            attribute_type = b.extra_info.attribute_type
            chart.add(b.params.schema, attribute_type, self.get_point(b))
        #
        chart = chart.build()
        #display(chart)
        self.save(chart, '%s-latest-getattr.svg' % impl)


def main():
    if len(sys.argv) != 2:
        print 'Usage: generate_charts.py BENCHMARKS-DIR'
        sys.exit(1)
    dir = sys.argv[1]
    gen = ChartGenerator(py.path.local(dir))
    gen.generate_latest('CPython')

if __name__ == '__main__':
    main()
