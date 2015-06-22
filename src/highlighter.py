#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  highlighter.py
#  
#  Copyright 2015 abmyii
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
from PyQt4 import Qt, QtCore, QtGui
import keyword
import __builtin__
import re

# Taken from KhtEditor
class BracketsInfo:

    def __init__(self, character, position):
        self.character = character
        self.position = position

# Taken from KhtEditor
class TextBlockData(QtGui.QTextBlockUserData):

    def __init__(self, parent=None):
        super(TextBlockData, self).__init__()
        self.braces = []
        self.valid = False

    def insert_brackets_info(self, info):
        self.valid = True
        self.braces.append(info)

    def isValid(self):
        return self.valid

class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        # Used and edited from IDLE codebase
        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setForeground(QtCore.Qt.blue)
        self.highlightingRules = [(r'\bdef\b\s*(\w+)', functionFormat)]
        self.highlightingRules.append((r'\bclass\b\s*(\w+)', functionFormat))
        
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.red)
        for kw in keyword.kwlist:
            if not kw == 'print':
                self.highlightingRules.append(('\\b' + kw + '\\b', keywordFormat))

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkMagenta)
        for d in dir(__builtin__):
            if not '_' in d:
                self.highlightingRules.append(('\\b' + d + '\\b', keywordFormat))

        commentFormat = QtGui.QTextCharFormat()
        commentFormat.setForeground(QtCore.Qt.darkRed)
        self.highlightingRules.append((r"#[^\n]*",
                commentFormat))
        
        self.stringFormat = QtGui.QTextCharFormat()
        self.stringFormat.setForeground(QtCore.Qt.darkGreen)
        self.stringprefix = stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
        self.highlightingRules.append((stringprefix + r"""((?!''')'[^']*'?|(?!\""")"[^"]*"?)""",
                self.stringFormat))
        
        # Tri strings
        self.tri_single = QtCore.QRegExp(stringprefix + r"""'''(?!")""")
        self.tri_double = QtCore.QRegExp(stringprefix + r'''"""(?!')''')
        self.tri_single = ( self.tri_single, 1, self.stringFormat )
        self.tri_double = ( self.tri_double, 2, self.stringFormat )

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = re.compile(pattern, re.S).finditer(text)
            while True:
                try:
                    expr = expression.next()
                    index = expr.start()
                    end = expr.end()
                    length = end - index
                    self.setFormat(index, length, format)
                except StopIteration:  # End of iter
                    break
        
        self.match_multiline(text, *self.tri_single)
        self.match_multiline(text, *self.tri_double)
    
    # Taken from KhtEditor
    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
