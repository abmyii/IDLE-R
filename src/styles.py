#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  styles.py
#  
#  Copyright 2015-2016 abmyii
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Whitespace


class PythonStyle(Style):
    """
    A colorful style, inspired by the IDLE style.
    """

    default_style = ""

    styles = {
        Whitespace:                 '#ffffff', # Whitespace (html)

        Comment:                    '#dd0000', # Comments
        Comment.Preproc:            '#dd0000', # Comments (?)
        Comment.Special:            '#dd0000', # Comments (?)

        Keyword:                    '#ff7700', # Keywords
        Keyword.Type:               '#ff7700', # Keywords

        Operator.Word:              '#ff7700', # in, and, or (and such)

        Name.Builtin:               '#800080', # all, abs (and such)
        Name.Builtin.Pseudo:        '#800080', # self, True, False
        Name.Function:              '#0000aa', # def <name.function>
        Name.Class:                 '#0000aa', # class <name.class>
        Name.Namespace:             '#000000', # import <...> or from <...>
        Name.Variable:              '#aa0000', # ?
        Name.Constant:              '#aa0000', # ?
        Name.Entity:                'bold #800', # ?
        Name.Attribute:             '#1e90ff', # ?
        Name.Tag:                   'bold #1e90ff', # ?
        Name.Decorator:             '#555555', # Decorator

        String:                     '#008000', # String
        String.Symbol:              '#008000', # String
        String.Regex:               '#008000', # String

        Number:                     '#005000',  # Numbers

        Generic.Heading:            'bold #000080', # ?
        Generic.Subheading:         'bold #800080', # ?
        Generic.Deleted:            '#aa0000', # ?
        Generic.Inserted:           '#00aa00', # ?
        Generic.Error:              '#aa0000', # ?
        Generic.Emph:               'italic', # ?
        Generic.Strong:             'bold', # ?
        Generic.Prompt:             '#555555', # ?
        Generic.Output:             '#888888', # ?
        Generic.Traceback:          '#aa0000', # ?

        Error:                      '#F00 bg:#FAA' # Errors
    }
