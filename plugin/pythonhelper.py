"""
Simple analyzer for python source files. Collect and give info about file
structure: classes, its methods and functions.

version: 0.2
date: 2016-05-21
author: Roman Dobosz <gryf@vimja.com>

TODO: - fix the corner case with applying a tag, where it shouldn't do. like:

1    def foo():
2        pass
3
4    if True == False:
5        foo()

where line 5 is reporting as a function foo() body, which is not true.

"""
from collections import OrderedDict
import re

import vim


RE_TAG_TYPE = re.compile(r'\s*(def|class)[ \t]+([^(:]+).*')
RE_INDENT = re.compile(r'([ \t]*).*')


class PythonTag(object):
    """A simple storage class representing a python tag."""

    def __init__(self, tag_type='', full_name='', line_number=0,
                 indent_level=0):
        """Initializes instances of Python tags.

        :param tag_type: Tag type as string
        :param full_name: Full tag name (in dotted notation)
        :param line_number: line number on which the tag starts
        :param indent_level: indentation level of the tag (number)
        """
        self.tag_type = tag_type
        self.name = full_name.split(".")[-1]
        self.full_name = full_name
        self.line_number = line_number
        self.indent_level = indent_level

    def __str__(self):
        """Returns a string representation of the tag."""
        return "%0.2d [%d] %s %s" % (self.line_number,
                                     self.indent_level,
                                     self.tag_type,
                                     self.full_name)

    __repr__ = __str__


class EvenSimplerPythonTagsParser(object):
    """Simplified version for Python source code tag parser."""

    def get_tags(self):
        """Return OrderedDict with all tags for current buffer"""
        tags_stack = []
        tags = OrderedDict()

        for line_no, line in enumerate(vim.current.buffer):

            tag_match = RE_TAG_TYPE.match(line)

            if not tag_match:
                continue

            indent_level = self._get_indent_level(line)

            for _ in range(len(tags_stack)):
                if tags_stack and tags_stack[-1].indent_level >= indent_level:
                    tags_stack.pop()

                if not tags_stack:
                    break

            tag = PythonTag(tag_match.group(1),
                            self._get_full_name(tags_stack,
                                                tag_match.group(2)),
                            line_no,
                            indent_level)
            tag.tag_type = self._get_tag_type(tag, tags_stack)

            tags[line_no] = tag
            tags_stack.append(tag)

        return tags

    def _get_tag_type(self, tag, tags_stack):
        """Return proper type of the tag depending on context"""
        if tag.tag_type == 'class':
            return 'class'

        if tags_stack and tags_stack[-1].tag_type == 'class':
            return 'method'

        return 'function'

    def _get_full_name(self, tags_stack, name):
        """Return full logical name dot separated starting from upper entity"""
        if tags_stack:
            return tags_stack[-1].full_name + "." + name

        return name

    def _get_indent_level(self, line):
        """Return indentation level as a simple count of whitespaces"""
        return len(RE_INDENT.match(line).group(1))


class PythonHelper(object):
    TAGS = {}

    @classmethod
    def find_tag(cls, buffer_number, changed_tick):
        """
        Tries to find the best tag for the current cursor position.

        Parameters

            buffer_number -- number of the current buffer

            changed_tick -- always-increasing number used to indicate that the
                buffer has been modified since the last time
        """
        tag = PythonHelper._get_tag(buffer_number, changed_tick)
        update_vim_vars(tag)

    @classmethod
    def _get_tag(cls, buffer_number, changed_tick):
        """Return the nearset tag object or None"""

        if PythonHelper.TAGS.get(buffer_number) and \
           PythonHelper.TAGS[buffer_number]['changed_tick'] == changed_tick:
            tags = PythonHelper.TAGS[buffer_number]['tags']
        else:
            parser = EvenSimplerPythonTagsParser()
            tags = parser.get_tags()
            PythonHelper.TAGS['buffer_number'] = {'changed_tick': changed_tick,
                                                  'tags': tags}

        # get line number of current cursor position from Vim's internal data.
        # It is always a positive number, starts from 1. Let's decrease it by
        # one, so that it will not confuse us while operating vim interface by
        # python, where everything starts from 0.
        line_number = vim.current.window.cursor[0] - 1

        while True:
            line = vim.current.buffer[line_number]
            line_indent = len(RE_INDENT.match(line).group(1))
            if line.strip():
                break
            # line contains nothing but white characters, looking up to grab
            # some more context
            line_number -= 1

        tag = tags.get(line_number)

        # if we have something at the beginning of the line, just return it;
        # it doesn't matter if it is the tag found there or not
        if line_indent == 0 or tag:
            return tag

        # get nearest tag
        for line_no in range(line_number - 1, 0, -1):
            tag = tags.get(line_no)
            line = vim.current.buffer[line_no]
            upper_line_indent = len(RE_INDENT.match(line).group(1))

            if tag and upper_line_indent < line_indent:
                return tag

            if not line.strip():
                continue

            if upper_line_indent == 0:
                return None

            if upper_line_indent >= line_indent:
                continue

            if tag and tag.indent_level >= line_indent:
                tag = None
                continue

        return tag

    @classmethod
    def delete_tags(cls, buffer_number):
        """Removes tag data for the specified buffer number."""
        del PythonHelper.TAGS[buffer_number]


def update_vim_vars(tag):
    """Update Vim variable usable with vimscript side of the plugin"""

    if not tag:
        vim.command('let w:PHStatusLine=""')
        vim.command('let w:PHStatusLineTag=""')
        vim.command('let w:PHStatusLineType=""')
    else:
        vim.command('let w:PHStatusLine="%s (%s)"' % (tag.full_name,
                                                      tag.tag_type))
        vim.command('let w:PHStatusLineTag="%s"' % tag.tag_type)
        vim.command('let w:PHStatusLineType="%s"' % tag.full_name)
