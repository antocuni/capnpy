from docutils.parsers.rst import Directive, directives
from traceback import format_exc, print_exc
from sphinx.directives.code import CodeBlock

import docutils.core
import pygal


class BenchmarkDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        'a': directives.unchanged,
        'b': directives.unchanged,
    }

    def run(self):
        width, height = 600, 400
        chart = pygal.Bar()
        chart.title = self.arguments[0]
        chart.add('a', eval(self.options['a']))
        chart.add('b', eval(self.options['b']))
        chart.config.width = width
        chart.config.height = height
        chart.explicit_size = True

        try:
            svg = '<embed src="%s" />' % chart.render_data_uri()
        except Exception:
            return [docutils.nodes.system_message(
                'An exception as occured during graph generation:'
                ' \n %s' % format_exc(), type='ERROR', source='/',
                level=3)]
        return [docutils.nodes.raw('', svg, format='html')]



def setup(app):
    app.add_directive('benchmark', BenchmarkDirective)
    return {'version': '0.1'}
