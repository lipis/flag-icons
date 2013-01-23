# -*- coding: utf-8 -*-
r"""
    werkzeug.templates
    ~~~~~~~~~~~~~~~~~~

    A minimal template engine.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD License.
"""
import sys
import re
import __builtin__ as builtins
from compiler import ast, parse
from compiler.pycodegen import ModuleCodeGenerator
from tokenize import PseudoToken
from werkzeug import urls, utils
from werkzeug._internal import _decode_unicode
from werkzeug.datastructures import MultiDict


from warnings import warn
warn(DeprecationWarning('werkzeug.templates is deprecated and '
                        'will be removed in Werkzeug 1.0'))


# Copyright notice: The `parse_data` method uses the string interpolation
# algorithm by Ka-Ping Yee which originally was part of `Itpl20.py`_.
#
# .. _Itpl20.py: http://lfw.org/python/Itpl20.py


token_re = re.compile('%s|%s(?s)' % (
    r'[uU]?[rR]?("""|\'\'\')((?<!\\)\\\1|.)*?\1',
    PseudoToken
))
directive_re = re.compile(r'(?<!\\)<%(?:(#)|(py(?:thon)?\b)|'
                          r'(?:\s*(\w+))\s*)(.*?)\s*%>\n?(?s)')
escape_re = re.compile(r'\\\n|\\(\\|<%)')
namestart_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
undefined = type('UndefinedType', (object,), {
    '__iter__': lambda x: iter(()),
    '__repr__': lambda x: 'Undefined',
    '__str__':  lambda x: ''
})()
runtime_vars = frozenset(['Undefined', '__to_unicode', '__context',
                          '__write', '__write_many'])


def call_stmt(func, args, lineno):
    return ast.CallFunc(ast.Name(func, lineno=lineno),
                        args, lineno=lineno)


def tokenize(source, filename):
    escape = escape_re.sub
    escape_repl = lambda m: m.group(1) or ''
    lineno = 1
    pos = 0

    for match in directive_re.finditer(source):
        start, end = match.span()
        if start > pos:
            data = source[pos:start]
            yield lineno, 'data', escape(escape_repl, data)
            lineno += data.count('\n')
        is_comment, is_code, cmd, args = match.groups()
        if is_code:
            yield lineno, 'code', args
        elif not is_comment:
            yield lineno, 'cmd', (cmd, args)
        lineno += source[start:end].count('\n')
        pos = end

    if pos < len(source):
        yield lineno, 'data', escape(escape_repl, source[pos:])


def transform(node, filename):
    root = ast.Module(None, node, lineno=1)
    nodes = [root]
    while nodes:
        node = nodes.pop()
        node.filename = filename
        if node.__class__ in (ast.Printnl, ast.Print):
            node.dest = ast.Name('__context')
        elif node.__class__ is ast.Const and isinstance(node.value, str):
            try:
                node.value.decode('ascii')
            except UnicodeError:
                node.value = node.value.decode('utf-8')
        nodes.extend(node.getChildNodes())
    return root


class TemplateSyntaxError(SyntaxError):

    def __init__(self, msg, filename, lineno):
        from linecache import getline
        l = getline(filename, lineno)
        SyntaxError.__init__(self, msg, (filename, lineno, len(l) or 1, l))


