"""
Simple analyzer for python source files. Collect and give info about file
structure: classes, its methods and functions.

Note, it'll probably not be behaving well with mixed spaces and tabs
indentation.

version: 1.0
date: 2016-05-30
author: Roman Dobosz <gryf@vimja.com>
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

    def __repr__(self):
        """Representation for the PythonTag objects"""
        return ("<PythonTag object at %s: %0.2d [%d] %s %s>" %
                (hex(id(self)),
                 self.line_number,
                 self.indent_level,
                 self.tag_type,
                 self.full_name))


class EvenSimplerPythonTagsParser(object):
    """Simplified version for Python source code tag parser."""

    def get_tags(self):
        """
        Find tag in current buffer. Store them in OrderedDict and return.

        :returns: OrderedDict with tags for current buffer or empty
                  OrderedDict in case of no tags found.
        """
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
        """
        Calculate name for provided tag.

        :param tag: PythonTag object
        :param tags_stack: list of PythonTag objects ordered from root to leaf

        :returns: 'class', 'method' or 'function' as a tag type
        """
        if tag.tag_type == 'class':
            return 'class'

        if tags_stack and tags_stack[-1].tag_type == 'class':
            return 'method'

        return 'function'

    def _get_full_name(self, tags_stack, name):
        """
        Return full logical name dot separated starting from upper entity

        :param tags_stack: list of PythonTag objects ordered from root to leaf
        :param name: class, method or function name

        :returns: full name starting from root, separated by dot, like:
                  function_name
                  ClassName
                  ClassName.method_name
                  ClassName.method_name.inner_function_name
        """
        if tags_stack:
            return tags_stack[-1].full_name + "." + name

        return name

    def _get_indent_level(self, line):
        """
        Calculate and get the indentation level for provided line

        :param line: a string, against which indentation should be calculated

        :returns: counted number of whitespaces

        """
        return len(RE_INDENT.match(line).group(1))


class PythonHelper(object):
    TAGS = {}

    @classmethod
    def find_tag(cls, buffer_number, changed_tick):
        """
        Tries to find the best tag for the current cursor position.

        :param buffer_number: buffer number in vim
        :param changed_tick: always-increasing number used to indicate that
                             the buffer has been modified since the last time
        """
        tag = PythonHelper._get_tag(buffer_number, changed_tick)

        s_line = '%s (%s)' % (tag.full_name, tag.tag_type) if tag else ''
        s_line_tag = tag.full_name if tag else ''
        s_line_type = tag.tag_type if tag else ''

        vim.command('let w:PHStatusLine="%s"' % s_line)
        vim.command('let w:PHStatusLineTag="%s"' % s_line_tag)
        vim.command('let w:PHStatusLineType="%s"' % s_line_type)

    @classmethod
    def _get_tag(cls, buffer_number, changed_tick):
        """
        Get the nearest tag object or None.

        :param buffer_number: buffer number in vim
        :param changed_tick: always-increasing number used to indicate that
                             the buffer has been modified since the last time

        :returns: PythonTag tag object or None
        """

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
            try:
                line = vim.current.buffer[line_number]
            except IndexError:
                return None

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
        """Removes tag data for the specified buffer number.

        :param buffer_number: buffer number in vim
        """
        try:
            del PythonHelper.TAGS[buffer_number]
        except KeyError:
            # If we don't have tags for specified buffer, just pass
            pass
