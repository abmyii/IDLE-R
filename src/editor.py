#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  editor.py
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
from highlighter import SyntaxHighlighter

class Editor(QtGui.QTextEdit):
    isUntitled = False
    fname = ''
    
    def __init__(self):
        super(Editor, self).__init__()
        
        # Highlighting current line
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                     self.highlight_current_line)
        self.highlight_current_line()
        
        # Syntax highlighting
        SyntaxHighlighter(self)
    
    def isModified(self):
        return self.document().isModified()
        
    def setModified(self, modified):
        return self.document().setModified(modified)
    
    def keyPressEvent(self, QKeyEvent):
        """Handle keypress events"""
        
        if QKeyEvent.text() == '\r':
            pos = self.textCursor().position()
            if pos >= 1:
                char = self.document().characterAt(pos - 1)
                if char == QtCore.QChar(0x3a):
                    self.textCursor().beginEditBlock()
                    self.insertPlainText('\n\t')
                    self.textCursor().endEditBlock()
                    return

        super(Editor, self).keyPressEvent(QKeyEvent)
    
    def highlight_current_line(self):
        self.extraSelections = []
        
        block = self.textCursor()
        selection = self.ExtraSelection()
        lineColor = QtGui.QColor("#858585")
        lineColor.setAlpha(20)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)
