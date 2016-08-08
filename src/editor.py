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
from src.completer import CodeAnalyser
import random
import re
import os
#import call_tip_widget

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
        
        # Code analyser
        self.analyser = CodeAnalyser(self)
        self.connect(self, QtCore.SIGNAL("textChanged()"),
                    self.analyser.analyse)
        
        # Completer
        self.completer = QtGui.QCompleter(self)
        self.completer.setModel(QtGui.QDirModel(self.completer))
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitive)
        self.completer.setWidget(self)
        self.connect(self.completer, QtCore.SIGNAL("activated(const QString&)"), self.complete)
        
        # Status bar
        self.statusBar = statusBar
        
        # Syntax highlighting
        self.highlighter = PygmentsHighlighter(self)
        
        # Highlighting
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.highlight)
        self.highlight()
        
        # Update status bar
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.updateStatusBar)
        self.connect(self, QtCore.SIGNAL("selectionChanged()"),
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
        # If Ctrl+Space is pressed, open auto-complete
        # If Tab pressed and no word under cursor, pass (fix on keyPressEvent)
        # If Tab pressed and word under cursor, open auto-complete (filter by word under cursor?)
        # If double Tab (quick taps?) and word under cursor, just tab. (TWEAK!)
        
        # Make a clone of the textCursor which we can work with
        cursor = self.textCursor()
        cursor.select(cursor.LineUnderCursor)
        
        # Get the word under the cursor
        line = cursor.selectedText()
        pos = self.textCursor().positionInBlock() - 1
        
        # Make sure that the lines has text and the text at pos isn't blank
        if line and line[pos].strip():
            # Set completer model to path if in string otherwise python/other
            lineSplit = line.split(' ')
            pos = line[:pos].count(' ')
            complete = lineSplit[pos]
            
            #print '0. ', [complete]
            if complete.startswith(os.sep) or complete.endswith(os.sep): # A Path
                # If the path is not complete, keep joining it with last item(s)
                old = complete
                while not os.path.exists(complete) and pos >= 0:
                    complete = lineSplit[pos - 1] + ' ' + complete
                    pos -= 1
                    
                # Still not complete, reset
                if not os.path.exists(complete):
                    complete = old
                #print '1. ', [complete]
                
                # Get rid of useless chars
                complete = re.findall("""([^"']+)""", complete)[0]
                #print '2. ', [complete]
                
                # Use the word under the cursor to start autocompletion
                self.completer.setCompletionPrefix(complete)
            else:
                # Autocomplete for Python
                return
        else:
            # Autocomplete Python with no prefix
            return
            
        # Set the start index for completing
        popup = self.completer.popup()
        popup.setCurrentIndex(self.completer.completionModel().index(0,0))
        
        # Start completing
        rect = self.cursorRect()
        rect.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(rect)
    
    def columnLinePaintEvent(self, event):
        if self.enableColumnLine:
            # Repaint on top first
            self.update()
            
            # Draw column line area
            painter = QtGui.QPainter(self.columnLine)
            color = QtGui.QColor("#22aa33")
            color.setAlpha(80)
            painter.fillRect(event.rect(), color)
    
    def complete(self, completion):
        # Clone the cursor
        cursor = self.textCursor()
        
        # Move position and insert completion
        cursor.movePosition(cursor.Left, cursor.KeepAnchor, len(self.completer.completionPrefix()))
        if os.path.isdir(completion):
            completion += os.path.sep
        cursor.insertText(completion)
        self.setTextCursor(cursor)
    
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
    
    def highlight(self):
        objects = []
        objects += [self.highlight_current_line()]
        self.setExtraSelections(objects)
    
    def highlight_current_line(self):
        selection = QtGui.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor("#858585")
        lineColor.setAlpha(20)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        return selection
    
    def dent_region(self, dent):
        # Load required variables
        pos = self.textCursor().position()
        cursor = self.textCursor()
        
        # Start edit block
        cursor.beginEditBlock()
        
        # One-line dent
        if not cursor.hasSelection():
            # Move position and run operation
            cursor.movePosition(cursor.StartOfLine)
            
            # Apply the relevant action on the text
            if dent == 'in':
                # Add 4 spaces (equiv. to a tab)
                cursor.insertText(' ' * 4)
                add = 4
            else:
                # Strip first <= 4 spaces from block
                text = cursor.block().text()
                if not text[:4].strip():
                    dedent = 4
                else:
                    dedent = len(text) - len(text.strip())
                add = -dedent
                cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
                cursor.insertText(text[dedent:])
            
            # Reset cursor state
            cursor.setPosition(pos + add)
            
        else:  # Multi-line dent
            # Get selection positions
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            selection = cursor.selection().toPlainText()
            
            # Move to appropriate position for operation
            cursor.setPosition(start)
            
            # Iterate through all of the lines in the selection
            sub = 0
            for pos, line in enumerate(selection.split('\n')):
                if dent == 'in':
                    # Add 4 spaces to the beginning of the line
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(' ' * 4)
                    add = 4
                else:
                    # Remove 4 (or less if there aren't that many) spaces
                    text = cursor.block().text()
                    if not text[:4].strip():
                        dedent = 4
                    else:
                        dedent = len(text) - len(text.strip())
                    
                    # Set variables that are needed for resetting cursor pos
                    if pos == 0:
                        add = -dedent
                    sub += dedent
                    
                    # Move position
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)
                    
                    # Change the text
                    cursor.insertText(text[dedent:])
                
                # Move one line down if needed
                if pos != len(selection.split('\n')) - 1:
                    cursor.movePosition(cursor.Down)
            
            # Reset to original position
            length = len(selection.split('\n'))
            cursor.setPosition(start + add)
            if dent == 'in':
                cursor.setPosition(end + add * length, cursor.KeepAnchor)
            else:
                cursor.setPosition(end - sub, cursor.KeepAnchor)
            
        # End edit block
        cursor.endEditBlock()
        
        # Reset our cursor
        self.setTextCursor(cursor)
    
    def indent_region(self):
        self.dent_region('in')
    
    def dedent_region(self):
        self.dent_region('de')
    
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
        """Handle key-press events"""
        pos = self.textCursor().position()
        text = event.text()
        last = self.document().findBlock(pos).text().strip()
        
        # Show variable under cursor
        z = self.textCursor()
        z.select(z.WordUnderCursor)
        variables = self.analyser.analyse()
        #t = call_tip_widget.CallTipWidget(self)
        #if variables.get(z.selectedText()):
            #self.setToolTip(z.selectedText() + ': ' + variables[z.selectedText()])
        #t.show_tip('hello')
        
        # Controls while filling in templates
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
            txt = self.textCursor().block().text()
            dedent = 0
            if not txt.strip():
                dedent = min(posInBlock % 4 or 4, len(txt))
            elif not txt[max(posInBlock-4, 0):posInBlock].strip():
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
                        # Check if the braces are in the same line
                        findpos = self.matchBraces(char, char_pos, close)
                        contains = self.textCursor().block().contains
                        if contains(findpos[0]) + contains(findpos[1]) != 2:
                            # If not, remove the indentation
                            subtract -= 4
                char_pos += 1
            if ind_pos:
                space += ' ' * (4 * ind_pos)
                hasBrace = True
            
            if last:
                char = last[-1]
                
                if char == ':':
                    space += ' ' * 4
                    
                if not hasBrace and char == '\\':
                    # Add extra spaces if there is a \ at the end of the line
                    space += ' ' * 4
            
            # Add last line's tabs to this line (keep indentation)
            line = self.document().findBlock(pos).text()
            space += ' ' * (len(line) - len(line.strip()))

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
                    # We found the opposite brace for the original brace
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
                    return position
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
    
    def paste_reverse(self):
        cb = QtGui.QApplication.clipboard().text()
        self.insertPlainText(' '.join(cb.split(' ')[::-1]))
    
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
        lines = self.toPlainText().count('\n') + 1
        message = ''
        if self.textCursor().hasSelection():
            text = self.toPlainText()
            selection = self.textCursor().selectedText()
            message += 'Selected Text Count: ' + str(text.count(selection)) + ' '
        message += 'Ln: %s/%s' % (self.textCursor().blockNumber() + 1, lines)
        message += ' '
        message += 'Col: %s' % self.textCursor().positionInBlock()
        message += ' '
        self.statusBar.showMessage(message)
