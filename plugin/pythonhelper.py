"""
Simple analyzer for python source files. Collect and give info about file
structure: classes, its methods and functions.
"""
import re
import sys
import time
import vim


# global dictionaries of tags and their line numbers, keys are buffer numbers
TAGS = {}
TAGLINENUMBERS = {}
BUFFERTICKS = {}


class PythonTag(object):
    """A simple storage class representing a python tag."""
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"

    def __init__(self, tag_type, name, full_name, line_number, indent_level):
        """Initializes instances of Python tags.

        :param tag_type: Tag type as string
        :param name: Short tag name
        :param full_name: Full tag name (in dotted notation)
        :param line_number: line number on which the tag starts
        :param indent_level: indentation level of the tag (number)
        """
        self.tag_type = tag_type
        self.name = name
        self.full_name = full_name
        self.line_number = line_number
        self.indent_level = indent_level

    def __str__(self):
        """Returns a string representation of the tag."""
        return "%s (%s) [%s, %u, %u]" % (self.name,
                                         self.tag_type,
                                         self.full_name,
                                         self.line_number,
                                         self.indent_level,)

    __repr__ = __str__


class SimplePythonTagsParser(object):
    """Provides a simple Python tag parser."""
    # how many chars a single tab represents (visually)
    TABSIZE = 8
    # regexp used to extract indentation and strip comments
    COMMENTS_INDENT_RE = re.compile('([ \t]*)([^\n#]*).*')
    # regexp used to extract a class name
    CLASS_RE = re.compile('class[ \t]+([^(:]+).*')
    # regexp used to extract a method or function name
    METHOD_RE = re.compile('def[ \t]+([^(]+).*')

    def __init__(self, source):
        """
        Initializes instances of SimplePythonTagsParser().

        :param source: source for which the tags will be generated. It must
                       be a generator.
        """
        self.source = source

    def get_tags(self):
        """
        Determines all the tags for the buffer.

        :returns: tuple in the format (tag_line_numbers, tags,).
        """
        tag_line_numbers = []
        tags = {}
        tags_stack = []

        import itertools
        # go through all the lines in the source and localize all Python tags
        # in it
        for (line, line_number) in zip(self.source, itertools.count(1)):

            # extract the line's indentation characters and its content
            line_match = self.COMMENTS_INDENT_RE.match(line)
            line_content = line_match.group(2)

            # match for the class tag
            tag_match = self.CLASS_RE.match(line_content)

            # if the class tag has been found, store some information on it
            if tag_match:
                current_tag = self.get_python_tag(tags_stack, line_number,
                                                  line_match.group(1),
                                                  tag_match.group(1),
                                                  self.tag_class_type_deciding_method)
                tag_line_numbers.append(line_number)
                tags[line_number] = current_tag

            else:
                # match for the method/function tag
                tag_match = self.METHOD_RE.match(line_content)

                # if the method/function tag has been found, store some
                # information on it
                if tag_match:
                    current_tag = self.get_python_tag(tags_stack,
                                                      line_number,
                                                      line_match.group(1),
                                                      tag_match.group(1),
                                                      self.tag_function_type_deciding_method)
                    tag_line_numbers.append(line_number)
                    tags[line_number] = current_tag

        return (tag_line_numbers, tags,)

    def get_parent_tag(self, tags_stack):
        """
        Given a tag, returns its parent tag (instance of PythonTag()) from the
        specified tag list. If no such parent tag exists, returns None.

        :param tags_stack: list (stack) of currently open PythonTag() instances
        """
        if len(tags_stack):
            parent_tag = tags_stack[-1]
        else:
            parent_tag = None

        return parent_tag

    def compute_indentation_level(indent_chars):
        """
        Computes the indentation level from the specified string.

        indent_chars -- white space before any other character on line
        """
        indent_level = 0

        # compute the indentation level (expand tabs)
        for char in indent_chars:
            if char == '\t':
                indent_level += SimplePythonTagsParser.TABSIZE
            else:
                indent_level += 1

        return indent_level

    compute_indentation_level = staticmethod(compute_indentation_level)

    def get_python_tag(self, tags_stack, line_number, indent_chars, tag_name,
                       tag_type_deciding_method):
        """
        Returns instance of PythonTag based on the specified data.

        Parameters

            tags_stack -- list (stack) of tags currently active. Note: Modified
                in this method!

            line_number -- current line number

            indent_chars -- characters making up the indentation level of the
                current tag

            tag_name -- short name of the current tag

            tag_type_deciding_method -- reference to the method that is called to
                determine the type of the current tag
        """
        indent_level = self.compute_indentation_level(indent_chars)
        parent_tag = self.get_parent_tag(tags_stack)

        # handle enclosed tag
        while parent_tag:
            # if the indent level of the parent tag is greater than of the
            # current tag, use parent tag of the parent tag
            if parent_tag.indent_level >= indent_level:
                del tags_stack[-1]

            # otherwise we have all information on the current tag and can
            # return it
            else:
                tag = PythonTag(tag_type_deciding_method(parent_tag.tag_type),
                                tag_name, "%s.%s" % (parent_tag.full_name,
                                                     tag_name,),
                                line_number, indent_level)

                break

            # use the parent tag of the parent tag
            parent_tag = self.get_parent_tag(tags_stack)

        # handle a top-indent level tag
        else:
            tag = PythonTag(tag_type_deciding_method(None), tag_name, tag_name,
                            line_number, indent_level)

        # add the tag to the list of tags
        tags_stack.append(tag)

        return tag

    def tag_class_type_deciding_method(self, parent_tag_type):
        """
        Returns tag type of the current tag based on its previous tag (super
        tag) for classes.

        Parameters

            parent_tag_type -- type of the enclosing/parent tag
        """
        return PythonTag.CLASS

    def tag_function_type_deciding_method(self, parent_tag_type):
        """
        Returns tag type of the current tag based on its previous tag (super
        tag) for functions/methods.

        Parameters

            parent_tag_type -- type of the enclosing/parent tag
        """
        if parent_tag_type == PythonTag.CLASS:
            return PythonTag.METHOD
        else:
            return PythonTag.FUNCTION


