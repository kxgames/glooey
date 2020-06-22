#!/usr/bin/env python3

import re
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.roles import AnyXRefRole
from pathlib import Path

class linebreak(nodes.General, nodes.Element):

    @staticmethod
    def visit_html(translator, node):
        translator.body.append('<br/>')

    @staticmethod
    def visit_latex(translator, node):
        translator.body.append(r'\linebreak')

    @staticmethod
    def visit_text(translator, node):
        translator.body.append('\n\n')

    @staticmethod
    def depart(translator, node):
        pass



class Demo(Directive):
    has_content = True
    required_arguments = 1

    def run(self):
        figure = nodes.figure()

        # Figure out what the show for this demo
        
        py_path = Path(self.arguments[0])
        zip_path = py_path.parent / (py_path.stem + '_assets.zip')
        png_path = py_path.parent / (py_path.stem + '.png')

        # Error out if the given python script doesn't exist.
        if py_path.suffix != '.py':
            raise self.error(f"'{py_path}' must be a python script.")

        if not py_path.exists():
            raise self.error(f"'{py_path}' doesn't exist.")
        
        if self.content:

            # Make sure the content is present in the given file.  Complain if 
            # there are differences.

            from textwrap import dedent

            with open(py_path) as py_file:
                py_code = [l.strip() for l in py_file.readlines()]

                for py_line in self.content:
                    if py_line.strip() not in py_code:
                        raise self.error(f"""\
Error in \"demo\" directive: The following line isn't present in '{py_path}':
{py_line}""")

            # Add a node for the code snippet

            from sphinx.directives.code import CodeBlock
            figure += self.make_snippet(self.content, png_path.exists())

        # Add a node for the screenshot

        if png_path.exists():
            figure += self.make_screenshot(png_path)

        # Add a node for the download links.
        
        caption = nodes.caption()
        caption += self.make_download_link(py_path)

        if zip_path.exists():
            caption += linebreak()
            caption += self.make_download_link(zip_path)

        figure += caption
        
        return [figure]

    def make_snippet(self, code, have_screenshot):
        code = '\n'.join(code)
        return nodes.literal_block(
                code, code,
                language='python',
                classes=['thin-margin' if have_screenshot else 'no-margin'],
        )

    def make_screenshot(self, path):
        return nodes.image(uri=str(path))

    def make_download_link(self, path):
        node = addnodes.download_reference(
                refdoc=self.state.document.settings.env.docname,
                refdomain='',
                refexplicit=False,
                reftarget=str(path),
                reftype='download',
                refwarn=True,
        )
        node += nodes.literal(
                '', str(path),
                classes=['xref', 'download'],
        )
        return node


class IndentedCodeBlock(directives.body.CodeBlock):
    # https://stackoverflow.com/questions/7034745/how-to-force-whitespace-in-code-block-in-restructuredtext
    INDENTATION_RE = re.compile("^ *")
    EXPECTED_INDENTATION = 3

    def run(self):
        block_lines = self.block_text.splitlines()
        block_header_len = self.content_offset - self.lineno + 1
        block_indentation = self.measure_indentation(self.block_text)
        code_indentation = block_indentation + self.EXPECTED_INDENTATION
        self.content = [ln[code_indentation:] for ln in block_lines[block_header_len:]]
        return super().run()

    @classmethod
    def measure_indentation(cls, line):
        return cls.INDENTATION_RE.match(line).end()
class SmartXRefRole(AnyXRefRole):

    def __init__(self):
        super().__init__(warn_dangling=True)

    def run(self):
        self.name = 'any'
        self.reftype = 'any'

        if self.target in self.config.smartxref_literals:
            return [nodes.literal(self.target, self.target)], []

        return super().run()

    def process_link(self, env, refnode, has_explicit_title, title, target):
        if target.startswith('~'):
            target = target[1:]
            title = target.split('.')[-1]

        target = self.config.smartxref_overrides.get(target, target)

        if '(' in target:
            target = target.split('(')[0]

        return super().process_link(env, refnode, has_explicit_title, title, target)

def setup(app): 
    app.add_directive('demo', Demo)
    app.add_directive('code', IndentedCodeBlock)

    app.add_node(
            linebreak,
            html=(linebreak.visit_html, linebreak.depart),
            latex=(linebreak.visit_latex, linebreak.depart),
            text=(linebreak.visit_text, linebreak.depart),
    )

    app.add_role('smartxref', SmartXRefRole())
    app.add_config_value('smartxref_overrides', {}, '')
    app.add_config_value('smartxref_literals', set(), '')

    app.add_css_file('css/custom.css')

