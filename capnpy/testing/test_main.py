import textwrap
from capnpy.__main__ import main, parse_argv

class TestParseOptions:

    def dump(self, options):
        lines = []
        for f in options.FIELDS:
            lines.append('%s: %s' % (f, getattr(options, f)))
        return '\n'.join(lines)

    def parse(self, cmdline):
        argv = cmdline.split()
        return parse_argv(argv)

    def test_simple(self):
        args, options = self.parse('compile myschema.capnp')
        assert args['--pyx'] == 'auto'
        expected = textwrap.dedent("""
            version_check: true
            convert_case: true
            text_type: bytes
            include_reflection_data: true
        """).strip()
        assert self.dump(options) == expected

    def test_options(self):
        args, options = self.parse('compile myschema.capnp '
                                   '--no-convert-case '
                                   '--text-type=unicode '
                                   '--no-pyx '
                                   '--no-version-check '
                                   '--no-reflection ')
        assert args['--pyx'] == False
        expected = textwrap.dedent("""
            version_check: false
            convert_case: false
            text_type: unicode
            include_reflection_data: false
        """).strip()
        assert self.dump(options) == expected

def test_compile(tmpdir):
    schema = textwrap.dedent("""
    @0xbf5147cbbecf40c1;
    struct Point {
        x @0 :Int64;
        y @1 :Int64;
    }
    """)
    example_capnp = tmpdir.join('example.capnp')
    example_capnp.write(schema)
    argv = ['compile', str(example_capnp), '--no-pyx']
    main(argv)
    assert tmpdir.join('example.py').exists()

