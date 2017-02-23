import py
import commands
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
        'timeline': directives.flag,
        'foreach': directives.unchanged,
        'filter': directives.unchanged,
        'series': directives.unchanged,
        'group': directives.unchanged,
    }

    @classmethod
    def setup(cls):
        if cls.charter is not None:
            return
        root = py.path.local(__file__).dirpath('..', '..')
        revision = commands.getoutput('git rev-parse HEAD')
        benchdir = root.join('.benchmarks')
        cls.charter = Charter(benchdir, revision)
    charter = None

    def run(self):
        self.setup()
        try:
            return self._run()
        except Exception:
            ## import pdb;pdb.xpm()
            raise
            ## return [docutils.nodes.system_message(
            ##     'An exception as occured during graph generation:'
            ##     ' \n %s' % format_exc(), type='ERROR', source='/',
            ##     level=3)]

    def get_function(self, name):
        src = 'lambda b: ' + self.options[name]
        return eval(src, self.namespace)

    def _run(self):
        title = self.arguments[0]
        charts = self.charter.run_directive(title, self.options, self.content)
        nodes = []
        for chart in charts:
            chart_id = docutils.nodes.make_id(chart.title)
            svg = '<embed id="%s" src="%s" />' % (chart_id, chart.render_data_uri())
            nodes.append(docutils.nodes.raw('', svg, format='html'))
        return nodes

def setup(app):
    app.add_directive('benchmark', BenchmarkDirective)
    app.connect('build-finished', on_build_finished)
    return {'version': '0.1'}

def on_build_finished(app, exception):
    def check_displayed(cat, benchmarks):
        not_displayed = []
        for b in benchmarks:
            if not b.get('__displayed__', False):
                not_displayed.append(b)
        #
        if not_displayed:
            print 'WARNING: the following [%s] benchmarks were not displayed' % cat
            for b in not_displayed:
                print '    %10s %s' % (b.group, b.name)
            print
    #
    if BenchmarkDirective.charter:
        check_displayed('latest', BenchmarkDirective.charter.latest)
    #check_displayed('all', BenchmarkDirective.charter.all)