class Parser(object):

    def __init__(self, gen, filename):
        self.gen = gen
        self.filename = filename
        self.lineno = 1

    def fail(self, msg):
        raise TemplateSyntaxError(msg, self.filename, self.lineno)

    def parse_python(self, expr, type='exec'):
        if isinstance(expr, unicode):
            expr = '\xef\xbb\xbf' + expr.encode('utf-8')
        try:
            node = parse(expr, type)
        except SyntaxError, e:
            raise TemplateSyntaxError(str(e), self.filename,
                                      self.lineno + e.lineno - 1)
        nodes = [node]
        while nodes:
            n = nodes.pop()
            if hasattr(n, 'lineno'):
                n.lineno = (n.lineno or 1) + self.lineno - 1
            nodes.extend(n.getChildNodes())
        return node.node

    def parse(self, needle=()):
        start_lineno = self.lineno
        result = []
        add = result.append
        for self.lineno, token, value in self.gen:
            if token == 'data':
                add(self.parse_data(value))
            elif token == 'code':
                add(self.parse_code(value.splitlines()))
            elif token == 'cmd':
                name, args = value
                if name in needle:
                    return name, args, ast.Stmt(result, lineno=start_lineno)
                if name in ('for', 'while'):
                    add(self.parse_loop(args, name))
                elif name == 'if':
                    add(self.parse_if(args))
                else:
                    self.fail('unknown directive %s' % name)
        if needle:
            self.fail('unexpected end of template')
        return ast.Stmt(result, lineno=start_lineno)

    def parse_loop(self, args, type):
        rv = self.parse_python('%s %s: pass' % (type, args), 'exec').nodes[0]
        tag, value, rv.body = self.parse(('end' + type, 'else'))
        if value:
            self.fail('unexpected data after ' + tag)
        if tag == 'else':
            tag, value, rv.else_ = self.parse(('end' + type,))
            if value:
                self.fail('unexpected data after else')
        return rv

    def parse_if(self, args):
        cond = self.parse_python('if %s: pass' % args).nodes[0]
        tag, value, body = self.parse(('else', 'elif', 'endif'))
        cond.tests[0] = (cond.tests[0][0], body)
        while 1:
            if tag == 'else':
                if value:
                    self.fail('unexpected data after else')
                tag, value, cond.else_ = self.parse(('endif',))
            elif tag == 'elif':
                expr = self.parse_python(value, 'eval')
                tag, value, body = self.parse(('else', 'elif', 'endif'))
                cond.tests.append((expr, body))
                continue
            break
        if value:
            self.fail('unexpected data after endif')
        return cond

    def parse_code(self, lines):
        margin = sys.maxint
        for line in lines[1:]:
            content = len(line.lstrip())
            if content:
                indent = len(line) - content
                margin = min(margin, indent)
        if lines:
            lines[0] = lines[0].lstrip()
        if margin < sys.maxint:
            for i in xrange(1, len(lines)):
                lines[i] = lines[i][margin:]
        while lines and not lines[-1]:
            lines.pop()
        while lines and not lines[0]:
            lines.pop(0)
        return self.parse_python('\n'.join(lines))

    def parse_data(self, text):
        start_lineno = lineno = self.lineno
        pos = 0
        end = len(text)
        nodes = []

        def match_or_fail(pos):
            match = token_re.match(text, pos)
            if match is None:
                self.fail('invalid syntax')
            return match.group().strip(), match.end()

        def write_expr(code):
            node = self.parse_python(code, 'eval')
            nodes.append(call_stmt('__to_unicode', [node], lineno))
            return code.count('\n')

        def write_data(value):
            if value:
                nodes.append(ast.Const(value, lineno=lineno))
                return value.count('\n')
            return 0

        while 1:
            offset = text.find('$', pos)
            if offset < 0:
                break
            next = text[offset + 1]

            if next == '{':
                lineno += write_data(text[pos:offset])
                pos = offset + 2
                level = 1
                while level:
                    token, pos = match_or_fail(pos)
                    if token in ('{', '}'):
                        level += token == '{' and 1 or -1
                lineno += write_expr(text[offset + 2:pos - 1])
            elif next in namestart_chars:
                lineno += write_data(text[pos:offset])
                token, pos = match_or_fail(offset + 1)
                while pos < end:
                    if text[pos] == '.' and pos + 1 < end and \
                       text[pos + 1] in namestart_chars:
                        token, pos = match_or_fail(pos + 1)
                    elif text[pos] in '([':
                        pos += 1
                        level = 1
                        while level:
                            token, pos = match_or_fail(pos)
                            if token in ('(', ')', '[', ']'):
                                level += token in '([' and 1 or -1
                    else:
                        break
                lineno += write_expr(text[offset + 1:pos])
            else:
                lineno += write_data(text[pos:offset + 1])
                pos = offset + 1 + (next == '$')
        write_data(text[pos:])

        return ast.Discard(call_stmt(len(nodes) == 1 and '__write' or
                           '__write_many', nodes, start_lineno),
                           lineno=start_lineno)


