import operator
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
        chart = pygal.Bar()
        chart.title = self.title
        series_names = sorted(self.all_series)
        groups = sorted(self.all_groups)
        chart.x_labels = groups
        for name in series_names:
            series = [self.data.get((name, group), None)
                      for group in groups]
            chart.add(name, series)
        return chart


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
