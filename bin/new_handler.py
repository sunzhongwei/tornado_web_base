#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------
# DESCRIPTION
# ===========
#
# ----------------------------------------

# build-in, 3rd party and my modules
import sys
import os.path


cur_file_path = os.path.realpath(__file__)
cur_dir_path = os.path.dirname(cur_file_path)
src_dir_path = os.path.join(cur_dir_path, "../src")
template_dir_path = os.path.join(src_dir_path, "template")


def print_help():
    help_msg = '''usage: ./new_handler.py <handler_name> <--html|--no-html> '''
    print help_msg


def generate_handler_py_file(handler_name, need_html):
    '''In [7]: "server_haha".title().replace("_", "")
    Out[7]: 'ServerHaha'
    '''
    if need_html:
        rsp_statement = 'self.render("%s.html")' % handler_name
    else:
        rsp_statement = 'self.write("Hello world!")'

    py_file_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------
# DESCRIPTION
# ===========
#
# ----------------------------------------

# build-in, 3rd party and my modules
import base


class %sHandler(base.BaseHandler):
    def get(self):
        %s


# ----------------------------------------
# test cases
# ----------------------------------------
def run_doctest():
    import doctest
    doctest.testmod()


if '__main__' == __name__:
    pass


''' % (handler_name.title().replace("_", ""), rsp_statement)

    py_handler_file = os.path.join(src_dir_path, "%s.py" % handler_name)
    with open(py_handler_file, "w") as f:
        f.write(py_file_content)


def generate_html_file(handler_name):
    html_file_content = '''{%% extends "base.html" %%}

{%% block title %%}%s{%% end %%}

{%% block body %%}
    <section>
        <header>
            <h1>Hello world!</h1>
        </header>
    </section>

    <section></section>
{%% end %%}''' % (handler_name, )

    html_file = os.path.join(template_dir_path, "%s.html" % handler_name)
    with open(html_file, "w") as f:
        f.write(html_file_content)


# ----------------------------------------
# test cases
# ----------------------------------------
def run_doctest():
    '''python -B <__file__> -v
    '''
    import doctest
    doctest.testmod()


if '__main__' == __name__:
    if len(sys.argv) != 3:
        print_help()
        sys.exit(1)

    handler_name = sys.argv[1]
    html_arg = sys.argv[2]
    if html_arg == "--html":
        need_html = True
    elif html_arg == "--no-html":
        need_html = False
    else:
        print "Invalid arguments!"
        print_help()
        sys.exit(1)

    generate_handler_py_file(handler_name, need_html)
    if need_html:
        generate_html_file(handler_name)
    print '''Manually add these lines to main.py:
    import %s
    (r"/%s", %s.%sHandler),

Add below line to base.html:
    <li><a href="/%s">%s</a></li>
    ''' % (handler_name, handler_name, handler_name,
            handler_name.title().replace("_", ""),
            handler_name, handler_name)


