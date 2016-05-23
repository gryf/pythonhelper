#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys


class Command(object):
    def __call__(self, args):
        print(args)


class Window(object):
    def __init__(self):
        self.cursor = (1, 1)


class Current(object):
    def __init__(self):
        with open('test_py_example.py') as fobj:
            self.buffer = fobj.read().split('\n')
        self.window = Window()


class MockVim(object):
    current = Current()
    command = Command()


sys.modules['vim'] = vim = MockVim


import pythonhelper


class TestTagsHelper(unittest.TestCase):

    def test_import(self):
        vim.current.window.cursor = (1, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 2)
        self.assertIsNone(tag)

    def test_class(self):
        vim.current.window.cursor = (4, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'class')

        vim.current.window.cursor = (6, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'class')

        vim.current.window.cursor = (7, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'class')

    def test_init(self):
        vim.current.window.cursor = (9, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'method')

        vim.current.window.cursor = (11, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'method')

    def test_method(self):
        vim.current.window.cursor = (13, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'method')

        vim.current.window.cursor = (15, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'method')

        vim.current.window.cursor = (24, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'method')

        # those tests should run if we have some kind of lexer analiser, not a
        # simple py source parser.
        #
        # vim.current.window.cursor = (32, 1)
        # tag = pythonhelper.PythonHelper._get_tag(1, 3)
        # self.assertEqual(tag.tag_type, 'method')

        # vim.current.window.cursor = (34, 1)
        # tag = pythonhelper.PythonHelper._get_tag(1, 3)
        # self.assertEqual(tag.tag_type, 'method')

    def test_inner_function(self):
        vim.current.window.cursor = (16, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

        vim.current.window.cursor = (18, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

        vim.current.window.cursor = (22, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

        vim.current.window.cursor = (23, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

    def test_main(self):
        vim.current.window.cursor = (37, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

        vim.current.window.cursor = (38, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

        vim.current.window.cursor = (40, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertEqual(tag.tag_type, 'function')

    def test_ifmain(self):
        vim.current.window.cursor = (41, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertIsNone(tag)

        vim.current.window.cursor = (42, 1)
        tag = pythonhelper.PythonHelper._get_tag(1, 3)
        self.assertIsNone(tag)


if __name__ == "__main__":
    unittest.main()
