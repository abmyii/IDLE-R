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

class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.red)
        keywordPatterns = []
        for kw in keyword.kwlist:
            if not kw == 'print':
                keywordPatterns.append('\\b' + kw + '\\b')
        self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]
        
        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setForeground(QtCore.Qt.blue)
        self.highlightingRules.append((QtCore.QRegExp(" [A-Za-z0-9_]+(?=\\()"),
                functionFormat))

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkMagenta)
        keywordPatterns = []
        for d in dir(__builtin__):
            if not '_' in d:
                keywordPatterns.append('\\b' + d + '\\b')
        highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]
        for rule in highlightingRules: self.highlightingRules.append(rule)

        commentFormat = QtGui.QTextCharFormat()
        commentFormat.setForeground(QtCore.Qt.darkRed)
        self.highlightingRules.append((QtCore.QRegExp(r"#[^\n]*"),
                commentFormat))
        
        stringFormat = QtGui.QTextCharFormat()
        stringFormat.setForeground(QtCore.Qt.darkGreen)
        stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
        self.highlightingRules.append((QtCore.QRegExp(stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"),
                stringFormat))
        self.highlightingRules.append((QtCore.QRegExp(stringprefix +  r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'),
                stringFormat))
        self.highlightingRules.append((QtCore.QRegExp(stringprefix +  r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"),
                stringFormat))
        self.highlightingRules.append((QtCore.QRegExp(stringprefix +  r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'),
                stringFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
