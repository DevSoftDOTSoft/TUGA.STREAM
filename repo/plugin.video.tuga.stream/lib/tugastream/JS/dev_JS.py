#!/usr/bin/python
# coding=utf-8

import sys,os

scripts_import = [os.getcwd() + '\\js2py']
for script in scripts_import:
    if not script in sys.path:
        sys.path.insert(0, script)

import js2py

def resolve_js(js):
    return js2py.eval_js(js)


def test():
    js_test = """
        function test(){
            return 1;
        }
        test();
    """

    res = resolve_js(js_test)
    print("Started up JS_TEST with ---> " + str(res))

#Startup_Test
test()