def vim_buffer_iterator(vim_buffer):
    for line in vim_buffer:
        yield line + "\n"


def get_nearest_line_index(row, tag_line_numbers):
    """
    Returns the index of 'tag_line_numbers' that contains the line nearest to
    the specified cursor row.

    Parameters

        row -- current cursor row

        tag_line_numbers -- list of tags' line numbers (ie. their position)
    """
    nearest_line_number = -1
    nearest_line_index = -1

    # go through all tag line numbers and find the one nearest to the
    # specified row
    for line_index, line_number in enumerate(tag_line_numbers):
        # if the current line is nearer the current cursor position, take it
        if nearest_line_number < line_number <= row:
            nearest_line_number = line_number
            nearest_line_index = line_index

        # if we've come past the current cursor position, end the search
        if line_number >= row:
            break

    return nearest_line_index


def get_tags(buffer_number, changed_tick):
    """
    Reads the tags for the buffer specified by the number. Returns a tuple
    of the format (taglinenumber[buffer], tags[buffer],).

    Parameters

        buffer_number -- number of the current buffer

        changed_tick -- always-increasing number used to indicate that the
            buffer has been modified since the last time
    """
    global TAGLINENUMBERS, TAGS, BUFFERTICKS

    # return immediately if there's no need to update the tags
    if (BUFFERTICKS.get(buffer_number, None) == changed_tick):
        return (TAGLINENUMBERS[buffer_number], TAGS[buffer_number])

    # get the tags
    simple_tags_parser = SimplePythonTagsParser(vim_buffer_iterator(vim.current.buffer))
    tag_line_numbers, tags = simple_tags_parser.get_tags()

    # update the global variables
    TAGS[buffer_number] = tags
    TAGLINENUMBERS[buffer_number] = tag_line_numbers
    BUFFERTICKS[buffer_number] = changed_tick

    return (tag_line_numbers, tags)


