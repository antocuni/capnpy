import py
import os
from commands import getoutput
import docutils.core
from docutils.parsers.rst import Directive, directives
from traceback import format_exc, print_exc
from sphinx.directives.code import CodeBlock
import pygal
from generate_charts import ChartGenerator

def function(src):
    src = 'lambda b: ' + src
    return eval(src)

class BenchmarkDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        'filter': function,
        'series': function,
        'group': function,
    }

    @classmethod
    def setup(cls):
        if cls.generator is not None:
            return
        # clone the .benchmarks repo, if it's needed
        root = py.path.local(__file__).dirpath('..', '..')
        benchdir = root.join('.benchmarks')
        if benchdir.check(exists=False):
            print 'Cloning the .benchmarks repo'
            url = getoutput('git config remote.origin.url')
            cmd = 'git clone --depth=1 --branch=benchmarks {url} {dst}'
            ret = os.system(cmd.format(url=url, dst=benchdir))
            assert ret == 0
        #
        cls.generator = ChartGenerator(benchdir)
    generator = None

    def run(self):
        self.setup()
        chart = self.generator.get_chart(
            title = self.arguments[0],
            filter = self.options['filter'],
            series = self.options['series'],
            group = self.options['group'])

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
