from generate_charts import GroupedBarChart

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