class Context(object):

    def __init__(self, namespace, charset, errors):
        self.charset = charset
        self.errors = errors
        self._namespace = namespace
        self._buffer = []
        self._write = self._buffer.append
        _extend = self._buffer.extend
        self.runtime = dict(
            Undefined=undefined,
            __to_unicode=self.to_unicode,
            __context=self,
            __write=self._write,
            __write_many=lambda *a: _extend(a)
        )

    def write(self, value):
        self._write(self.to_unicode(value))

    def to_unicode(self, value):
        if isinstance(value, str):
            return _decode_unicode(value, self.charset, self.errors)
        return unicode(value)

    def get_value(self, as_unicode=True):
        rv = u''.join(self._buffer)
        if not as_unicode:
            return rv.encode(self.charset, self.errors)
        return rv

    def __getitem__(self, key, default=undefined):
        try:
            return self._namespace[key]
        except KeyError:
            return getattr(builtins, key, default)

    def get(self, key, default=None):
        return self.__getitem__(key, default)

    def __setitem__(self, key, value):
        self._namespace[key] = value

    def __delitem__(self, key):
        del self._namespace[key]


class TemplateCodeGenerator(ModuleCodeGenerator):

    def __init__(self, node, filename):
        ModuleCodeGenerator.__init__(self, transform(node, filename))

    def _nameOp(self, prefix, name):
        if name in runtime_vars:
            return self.emit(prefix + '_GLOBAL', name)
        return ModuleCodeGenerator._nameOp(self, prefix, name)


class Template(object):
    """Represents a simple text based template.  It's a good idea to load such
    templates from files on the file system to get better debug output.
    """

    default_context = {
        'escape':           utils.escape,
        'url_quote':        urls.url_quote,
        'url_quote_plus':   urls.url_quote_plus,
        'url_encode':       urls.url_encode
    }

    def __init__(self, source, filename='<template>', charset='utf-8',
                 errors='strict', unicode_mode=True):
        if isinstance(source, str):
            source = _decode_unicode(source, charset, errors)
        if isinstance(filename, unicode):
            filename = filename.encode('utf-8')
        node = Parser(tokenize(u'\n'.join(source.splitlines()),
                               filename), filename).parse()
        self.code = TemplateCodeGenerator(node, filename).getCode()
        self.filename = filename
        self.charset = charset
        self.errors = errors
        self.unicode_mode = unicode_mode

    @classmethod
    def from_file(cls, file, charset='utf-8', errors='strict',
                  unicode_mode=True):
        """Load a template from a file.

        .. versionchanged:: 0.5
            The encoding parameter was renamed to charset.

        :param file: a filename or file object to load the template from.
        :param charset: the charset of the template to load.
        :param errors: the error behavior of the charset decoding.
        :param unicode_mode: set to `False` to disable unicode mode.
        :return: a template
        """
        close = False
        f = file
        if isinstance(file, basestring):
            f = open(file, 'r')
            close = True
        try:
            data = _decode_unicode(f.read(), charset, errors)
        finally:
            if close:
                f.close()
        return cls(data, getattr(f, 'name', '<template>'), charset,
                   errors, unicode_mode)

    def render(self, *args, **kwargs):
        """This function accepts either a dict or some keyword arguments which
        will then be the context the template is evaluated in.  The return
        value will be the rendered template.

        :param context: the function accepts the same arguments as the
                        :class:`dict` constructor.
        :return: the rendered template as string
        """
        ns = self.default_context.copy()
        if len(args) == 1 and isinstance(args[0], MultiDict):
            ns.update(args[0].to_dict(flat=True))
        else:
            ns.update(dict(*args))
        if kwargs:
            ns.update(kwargs)
        context = Context(ns, self.charset, self.errors)
        exec self.code in context.runtime, context
        return context.get_value(self.unicode_mode)

    def substitute(self, *args, **kwargs):
        """For API compatibility with `string.Template`."""
        return self.render(*args, **kwargs)
