import py
import os
from commands import getoutput
import docutils.core
from docutils.parsers.rst import Directive, directives
from traceback import format_exc, print_exc
from sphinx.directives.code import CodeBlock
import pygal
from charter import Charter

class BenchmarkDirective(Directive):
    required_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        'filter': directives.unchanged,
        'series': directives.unchanged,
        'group': directives.unchanged,
    }

    @classmethod
    def setup(cls):
        if cls.charter is not None:
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
        cls.charter = Charter(benchdir)
    charter = None

    def run(self):
        self.setup()
        try:
            return self._run()
        except Exception:
            return [docutils.nodes.system_message(
                'An exception as occured during graph generation:'
                ' \n %s' % format_exc(), type='ERROR', source='/',
                level=3)]

    def get_function(self, name):
        src = 'lambda b: ' + self.options[name]
        return eval(src, self.namespace)

    def _run(self):
        self.namespace = {'charter': self.charter}
        if self.content:
            src = py.code.Source('\n'.join(self.content))
            exec src.compile() in self.namespace
        #
        nodes = []
        for impl in 'CPython', 'PyPy':
            chart = self.charter.get_chart(
                impl = impl,
                title = '%s [%s]' % (self.arguments[0], impl),
                filter = self.get_function('filter'),
                series = self.get_function('series'),
                group = self.get_function('group'))
            svg = '<embed src="%s" />' % chart.render_data_uri()
            nodes.append(docutils.nodes.raw('', svg, format='html'))
        return nodes

def setup(app):
    app.add_directive('benchmark', BenchmarkDirective)
    return {'version': '0.1'}
