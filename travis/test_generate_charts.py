import pytest
from collections import namedtuple
from generate_charts import GroupedBarChart, PyQuery

Point = namedtuple('Point', ['x', 'y'])

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
