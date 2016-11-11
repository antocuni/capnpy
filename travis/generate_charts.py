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


class ChartGenerator(object):

    def __init__(self, dir, display_filter=None):
        self.dir = dir
        self.display_filter = display_filter

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
        if self.display_filter and self.display_filter in name:
            display(chart)
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

    @classmethod
    def extract_test_name(cls, name):
        m = re.match(r'test_(.*)\[.*\]', name)
        assert m
        return m.group(1)

    def generate_latest(self, impl):
        all_benchmarks = self.load_many(self.find_latest())
        benchmarks = all_benchmarks.filter(
            lambda b: b.info.machine_info.python_implementation == impl)
        self.gen_getattr(impl, benchmarks)
        self.gen_getattr_special(impl, benchmarks)
        self.gen_hash(impl, benchmarks)
        self.gen_load(impl, benchmarks)
        self.gen_ctor(impl, benchmarks)
        ## self.gen_buffered(impl, benchmarks)

    def _gen_generic_chart(self, title, benchmarks, series, group, filename):
        chart = GroupedBarChart(title)
        for b in benchmarks:
            series_name = series(b)
            group_name = group(b)
            chart.add(series_name, group_name, self.get_point(b))
        chart = chart.build()
        self.save(chart, filename)

    def gen_getattr(self, impl, benchmarks):
        benchmarks = benchmarks.filter(lambda b: b.group == 'getattr')
        self._gen_generic_chart(
            title = '%s: get attribute' % impl,
            benchmarks = benchmarks,
            series = lambda b: b.params.schema,
            group = lambda b: b.extra_info.attribute_type,
            filename = '%s-latest-getattr.svg' % impl)

    def gen_getattr_special(self, impl, benchmarks):
        def group(b):
            name = self.extract_test_name(b.name)
            if name == 'numeric':
                return 'int16'
            return name
        #
        benchmarks = benchmarks.filter(lambda b: (
            b.name == 'test_numeric[Capnpy-int16]' or
            b.group == 'getattr_special'))
        self._gen_generic_chart(
            title = '%s: special attributes' % impl,
            benchmarks = benchmarks,
            series = lambda b: None,
            group = group,
            filename = '%s-latest-getattr-special.svg' % impl)

    def gen_hash(self, impl, benchmarks):
        benchmarks = benchmarks.filter(lambda b: b.group.startswith('hash'))
        self._gen_generic_chart(
            title = '%s: hash' % impl,
            benchmarks = benchmarks,
            series = lambda b: b.extra_info.schema,
            group = lambda b: b.extra_info.type,
            filename = '%s-latest-hash.svg' % impl)

    def gen_load(self, impl, benchmarks):
        benchmarks = benchmarks.filter(lambda b: b.group == 'load')
        self._gen_generic_chart(
            title = '%s: load' % impl,
            benchmarks = benchmarks,
            series = lambda b: b.params.schema,
            group = lambda b: self.extract_test_name(b.name),
            filename = '%s-latest-load.svg' % impl)

    def gen_ctor(self, impl, benchmarks):
        benchmarks = benchmarks.filter(lambda b: b.group == 'ctor')
        self._gen_generic_chart(
            title = '%s: constructors' % impl,
            benchmarks = benchmarks,
            series = lambda b: b.params.schema,
            group = lambda b: self.extract_test_name(b.name),
            filename = '%s-latest-ctor.svg' % impl)


def main():
    if len(sys.argv) == 2:
        dir = sys.argv[1]
        display_filter = None
    elif len(sys.argv) == 3:
        dir = sys.argv[1]
        display_filter = sys.argv[2]
    else:
        print 'Usage: generate_charts.py BENCHMARKS-DIR [DISPLAY]'
        sys.exit(1)
    #
    gen = ChartGenerator(py.path.local(dir), display_filter)
    gen.generate_latest('CPython')
    gen.generate_latest('PyPy')

if __name__ == '__main__':
    main()
