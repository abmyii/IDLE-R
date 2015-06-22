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
import pygments
import pygments.lexers

class CommentRange:
    def __init__(self, index, length=0):
        self.index = index
        self.length = length
        
    def __lt__ (left,  right):
        return left.index < right.index


class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.red)
        keywordPatterns = []
        for kw in keyword.kwlist:
            if not kw == 'print':
                keywordPatterns.append('\\b' + kw + '\\b')
        self.highlightingRules = [(pattern, keywordFormat)
                for pattern in keywordPatterns]
        
        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setForeground(QtCore.Qt.blue)
        self.highlightingRules.append((" [A-Za-z0-9_]+(?=\\()",
                functionFormat))

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkMagenta)
        keywordPatterns = []
        for d in dir(__builtin__):
            if not '_' in d:
                keywordPatterns.append('\\b' + d + '\\b')
        highlightingRules = [(pattern, keywordFormat)
                for pattern in keywordPatterns]
        for rule in highlightingRules: self.highlightingRules.append(rule)

        commentFormat = QtGui.QTextCharFormat()
        commentFormat.setForeground(QtCore.Qt.darkRed)
        self.highlightingRules.append((r"#[^\n]*",
                commentFormat))
        
        self.stringFormat = QtGui.QTextCharFormat()
        self.stringFormat.setForeground(QtCore.Qt.darkGreen)
        self.stringprefix = stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
        self.highlightingRules.append((stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?",
                self.stringFormat))
        self.highlightingRules.append((stringprefix +  r'"[^"\\\n]*(\\.[^"\\\n]*)*"?',
                self.stringFormat))

    def highlightBlock(self, text):
        text = str(self.document().toPlainText())
        lex = pygments.lex(text, pygments.lexers.PythonLexer())
        
        ##types = ('"""', "'''")
        #types = ('"""')
        #for strType in types:
            #index = types.index(strType) + 1
            
            ## Comment expressions
            #self.commentStartExpression = QtCore.QRegExp(self.stringprefix + strType)
            #self.commentEndExpression = QtCore.QRegExp(strType)

            #self.setCurrentBlockState(0)
    
            #startIndex = 0
            #if self.previousBlockState() != 1:
                #startIndex = self.commentStartExpression.indexIn(text)
    
            #while startIndex >= 0:
                #endIndex = self.commentEndExpression.indexIn(text, startIndex + 1)
    
                #if endIndex == -1:
                    #self.setCurrentBlockState(index)
                    #commentLength = len(text) - startIndex
                #else:
                    #commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
    
                #self.setFormat(startIndex, commentLength,
                        #self.stringFormat)
                #startIndex = self.commentStartExpression.indexIn(text,
                        #startIndex + commentLength)
        
        #for pattern, format in self.highlightingRules:
            #expression = re.compile(pattern, re.S).finditer(text)
            #while True:
                #try:
                    #expr = expression.next()
                    #index = expr.start()
                    #end = expr.end()
                    #length = end - index
                    #if pattern == " [A-Za-z0-9_]+(?=\\()":
                        #if 'class' in [text[index-5:index]] or 'def' in [text[index-3:index]]:
                            #self.setFormat(index, length, format)
                    #elif '"' in pattern or "'" in pattern:
                        #if not self.previousBlockState() in [1, 2]:
                            #self.setFormat(index, length, format)
                    #else:
                        #self.setFormat(index, length, format)
                #except StopIteration:  # End of iter
                    #break
