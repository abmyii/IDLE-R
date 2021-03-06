#
#  editor.py
#
from PySide2 import QtCore, QtGui, QtWidgets
from src.highlighter import PygmentsHighlighter
from src.extended import FindDialog, ReplaceDialog, codeToolTip
from src.completer import CodeAnalyser, Completer, Autocompleter
import random
import re
import os
import ast


class LineArea(QtWidgets.QWidget):

    def __init__(self, editor):
        QtWidgets.QWidget.__init__(self, editor)
        self.editor = editor

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(self.editor.lineAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineAreaPaintEvent(event)


class ColumnLine(LineArea):

    def paintEvent(self, event):
        self.editor.columnLinePaintEvent(event)


class Editor(QtWidgets.QPlainTextEdit):
    isUntitled = False
    filename = ''
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
    # When last action was inserting a completion
    completed = False

    def __init__(self, statusBar):
        super(Editor, self).__init__()
        self.setAcceptDrops(False)

        # Set the Font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)

        # Tab & Cursor width
        self.setTabStopWidth(self.tabStopWidth() / 2)
        self.origCursorWidth = self.cursorWidth()

        # Code analyser
        self.analyser = CodeAnalyser(self)

        # Completer and auto-completer
        self.completer = Completer(self)
        self.autocompleter = Autocompleter()

        # Add the builtins module to the autocompleter
        self.autocompleter.add_module(__import__('builtins'))

        # Status bar
        self.statusBar = statusBar

        # Syntax highlighting
        self.highlighter = PygmentsHighlighter(self)

        # Add line number label to status bar and update it
        self.lineNumber = QtWidgets.QLabel()
        self.connect(self, QtCore.SIGNAL("cursorPositionChanged()"),
                    self.updateStatusBar)
        self.connect(self, QtCore.SIGNAL("selectionChanged()"),
                    self.updateStatusBar)
        self.updateStatusBar()

        # Remove frame and set line wrap mode
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

        # Draw the column line
        self.enableColumnLine = False
        if self.enableColumnLine:
            self.columnLine = ColumnLine(self)
            fm = self.fontMetrics()
            self.columnLine.setGeometry((0.5 + fm.width('0')) * 80, 0, 1, 1000)

        # Create line number widget
        self.enableLineNumbers = False
        if self.enableLineNumbers:
            self.lineArea = LineArea(self)

            # Connect relevant signals to line number widget
            self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), \
                        self.updateLineAreaWidth)
            self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'), \
                        self.updateLineArea)

            # Initialize Line number widget
            self.updateLineAreaWidth()

        # Connect other signals
        self.connect(self, QtCore.SIGNAL('copyAvailable(bool)'), \
                    self.show_parens)

        # Set cursor format
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QColor('#000000'))
        self.setCurrentCharFormat(format)

    def focusInEvent(self, *args):
        self.statusBar.addPermanentWidget(self.lineNumber)
        self.lineNumber.show()
        self.highlight()
        super(Editor, self).focusInEvent(*args)

    def focusOutEvent(self, *args):
        self.statusBar.removeWidget(self.lineNumber)
        super(Editor, self).focusOutEvent(*args)

    def autocomplete(self):
        # NOTES:
        # If Ctrl+Space is pressed, open auto-complete
        # If Tab pressed and no word under cursor, pass (fix on keyPressEvent)
        # If Tab pressed and word under cursor, open auto-complete (filter by word under cursor?)
        # If double Tab (quick taps?) and word under cursor, just tab. (TWEAK!)

        # Get the word under the cursor
        complete = self.getWordUnderCursor(True)

        # Start completion if there is a word under the cursor
        if complete:
            complete, pos = complete
            if complete.startswith(os.sep) or complete.endswith(os.sep): # A Path
                # If the path is not complete, keep joining it with last item(s)
                old = complete
                while not os.path.exists(complete) and pos > 0:
                    complete = lineSplit[pos - 1] + ' ' + complete
                    pos -= 1

                # Get rid of useless chars
                complete = complete.replace('"', '')
                complete = complete.replace("'", '')

                # Still not complete, reset
                if not os.path.exists(complete):
                    complete = old
                else:
                    self.completer.setModel(QtWidgets.QDirModel())

                # Use the word under the cursor to start autocompletion
                self.completer.setCompletionPrefix(complete)
            else:
                # Autocomplete for Python
                self.completer = Completer(self, ['testing'])
        else:
            # Autocomplete Python with no prefix
            # put list in model?
            self.completer = Completer(self, self.autocompleter['builtins'])

        # Show completer
        if self.completer.completionCount():
            self.completer.showCompleter()

    def columnLinePaintEvent(self, event):
        if self.enableColumnLine:
            # Repaint on top first
            self.update()

            # Draw column line area
            painter = QtWidgets.QPainter(self.columnLine)
            color = QtGui.QColor("#000000")
            color.setAlpha(80)
            painter.fillRect(event.rect(), color)

    def complete(self, completion, prefix):
        # Clone the cursor
        cursor = self.textCursor()

        # Move position and insert completion
        cursor.movePosition(cursor.Left, cursor.KeepAnchor, len(prefix))
        if os.path.isdir(completion):
            completion += os.path.sep
        cursor.insertText(completion)
        self.setTextCursor(cursor)
        self.completed = True

    def find(self, text='', pos=None, comp=False, states={}, replaceCursor=True):
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
            if do and states['wholeWord']:
                if not f' {txt} ' in all_text: do = 0
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

                # Move cursor
                if replaceCursor:
                    self.setTextCursor(cursor)

                # Return search result
                if cursor.hasSelection():
                    return True
                else:
                    # Otherwise try searching from the beginning of the document
                    if comp: return False
                    return self.find(text, 0, comp, states)
            elif comp: return False

    def getWordUnderCursor(self, position=False):
        cursor = self.textCursor()
        cursor.select(cursor.LineUnderCursor)

        # Get the word under the cursor
        line = cursor.selectedText()
        pos = self.textCursor().positionInBlock() - 1

        # Make sure that the lines has text and the text at pos isn't blank
        if line and line[pos].strip():
            lineSplit = line.split(' ')
            pos = line[:pos].count(' ')
            word = lineSplit[pos]
            if position:
                return word, pos
            return word

    def goto_line(self):
        line, ok = QtWidgets.QInputDialog.getInt(self, "Goto", "Go to Line number:")
        if ok:
            self.moveCursor(QtGui.QTextCursor.Start)
            for _ in range(line - 1):
                self.moveCursor(QtGui.QTextCursor.Down)

    def highlight(self):
        objects = []
        objects += [self.highlight_current_line()]
        self.setExtraSelections(objects)

        # Remove tooltips (? always)
        QtWidgets.QToolTip.hideText()

    def highlight_current_line(self):
        selection = QtWidgets.QTextEdit.ExtraSelection()
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

    def mousePressEvent(self, event):
        super(Editor, self).mousePressEvent(event)
        self.highlight()

    def keyPressEvent(self, event):
        """Handle key-press events"""
        pos = self.textCursor().position()
        text = event.text()
        last = self.document().findBlock(pos).text().strip()
        completer_isVisible = self.completer.popup().isVisible()


        # Last action was not inserting a completion
        completed = self.completed
        if self.completed:
            self.completed = False

        # Control keypresses when completer is active
        if self.completer.popup().isVisible():
            # Enter, Return, Escape, Tab, Backtab
            forbidden = [16777221, 16777220, 16777216, 16777217, 16777218]
            if not event.nativeModifiers() and event.key() in forbidden:
                if event.key() in [16777221, 16777220, 16777217]:
                    self.completer.onActivated(self.completer.currentCompletion())
                    self.completer.popup().hide()
                return
            else:
                # Hide and continue
                self.completer.popup().hide()

        # Controls while filling in templates
        if self.inTemplate:
            if text == '\t':
                self.isInTemplate()
                return
            elif text == u'\x1b':  # Key escape
                if self.textCursor().hasSelection():
                    self.textCursor().clearSelection()
                self.inTemplate = False
                return

        if self.selectedBraces:
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)

        # Move to beginning of first word whith HOME key
        if event.key() == 16777232:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.movePosition(QtGui.QTextCursor.NextWord)
            self.setTextCursor(cursor)
            return

        # Handle backspaces
        if text == '\b':
            # fix and do in one edit block
            tc = self.textCursor()
            posInBlock = tc.positionInBlock()
            txt = tc.block().text()
            dedent = 0
            if not txt.strip():
                dedent = min(posInBlock % 4 or 4, len(txt))
            elif not txt[max(posInBlock-4, 0):posInBlock].strip():
                dedent = 4
            if dedent:
                for i in range(dedent):
                    tc.deletePreviousChar()
            self.setTextCursor(tc)
            if dedent:
                return

        # Insert spaces instead of tabs
        elif text == '\t':
            if not completed:
                self.autocomplete()
            else:
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
            if line.rstrip():
                space += ' ' * (len(line) - len(line.strip()))
            else:
                for i in range(len(line)):
                    self.textCursor().deletePreviousChar()

            # Dedent if last word is one of the block-ending words
            if last in ['break', 'continue', 'pass', 'yield']:
                space = space[:-4]

            if subtract:
                space = space[:subtract]

            # Insert text and space
            super(Editor, self).keyPressEvent(event)
            self.insertPlainText(space)
            return

        # Show brace formatting
        elif text and text in '([{}])':
            super(Editor, self).keyPressEvent(event)
            if text in '([{':
                self.matchBraces(text, pos, highlight=True)
            if text in ')]}':
                self.matchBraces(text, pos, True, highlight=True)
            return

        # Allow event to continue being processed if needed
        super(Editor, self).keyPressEvent(event)

        # Analyse & highlight code
        """self.analyser.analyse()"""
        self.highlight()

        """# Show variable under cursor (do properly like in AC?)
        variables = self.analyser.variables
        variable = self.getWordUnderCursor()
        if variable and self.analyser.variables.get(variable):
            text = variable + ': ' + str(variables[variable])
            codeToolTip(self, text)
        else:
            # Eval line under cursor
            tc = self.textCursor()
            tc.select(tc.LineUnderCursor)
            selected = tc.selectedText()
            try:
                # Make sure malicious code doesn't get eval'ed
                # Whoops. It evals anything still.
                # TODO: Fix
                #codeToolTip(self, 'Eval: ' + str(eval(selected, variables)))
                ## find space after cursor and select behind, run parse and
                ## select last
                tree = ast.parse(selected)
                last = tree.body[-1]
                print tree
            except Exception, e:
                print('Eval Error: ' + str(e), selected)"""

        # No more selected braces
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
        painter = QtWidgets.QPainter(self.lineArea)
        painter.fillRect(event.rect(), QtGui.QColor('#EEEEEE'))

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
        cb = QtWidgets.QApplication.clipboard().text()
        self.insertPlainText(' '.join(cb.split(' ')[::-1]))

    def replace(self):
        states = {
            'caseSensitive': self.replace_caseSensitive,
            'wholeWord': self.replace_wholeWord,
            'backward': self.replace_backward,
            'replace_text': self.replace_text,
            'replace_with': self.replace_with,
        }

        # Run dialog
        find, replace, states, successful = ReplaceDialog(states).exec_()

        # Save dialog state
        self.replace_caseSensitive = states['caseSensitive']
        self.replace_wholeWord = states['wholeWord']
        self.replace_backward = states['backward']
        self.replace_text = states['replace_text']
        self.replace_with = states['replace_with']

        text = self.toPlainText()
        if not successful or not states['replaceAll']: # If not successful, Enter was pressed.
            # Just replace one ocurrence
            found = self.find(find, None, True, states)
            if found:
                self.insertPlainText(replace)
            # keep dialog alive
        elif successful and states['replaceAll']:
            # Use regex to replace all occurrences
            text = re.sub(
                re.escape(find), re.escape(replace), self.toPlainText(),
                re.U if self.replace_caseSensitive else re.I|re.U
            )

            # Replace old text
            self.textCursor().beginEditBlock()
            self.selectAll()
            self.insertPlainText(text)
            self.textCursor().endEditBlock()

    def resizeEvent(self, event):
        if self.enableLineNumbers:
            # Resize line area as well
            super(Editor, self).resizeEvent(event)
            rect = self.contentsRect()
            self.lineArea.setGeometry(
                QtCore.QRect(rect.left(), rect.top(),
                self.lineAreaWidth(), rect.height())
            )

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
            self.lineArea.update(0, rect.y(), self.lineArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineAreaWidth()

    def updateLineAreaWidth(self):
        self.setViewportMargins(self.lineAreaWidth(), 0, 0, 0)

    def updateStatusBar(self):
        lines = self.toPlainText().count('\n') + 1

        # Info on selection
        if self.textCursor().hasSelection():
            text = self.toPlainText()
            selection = self.textCursor().selectedText()
            info = 'Selection Duplicates Count: ' + str(text.count(selection)) + ' '
            self.statusBar.showMessage(info)
        else:
            # Clear any message that might have been shown before
            self.statusBar.clearMessage()

        # The line number and column number
        message = 'Ln: %s/%s' % (self.textCursor().blockNumber() + 1, lines)
        message += ' '
        message += 'Col: %s' % self.textCursor().positionInBlock()
        message += ' '
        self.lineNumber.setText(message)

        # Set text cursor width accordingly
        if self.textCursor().positionInBlock():
            self.setCursorWidth(self.origCursorWidth * 2)
        else:
            self.setCursorWidth(self.origCursorWidth)