def find_tag(buffer_number, changed_tick):
    """
    Tries to find the best tag for the current cursor position.

    Parameters

        buffer_number -- number of the current buffer

        changed_tick -- always-increasing number used to indicate that the
            buffer has been modified since the last time
    """
    try:
        # get the tag data for the current buffer
        tag_line_numbers, tags = get_tags(buffer_number, changed_tick)

        # link to Vim's internal data
        current_buffer = vim.current.buffer
        current_window = vim.current.window
        row, col = current_window.cursor

        # get the index of the nearest line
        nearest_line_index = get_nearest_line_index(row, tag_line_numbers)

        # if a line has been found, find out if the tag is correct {{{
        # E.g. the cursor might be below the last tag, but in code that has
        # nothing to do with the tag, which we know because the line is
        # indented differently. In such a case no applicable tag has been
        # found.
        while nearest_line_index > -1:
            # get the line number of the nearest tag
            nearest_line_number = tag_line_numbers[nearest_line_index]

            # walk through all the lines in the range (nearestTagLine,
            # cursorRow)
            for line_number in xrange(nearest_line_number + 1, row):
                # get the current line
                line = current_buffer[line_number]

                # count the indentation of the line, if it's lower than the
                # tag's, the tag is invalid
                if len(line):
                    # initialize local auxiliary variables
                    line_start = 0
                    i = 0

                    # compute the indentation of the line
                    while (i < len(line)) and (line[i].isspace()):
                        # move the start of the line code
                        if line[i] == '\t':
                            line_start += SimplePythonTagsParser.TABSIZE
                        else:
                            line_start += 1

                        # go to the next character on the line
                        i += 1

                    # if the line contains only spaces, skip it
                    if i == len(line):
                        continue

                    # if the next character is a '#' (python comment), skip
                    # to the next line
                    if line[i] == '#':
                        continue

                    # if the line's indentation starts before or at the
                    # nearest tag's, the tag is invalid
                    if line_start <= tags[nearest_line_number].indent_level:
                        nearest_line_index -= 1
                        break

            # the tag is correct, so use it
            else:
                break

        # no applicable tag has been found
        else:
            nearest_line_number = -1

        # describe the cursor position (what tag the cursor is on)
        # reset the description
        tag_description = ""
        tag_description_tag = ""
        tag_description_type = ""

        # if an applicable tag has been found, set the description accordingly
        if nearest_line_number > -1:
            tag_info = tags[nearest_line_number]
            tag_description_tag = tag_info.full_name
            tag_description_type = tag_info.tag_type
            tag_description = "%s (%s)" % (tag_description_tag,
                                           tag_description_type)

        # update the variable for the status line so it get updated with the
        # new description
        vim.command("let w:PHStatusLine=\"%s\"" % (tag_description,))
        vim.command("let w:PHStatusLineTag=\"%s\"" % (tag_description_tag,))
        vim.command("let w:PHStatusLineType=\"%s\"" % (tag_description_type,))

    # handle possible exceptions
    except Exception:
        # FIXME: wrap try/except blocks around single sources of exceptions
        # ONLY. Break this try/except block into as many small ones as you
        # need, and only catch classes of exceptions that you have encountered.
        # Catching "Exception" is very, very bad style!
        # To the author: why is this clause here? There's no git log for why you
        # have added it. Can you please put in a comment of a specific situation
        # where you have encountered exceptions?
        # bury into the traceback
        ec, ei, tb = sys.exc_info()
        while tb != None:
            if tb.tb_next == None:
                break
            tb = tb.tb_next

        # spit out the error
        print "ERROR: %s %s %s:%u" % (ec.__name__, ei,
                                      tb.tb_frame.f_code.co_filename,
                                      tb.tb_lineno)
        time.sleep(0.5)


def delete_tags(buffer_number):
    """
    Removes tag data for the specified buffer number.

    Parameters

        buffer_number -- number of the buffer
    """
    global TAGS, TAGLINENUMBERS, BUFFERTICKS

    # try to delete the tags for the buffer
    for o in (TAGS, TAGLINENUMBERS, BUFFERTICKS):
        try:
            del o[buffer_number]
        except KeyError:
            pass
