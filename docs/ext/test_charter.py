import pytest
import json
from mock import Mock
from dotmap import DotMap
from collections import namedtuple
from charter import GroupedBarChart, TimelineChart, PyQuery, Charter

Point = namedtuple('Point', ['x', 'y'])

class MyCharter(Charter):
    def __init__(self, benchmarks=PyQuery()):
        self.all = benchmarks
        self.latest = benchmarks
        self.latest_warning = None

    def get_point(self, b):
        return b.value

def fake_get_chart(timeline, benchmarks, title, filter, series, group):
    chart = Mock()
    chart.timeline = timeline
    chart.benchmarks = benchmarks
    chart.b_values = [b.value for b in benchmarks]
    chart.title = title
    chart.filter = filter
    chart.series = series
    chart.group = group
    return chart

def test_GroupedBarChart():
    ch = GroupedBarChart('My Title')
    ch.get_point = lambda b: b
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
            'machine_info': {
                'cpu': 'Intel',
                'python_implementation': 'CPython',
            },
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
        assert b1.info.machine_info.cpu == 'Intel'
        assert b1.python_implementation == 'CPython'
        assert b1.info.datetime == 'today'
        #
        assert b2.name == 'bar'
        assert b2.time == 2
        assert b2.info.machine_info.cpu == 'Intel'
        assert b2.python_implementation == 'CPython'
        assert b2.info.datetime == 'today'

    def test_extract_test_name(self):
        ex = Charter.extract_test_name
        assert ex('test___which__[Capnpy]') == '__which__'
        assert ex('test_BufferedSocket') == 'BufferedSocket'

    def test_run_directive_simple(self):
        benchmarks = PyQuery([
            DotMap(value=1),
            DotMap(value=2),
        ])
        charter = MyCharter(benchmarks)
        charter.get_chart = fake_get_chart
        options = {
            'filter': 'b+1',
            'series': 'b+2',
            'group': 'b+3',
        }
        charts = charter.run_directive('My title', options, [])
        assert len(charts) == 1
        chart = charts[0]
        assert not chart.timeline
        assert chart.title == 'My title'
        assert chart.b_values == [1, 2]
        assert chart.filter(0) == 1
        assert chart.series(0) == 2
        assert chart.group(0) == 3

    def test_run_directive_foreach(self):
        benchmarks = PyQuery([
            DotMap(impl='CPython', value=1),
            DotMap(impl='CPython', value=2),
            DotMap(impl='PyPy',    value=3),
            DotMap(impl='PyPy',    value=4),
        ])
        charter = MyCharter(benchmarks)
        charter.get_chart = fake_get_chart
        options = {
            'foreach': 'b.impl',
        }
        charts = charter.run_directive('My title', options, [])
        ch1, ch2 = charts
        assert ch1.title == 'My title [CPython]'
        assert ch1.b_values == [1, 2]
        assert ch2.title == 'My title [PyPy]'
        assert ch2.b_values == [3, 4]

    def test_run_directive_content(self):
        benchmarks = PyQuery([
            DotMap(value=1),
            DotMap(value=2),
        ])
        charter = MyCharter(benchmarks)
        charter.get_chart = fake_get_chart
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


    def test_get_chart(self, monkeypatch):
        def get_point(self, b):
            return b.value
        monkeypatch.setattr(GroupedBarChart, 'get_point', get_point)
        #
        benchmarks = PyQuery([
            DotMap(group='getattr', schema='capnpy', type='int16', value=1),
            DotMap(group='getattr', schema='capnpy', type='text', value=2),
            DotMap(group='getattr', schema='instance', type='int16', value=3),
            DotMap(group='getattr', schema='instance', type='text', value=4),
            DotMap(group='other'),
            ])
        charter = MyCharter(benchmarks)
        chart = charter.get_chart(
            timeline = False,
            benchmarks = benchmarks,
            title = 'My title',
            filter = lambda b: b.group == 'getattr',
            series = lambda b: b.schema,
            group = lambda b: b.type)
        #
        assert chart.title == 'My title'
        assert chart.x_labels == ['int16', 'text']
        assert chart.raw_series == [
            ([1, 2], {'title': 'capnpy'}),
            ([3, 4], {'title': 'instance'})
        ]

    def test_get_chart_timeline(self, monkeypatch):
        def get_point(self, b):
            return {'value': b.value}
        monkeypatch.setattr(TimelineChart, 'get_point', get_point)
        def commit(rev):
            return DotMap(commit_info=DotMap(id=rev))
        #
        benchmarks = PyQuery([
            DotMap(info=commit('a'), group='getattr', schema='capnpy', value=1),
            DotMap(info=commit('b'), group='getattr', schema='capnpy', value=2),
            DotMap(info=commit('a'), group='getattr', schema='instance', value=3),
            DotMap(info=commit('b'), group='getattr', schema='instance', value=4),
            DotMap(info=commit('a'), group='other'),
            ])
        charter = MyCharter(benchmarks)
        chart = charter.get_chart(
            timeline = True,
            benchmarks = benchmarks,
            title = 'My title',
            filter = lambda b: b.group == 'getattr',
            series = lambda b: b.schema,
            group = lambda b: None)
        #
        assert chart.title == 'My title'
        chart.raw_series.sort(key=lambda s:s[1]['title'])
        assert chart.raw_series == [
            ([{'value': 1}, {'value': 2}], {'title': 'capnpy'}),
            ([{'value': 3}, {'value': 4}], {'title': 'instance'})
        ]

    def test_timeline_sorted(self, monkeypatch):
        def get_point(self, b):
            return {'value': b.value}
        monkeypatch.setattr(TimelineChart, 'get_point', get_point)
        def commit(rev):
            return DotMap(commit_info=DotMap(id=rev))
        #
        benchmarks = PyQuery([
            DotMap(info=commit('aaa'), schema='capnpy',   value=1),
            DotMap(info=commit('bbb'), schema='capnpy',   value=2),
            DotMap(info=commit('bbb'), schema='instance', value=2),
            DotMap(info=commit('ccc'), schema='instance', value=3),
            DotMap(info=commit('ddd'), schema='capnpy',   value=4),
            DotMap(info=commit('ddd'), schema='instance', value=4),
            ])
        charter = MyCharter(benchmarks)
        chart = charter.get_chart(
            timeline = True,
            benchmarks = benchmarks,
            title = 'My title',
            filter = lambda b: True,
            series = lambda b: b.schema,
            group = lambda b: None)
        #
        assert chart.title == 'My title'
        chart.raw_series.sort(key=lambda s:s[1]['title'])
        assert chart.raw_series == [
            ([{'value': 1}, {'value': 2}, None, {'value': 4}], {'title': 'capnpy'}),
            ([None, {'value': 2}, {'value': 3}, {'value': 4}], {'title': 'instance'})
        ]
