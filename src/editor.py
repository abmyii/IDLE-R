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
from highlighter import PygmentsHighlighter
from extended import FindDialog, ReplaceDialog

class LineArea(QtGui.QWidget):
    
    def __init__(self, editor):
        QtGui.QWidget.__init__(self, editor)
        self.editor = editor
    
    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(self.editor.lineAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineAreaPaintEvent(event)

class Editor(QtGui.QPlainTextEdit):
    isUntitled = False
    fname = ''
    indentation = 0
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
    
    def __init__(self, statusBar):
        super(Editor, self).__init__()
        
        # Status bar
        self.statusBar = statusBar
        
        # Highlighting current line
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.highlight_current_line)
        self.highlight_current_line()
                     
        # Update status bar
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.updateStatusBar)
        self.updateStatusBar()
        
        # Syntax highlighting
        PygmentsHighlighter(self.document())
        
        # Disable line wrapping and fix other settings
        self.enableLineNumbers = True
        self.setLineWrapMode(0)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        
        # Create line number widget
        self.lineArea = LineArea(self)
        
        # Connect relevant signals to line number widget
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), \
                    self.updateLineAreaWidth)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'), \
                    self.updateLineArea)
        
        # Connect other signals
        self.connect(self, QtCore.SIGNAL('copyAvailable(bool)'), \
                    self.setFindReplaceText)
        
        # Font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        
        # Tab & Cursor width
        self.setTabStopWidth(self.tabStopWidth() / 2)
        self.setCursorWidth(self.cursorWidth() * 2)
        
        # Initialize Line number widget
        self.updateLineAreaWidth(0)
    
    def setFindReplaceText(self, yes):
        if yes:
            data = self.textCursor().selectedText()
            self.find_text = self.replace_text = data
    
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
        if str(text):
            # Check there are occurences of the search text in the document.
            do = 0
            txt = str(text)
            alltxt = str(self.toPlainText())
            if not states['caseSensitive']:
                txt = txt.lower()
                alltxt = alltxt.lower()
            if txt in alltxt: do = 1
            if not do and states['wholeWord']:
                if ' ' + txt + ' ' in alltxt: do = 1
            if not do and comp and states['replaceAll']: states['backward'] = True
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
    
    def isModified(self):
        return self.document().isModified()
        
    def setModified(self, modified):
        return self.document().setModified(modified)
    
    def keyPressEvent(self, QKeyEvent):
        """Handle keypress events"""
        pos = self.textCursor().position()
        
        # Insert spaces instead of tabs
        if QKeyEvent.text() == '\t':
            self.insertPlainText('    ')
            return
            
        if QKeyEvent.text() == '\r':
            space = ''
            if pos >= 1:
                char = self.document().characterAt(pos - 1)
                if char == QtCore.QChar(0x3a):
                    space += '    '
            
            # Add last line's tabs to this line (keep indentaition)
            for char in self.document().findBlock(pos).text():
                if char != ' ':
                    break
                space += ' '
                    
            # Dedent if last word is pass or continue or break
            last = str(self.document().findBlock(pos).text()).strip()
            if last == 'break' or last == 'continue' or last == 'pass':
                space = space[:-4]
            
            # Insert text and space
            self.textCursor().beginEditBlock()
            self.insertPlainText('\n' + space)
            self.textCursor().endEditBlock()
            scrollBar = self.verticalScrollBar()
            scrollBar.setValue(scrollBar.value() + scrollBar.singleStep())
            return
        
        if QKeyEvent.text() == '\b':
            posInBlock = self.textCursor().positionInBlock()
            txt = self.document().findBlock(pos).text()[posInBlock-4:posInBlock]
            if txt == '    ':
                for i in range(4):
                    self.textCursor().deletePreviousChar()
                return
        super(Editor, self).keyPressEvent(QKeyEvent)
    
    def goto_line(self):
        line, ok = QtGui.QInputDialog.getInt(self, "Goto", "Go to Line number:")
        if ok:
            self.moveCursor(QtGui.QTextCursor.Start)
            for _ in range(line - 1):
                self.moveCursor(QtGui.QTextCursor.Down)
    
    def highlight_current_line(self):
        self.extraSelections = []
        
        block = self.textCursor()
        selection = QtGui.QTextEdit().ExtraSelection()
        lineColor = QtGui.QColor("#858585")
        lineColor.setAlpha(20)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)
    
    def lineAreaPaintEvent(self, event):
        # Draw gutter area
        painter = QtGui.QPainter(self.lineArea)
        painter.fillRect(event.rect(), QtGui.QColor('#949494'))

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
                num = QtCore.QString(str(blockNumber + 1))
                painter.setPen(QtCore.Qt.black)
                painter.drawText(-1, top, self.lineArea.width(), \
                                 self.fontMetrics().height(), \
                                 QtCore.Qt.AlignHCenter, num)

            # Increment
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber = blockNumber + 1
    
    def lineAreaWidth(self):
        # Return a line number width of 4 chars
        if self.enableLineNumbers:
            fm = self.fontMetrics()
            return 4 + fm.width(QtCore.QChar('9')) * 4
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
            replaced = False
            while True:
                found = self.find(find, None, True, states)
                if found is True:
                    replaced = True
                    self.insertPlainText(replace)
                if not found or not states['replaceAll']:
                    break
            if not states['replaceAll'] and replaced and str(find) in str(self.toPlainText()):
                self.replace()
    
    def resizeEvent(self, event):
        # Resize line area as well
        super(Editor, self).resizeEvent(event)
        rect = self.contentsRect()
        self.lineArea.setGeometry(QtCore.QRect(rect.left(), rect.top(), \
                                        self.lineAreaWidth(), rect.height()))
    
    def updateLineArea(self, rect, dy):
        # Respond to a scroll event
        if dy:
            self.lineArea.scroll(0, dy)
        else:
            self.lineArea.update(0, rect.y(), \
                                 self.lineArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineAreaWidth(0)
    
    def updateLineAreaWidth(self, blocks):
        self.setViewportMargins(self.lineAreaWidth(), 0, 0, 0)
    
    def updateStatusBar(self):
        message = 'Ln: %s' % (self.textCursor().blockNumber() + 1)
        message += ' '
        message += 'Col: %s' % self.textCursor().positionInBlock()
        parent = self.statusBar.parentWidget()
        if self.statusBar.widget:
            self.statusBar.removeWidget(self.statusBar.widget)
        self.statusBar.addPermanentWidget(QtGui.QLabel(message))
