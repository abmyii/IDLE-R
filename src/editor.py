#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  editor.py
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
from PySide import QtCore, QtGui
from src.highlighter import PygmentsHighlighter
from src.extended import FindDialog, ReplaceDialog
import random

class LineArea(QtGui.QWidget):
    
    def __init__(self, editor):
        QtGui.QWidget.__init__(self, editor)
        self.editor = editor
    
    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(self.editor.lineAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineAreaPaintEvent(event)

class ColumnLine(LineArea):

    def paintEvent(self, event):
        self.editor.columnLinePaintEvent(event)

class Editor(QtGui.QPlainTextEdit):
    isUntitled = False
    fname = ''
    indentation = 0
    selectedBraces = 0
    # Vars for searching for text
    find_text = ''
    find_caseSensitive = 0
    find_fromStart = 0
    find_wholeWord = 0
    find_backward = 0
    # Vars for replacing text
    replace_text = '' 
    replace_with = ''
    replace_caseSensitive = 0
    replace_wholeWord = 0
    replace_backward = 0
    hadSelection = False
    inTemplate = False
    templateStart = 0
    
    def __init__(self, statusBar):
        super(Editor, self).__init__()
        
        # Set the Font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        
        # Status bar
        self.statusBar = statusBar
        
        # Syntax highlighting
        self.highlighter = PygmentsHighlighter(self)
        
        # Highlighting current line
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.highlight_current_line)
        self.highlight_current_line()
        
        # Update status bar
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.updateStatusBar)
        self.updateStatusBar()
        
        # Remove frame and set line wrap mode
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        
        # Draw the column line
        self.enableColumnLine = True
        self.columnLine = ColumnLine(self)
        fm = self.fontMetrics()
        self.columnLine.setGeometry((0.5 + fm.width('0')) * 80, 0, 1, 1000)
        
        # Create line number widget
        self.enableLineNumbers = True
        self.lineArea = LineArea(self)
        
        # Connect relevant signals to line number widget
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), \
                    self.updateLineAreaWidth)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'), \
                    self.updateLineArea)
        
        # Connect other signals
        self.connect(self, QtCore.SIGNAL('copyAvailable(bool)'), \
                    self.show_parens)
        
        # Tab & Cursor width
        self.setTabStopWidth(self.tabStopWidth() / 2)
        self.setCursorWidth(self.cursorWidth() * 2)
        
        # Initialize Line number widget
        self.updateLineAreaWidth()
    
    def autocomplete(self):
        # NOTES:
        # If Ctrl+Space is pressed, open autocomplete
        # If Tab pressed and no word under cursor, pass (fix on keyPressEvent)
        # If Tab pressed and word under cursor, open autocomplete (filter by word under cursor?)
        # If double Tab (quick taps?) and word under cursor, just tab. (TWEAK!)
        # If text under cursor >= 3 letters show
        pass
    
    def columnLinePaintEvent(self, event):
        if self.enableColumnLine:
            # Repaint on top first
            self.update()
            
            # Draw column line area
            painter = QtGui.QPainter(self.columnLine)
            color = QtGui.QColor("#22aa33")
            color.setAlpha(80)
            painter.fillRect(event.rect(), color)
    
    def find(self, text='', pos=None, comp=False, states={}):
        # Check and get text if none was given
        if not text:
            states = {
                'caseSensitive': self.find_caseSensitive,
                'fromStart': self.find_fromStart,
                'wholeWord': self.find_wholeWord,
                'backward': self.find_backward,
                'find_text': self.find_text,
            }
            text, states, successful = FindDialog(states).exec_()
            if not successful:
                return
            self.find_caseSensitive = states['caseSensitive']
            self.find_fromStart = states['fromStart']
            self.find_wholeWord = states['wholeWord']
            self.find_backward = states['backward']
            self.find_text = states['find_text']
        elif not states:
            states = {
                'caseSensitive': False,
                'wholeWord': False,
            }
        
        # If got text, then start finding
        if text:
            # Check there are occurences of the search text in the document.
            do = 0
            txt = text
            all_text = self.toPlainText()
            if not states['caseSensitive']:
                all_text = all_text.lower()
            if text in all_text: do = 1
            if not do and states['wholeWord']:
                if ' ' + txt + ' ' in all_text: do = 1
            if not do and comp and states['replaceAll']: states['backward'] = 1
            if do:
                self.find_text = text
                
                # Start search from cursor pos if no pos is given
                if pos is None: pos = self.textCursor().position()
                
                # Make options
                flags = QtGui.QTextDocument.FindFlag(0)
                if self.find_caseSensitive or comp and (states and states['caseSensitive']):
                    flags |= QtGui.QTextDocument.FindCaseSensitively
                if self.find_wholeWord or comp and (states and states['wholeWord']):
                    flags |= QtGui.QTextDocument.FindWholeWords
                if self.find_backward or comp and (states and states['backward']):
                    flags |= QtGui.QTextDocument.FindBackward
                
                # Find text
                if self.find_fromStart is 2 or comp and (states and states['replaceAll']):
                    cursor = self.document().find(self.find_text, 0, flags)
                    self.find_fromStart = 1
                else:
                    cursor = self.document().find(self.find_text, pos, flags)
                
                # Replace current cursor if there is a new one given
                if cursor.hasSelection():
                    self.setTextCursor(cursor)
                    if comp: return True
                else:
                    # Otherwise try searching from the beginning of the document
                    if comp: return False
                    self.find(text, 0, comp, states)
            elif comp: return False
    
    def goto_line(self):
        line, ok = QtGui.QInputDialog.getInt(self, "Goto", "Go to Line number:")
        if ok:
            self.moveCursor(QtGui.QTextCursor.Start)
            for _ in range(line - 1):
                self.moveCursor(QtGui.QTextCursor.Down)
    
    def highlight_current_line(self):
        selection = QtGui.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor("#858585")
        lineColor.setAlpha(20)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])
    
    def isInTemplate(self):
        find = self.toPlainText().find('<', self.templateStart)
        if find == -1:
            self.inTemplate = False
            return
        self.matchBraces('<', find, select=False, highlight=True)
        self.templateStart = find + 1
    
    def isModified(self):
        return self.document().isModified()
    
    def keyPressEvent(self, event):
        """Handle keypress events"""
        pos = self.textCursor().position()
        text = event.text()
        last = self.document().findBlock(pos).text().strip()
        # Make where when there is an undo, don't undo tabs (spaces?) and words
        
        if self.inTemplate:
            if text == '\t':
                self.isInTemplate()
                return
            elif text == u'\x1b':  # Key escape
                if self.textCursor().hasSelection():
                    # Move the text cursor to deselect
                    self.moveCursor(QtGui.QTextCursor.Left)
                    self.moveCursor(QtGui.QTextCursor.Right)
                self.inTemplate = False
                return
        
        if self.selectedBraces:
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
        
        # Handle backspaces
        if text == '\b':
            posInBlock = self.textCursor().positionInBlock()
            txt = self.document().findBlock(pos).text()
            dedent = 0
            if not txt.strip():
                dedent = len(txt)
            elif not txt[posInBlock-4:posInBlock].strip():
                dedent = 4
            if dedent:
                for i in range(dedent):
                    self.textCursor().deletePreviousChar()
                return
        
        # Insert spaces instead of tabs
        elif text == '\t':
            self.textCursor().beginEditBlock()
            self.insertPlainText('    ')
            self.textCursor().endEditBlock()
            return
            
        elif text in ['\r', '\n']:
            space = ''
            hasBrace = False
            subtract = 0
            
            # Add spaces for when cursor is in a brace that is not opened/closed
            char_pos = pos - len(last)
            ind_pos = 0
            for char in last:
                if char in '([{}])':
                    close = False if char in '([{' else True
                    if not self.matchBraces(char, char_pos, close):
                        ind_pos += 1
                    else:
                        subtract -= 4
                char_pos += 1
            if ind_pos:
                space += ' ' * (4 * ind_pos)
                hasBrace = True
            
            if last:
                char = last[-1]
                
                if char == ':':
                    space += '    '
                    
                if not hasBrace and char == '\\':
                    # Add extra spaces if there is a \ at the end of the line
                    space += ' ' * 4
            
            # Add last line's tabs to this line (keep indentaition)
            for char in self.document().findBlock(pos).text():
                if not subtract:
                    if char != ' ':
                        break
                    space += ' '
                else:
                    subtract += 1

            # Dedent if last word is one of the block-ending words
            if last in ['break', 'continue', 'pass', 'yield']:
                space = space[:-4]
            
            if subtract:
                space = space[:subtract]
            
            # Insert text and space
            self.textCursor().beginEditBlock()
            self.insertPlainText('\n' + space)
            self.textCursor().endEditBlock()
            self.ensureCursorVisible()
            self.update()
            return
        
        # Show brace formatting
        elif text and text in '([{}])':
            super(Editor, self).keyPressEvent(event)
            if text in '([{':
                self.matchBraces(text, pos, highlight=True)
            if text in ')]}':
                self.matchBraces(text, pos, True, highlight=True)
            return
        
        super(Editor, self).keyPressEvent(event)
            
        if not self.textCursor().hasSelection() and self.selectedBraces:
            self.selectedBraces = 0
    
    def matchBraces(self, brace, pos, close=False, highlight=False, select=1):
        if not close:
            searchText = self.toPlainText()[pos + 1:]
            other = {'(': ')', '[': ']', '{': '}', '<': '>'}.get(brace)
        else:
            searchText = self.toPlainText()[:pos][::-1]
            other = {')': '(', ']': '[', '}': '{', '>': '<'}.get(brace)
        level = 0  # for if there are other open/close brackets
        for char in enumerate(searchText):
            if char[1] == other:
                if level:
                    # We found the opposite brace, but for another open brace
                    level -= 1
                else:
                    # We found the opposite brace for the origional brace
                    newpos = pos - 1 - char[0] if close else pos + 1 + char[0]
                    position = (newpos, pos) if close else (pos, newpos)
                    if not highlight:
                        return position
                    cursor = self.textCursor()
                    cursor.setPosition(position[0])
                    cursor.setPosition(position[1] + 1, cursor.KeepAnchor)
                    self.setTextCursor(cursor)
                    if select:
                        self.selectedBraces = True
                    return 1
            elif char[1] == brace:
                # If there is another identical brace, increment level
                level += 1
        return
    
    def lineAreaPaintEvent(self, event):
        # Draw gutter area
        painter = QtGui.QPainter(self.lineArea)
        painter.fillRect(event.rect(), QtGui.QColor('#C4C4C4'))

        # Match editor font
        painter.setFont(self.font())

        # Calculate geometry
        firstBlock = self.firstVisibleBlock()
        blockNumber = firstBlock.blockNumber()
        top = self.blockBoundingGeometry(firstBlock).\
              translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(firstBlock).height()

        # Draw line numbers
        block = firstBlock
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                num = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(3, top, self.lineArea.width(), \
                                 self.fontMetrics().height(), \
                                 QtCore.Qt.AlignLeft, num)

            # Increment
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber = blockNumber + 1
    
    def lineAreaWidth(self):
        # Return a line number width of 4 chars
        if self.enableLineNumbers:
            fm = self.fontMetrics()
            return 4 + fm.width('9') * 4
        else:
            return 0
    
    def replace(self):
        states = {
            'caseSensitive': self.replace_caseSensitive,
            'wholeWord': self.replace_wholeWord,
            'backward': self.replace_backward,
            'replace_text': self.replace_text,
            'replace_with': self.replace_with,
        }
        find, replace, states, successful = ReplaceDialog(states).exec_()
        if not successful:
            return
        self.replace_caseSensitive = states['caseSensitive']
        self.replace_wholeWord = states['wholeWord']
        self.replace_backward = states['backward']
        self.replace_text = states['replace_text']
        self.replace_with = states['replace_with']
        if successful:
            do_replace = False
            while True:
                found = self.find(find, None, True, states)
                if found is True:
                    do_replace = True
                    self.insertPlainText(replace)
                if not found or not states['replaceAll']:
                    break
            text = self.toPlainText()
            if not states['replaceAll'] and do_replace and find in text:
                self.replace()
    
    def resizeEvent(self, event):
        # Resize line area as well
        super(Editor, self).resizeEvent(event)
        rect = self.contentsRect()
        self.lineArea.setGeometry(QtCore.QRect(rect.left(), rect.top(), \
                                        self.lineAreaWidth(), rect.height()))
    
    def setFocus(self, isTemplate=False):
        super(Editor, self).setFocus()
        if isTemplate:
            self.inTemplate = True
            self.isInTemplate()
    
    def setModified(self, modified):
        return self.document().setModified(modified)
    
    def show_parens(self, yes):
        text = self.textCursor().selectedText()
        if yes and not self.hadSelection and not text == u'\u2029':
            self.hadSelection = True
            if len(text) == 1 and text in '([{}])':
                pos = self.textCursor().selectionStart()
                self.matchBraces(text, pos, True if text in '}])' else False)
        elif yes:
            self.hadSelection = False
    
    def updateLineArea(self, rect, dy):
        # Respond to a scroll event
        if dy:
            self.lineArea.scroll(0, dy)
        else:
            self.lineArea.update(0, rect.y(), \
                                self.lineArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineAreaWidth()
    
    def updateLineAreaWidth(self):
        self.setViewportMargins(self.lineAreaWidth(), 0, 0, 0)
    
    def updateStatusBar(self):
        message = 'Ln: %s' % (self.textCursor().blockNumber() + 1)
        message += ' '
        message += 'Col: %s' % self.textCursor().positionInBlock()
        parent = self.statusBar.parentWidget()
        if self.statusBar.widget:
            self.statusBar.removeWidget(self.statusBar.widget)
        self.statusBar.addPermanentWidget(QtGui.QLabel(message))
