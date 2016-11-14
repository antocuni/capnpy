import pytest
import json
from mock import Mock
from collections import namedtuple
from charter import GroupedBarChart, PyQuery, Charter

Point = namedtuple('Point', ['x', 'y'])

class MyCharter(Charter):
    def __init__(self):
        pass

    def get_chart(self, impl, title, filter, series, group):
        chart = Mock()
        chart.impl = impl
        chart.title = title
        chart.filter = filter
        chart.series = series
        chart.group = group
        return chart

def test_GroupedBarChart():
    ch = GroupedBarChart('My Title')
    ch.add('capnpy', 'int64', 1)
    ch.add('capnpy', 'text', 2)
    ch.add('instance', 'text', 3)
    ch.add('instance', 'list', 4)
    chart = ch.build()
    assert chart.title == 'My Title'
    assert chart.raw_series == [
        ([1, None, 2], {'title': 'capnpy'}),
        ([None, 4, 3], {'title': 'instance'})
    ]


class TestPyQuery(object):

    def test_filter(self):
        all = PyQuery(range(10))
        subset = all.filter(lambda x: x < 4)
        assert subset == [0, 1, 2, 3]
        assert isinstance(subset, PyQuery)

    def test_getattr(self):
        points = PyQuery([Point(x, x*2) for x in range(5)])
        assert points.getattr('x') == [0, 1, 2, 3, 4]
        assert points.getattr('y') == [0, 2, 4, 6, 8]

    def test_getattr_strict(self):
        points = PyQuery([
            Point(1, 2),
            'hello',
            Point(3, 4)
        ])
        assert points.getattr('x') == [1, 3]
        with pytest.raises(AttributeError):
            points.getattr('x', strict=True)

    def test___getattr__(self):
        points = PyQuery([Point(x, x*2) for x in range(5)])
        assert points.x == [0, 1, 2, 3, 4]
        with pytest.raises(AttributeError):
            points.i_dont_exist

    def test_call(self):
        lower_list = PyQuery(['hello', 'world'])
        upper_list = lower_list.upper()
        assert upper_list == ['HELLO', 'WORLD']


class TestCharter(object):

    def test_load_one(self, tmpdir):
        data = {
            'machine_info': 'Intel',
            'datetime': 'today',
            'benchmarks': [
                {'name': 'foo', 'time': 1},
                {'name': 'bar', 'time': 2},
            ]
        }
        myfile = tmpdir.join('myfile.json')
        myfile.write(json.dumps(data))
        #
        benchmarks = Charter.load_one(myfile)
        b1, b2 = benchmarks
        assert b1.name == 'foo'
        assert b1.time == 1
        assert b1.info.machine_info == 'Intel'
        assert b1.info.datetime == 'today'
        #
        assert b2.name == 'bar'
        assert b2.time == 2
        assert b2.info.machine_info == 'Intel'
        assert b2.info.datetime == 'today'

    def test_extract_test_name(self):
        ex = Charter.extract_test_name
        assert ex('test___which__[Capnpy]') == '__which__'
        assert ex('test_BufferedSocket') == 'BufferedSocket'

    def test_run_directive_simple(self):
        charter = MyCharter()
        options = {
            'filter': 'b+1',
            'series': 'b+2',
            'group': 'b+3',
        }
        charts = charter.run_directive('My title', options, [])
        ch1, ch2 = charts
        assert ch1.impl == 'CPython'
        assert ch1.title == 'My title [CPython]'
        assert ch2.impl == 'PyPy'
        assert ch2.title == 'My title [PyPy]'
        for ch in charts:
            assert ch.filter(0) == 1
            assert ch.series(0) == 2
            assert ch.group(0) == 3

    def test_run_directive_content(self):
        charter = MyCharter()
        options = {
            'filter': 'myfilter(b)',
            'series': 'b+2',
            'group': 'b+3',
        }
        content = [
            'def myfilter(x):'
            '    return x*6'
        ]
        charts = charter.run_directive('My title', options, content)
        ch = charts[0]
        assert ch.filter(7) == 42
