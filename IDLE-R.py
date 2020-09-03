#!/usr/bin/env python3
#
#  IDLE-R.py
#
import sys, os, subprocess, re, time
from PySide2 import QtCore, QtGui, QtWidgets
from datetime import date

# Import all parts of the IDE
from src.editor import Editor
from src.tabBar import TabBar
from src.extended import QAction, StatusBar, MenuBar


def open_file(*args):
    filename = args[0].replace('/', os.path.sep) # For other OSes
    return open(filename, *args[1:])


def make_settings():
    """
    Makes the default settings folders and files for IDLE-R
    """
    # Base folder
    home = os.path.expanduser('~') + os.path.sep
    if not os.path.isdir(home + '.idle-r'):
        os.mkdir(home + '.idle-r')

    # Workspaces folder for workspace saving
    if not os.path.isdir(home + '.idle-r/workspaces'):
        os.mkdir(home + '.idle-r/workspaces')

    # Templates folder for workspace saving
    if not os.path.isdir(home + '.idle-r/templates'):
        os.mkdir(home + '.idle-r/templates')

    # Recent files file
    if not os.path.isfile(home + '.idle-r/recent_files'):
        with open_file(home + '.idle-r/recent_files', 'w') as rfile: pass


class AboutIDLE_R(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.Dialog)
        self.setWindowTitle("About IDLE-R")
        self.setMaximumSize(QtCore.QSize(0, 0))

        vbox = QtWidgets.QVBoxLayout(self)

        #Create an icon for the Dialog
        pixmap = QtGui.QPixmap('images/icon.png')
        self.lblIcon = QtWidgets.QLabel()
        self.lblIcon.setPixmap(pixmap)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.lblIcon)

        lblTitle = QtWidgets.QLabel(
"<h1>IDLE-R</h1>\n<i>Intergrated Development Learning Environment Reimagined<i>"
)
        lblTitle.setTextFormat(QtCore.Qt.RichText)
        lblTitle.setAlignment(QtCore.Qt.AlignLeft)
        hbox.addWidget(lblTitle)
        vbox.addLayout(hbox)
        #Add description
        vbox.addWidget(QtWidgets.QLabel("""
IDLE-R (Intergrated Development Learning Environment Reimagined), is a
clone of IDLE but with fixes to make it more user and learner friendly.
"""
))


class IDLE_R(QtWidgets.QMainWindow):

    def __init__(self):
        # Init & Tweak
        super(IDLE_R, self).__init__()
        self.setWindowTitle("IDLE_R")
        self.setMinimumSize(950, 600)
        self.alt = 0

        # Set the number for file names
        self.file_index = 1

        # Add menubar
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)

        # Add menubar actions
        self.addMenuActions()

        # Add tool
        self.tool_bar = QtWidgets.QToolBar()
        self.tool_bar.setMovable(False)
        self.tool_bar.addAction('')
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.tool_bar)

        # Add menubar actions
        self.addMenuActions()

        # Status bar
        self.statusBar = StatusBar()
        self.setStatusBar(self.statusBar)

        options = ''
        if options == 'gvim':
            if os.path.isfile('.entered'):
                os.remove('.entered')
            gvim_container = QtWidgets.QX11EmbedContainer(self)
            winId = str(gvim_container.winId())
            if sys.platform in ['win32', 'cygwin']:
                args = ['gvim.exe', '--winid', winId, '--cmd', '"source test.session"']
            else:
                args = ['gvim', '--socketid', winId, '--cmd', '"source test.session"']
            # Terminate on close of IDLE-R
            # On exit of gvim give focus back to IDLE-R
            # Don't grab vim input (shortcut keys)
            gvim_container.resize(1280, 1024)
            gvim = os.system(' '.join(args))
            while not os.path.isfile('.entered'):
                time.sleep(0.1)
            with open('.entered') as pidfile:
                data = pidfile.read()
                pid = int(data.split('\n')[0])
                wid = data.split('\n')[1]
            os.remove('.entered')
            # Work out why gvim downsizes
            time.sleep(1.5)
            self.showMaximized()
            gvim_container.setFocus()
            self.setCentralWidget(gvim_container)
        else:
            # Add tab bar
            self.tab_bar = TabBar(self)
            self.tab_bar.setMovable(True)

            # Set tabs to be closable
            self.tab_bar.tabCloseRequested.connect(self.closeTab)
            self.tab_bar.currentChanged.connect(self.editorUpdateStatusBar)
            self.tab_bar.setTabsClosable(True)

            # Change window name to the current filename
            self.tab_bar.currentChanged.connect(self.changeWindowName)

            # Set central widget
            self.setCentralWidget(self.tab_bar)

            # Start a new file
            self.newFile()

    def addMenuActions(self):
        """Adds all of the actions to the menu bar"""
        # Clear menu bar in case already called
        self.menu_bar.clear()

        ## Add the "File" menu ##
        pre = "&" if self.alt else ""
        fileMenu = self.menu_bar.addMenu(pre + "File")

        action = self.newAction("New", self.newFile, "Ctrl+N")
        fileMenu.addAction(action)

        # Add the templates menu
        menu = fileMenu.addMenu("New (with Template)")
        for template in self.getTemplates():
            if template:
                Template = QAction(template, self, self.openTemplate)
                Template.setStatusTip(self.readTemplate(template, tooltip=True))
                menu.addAction(Template)

        action = self.newAction("Open...", self.openFile, "Ctrl+O")
        fileMenu.addAction(action)

        # Separator
        fileMenu.addSeparator()

        action = self.newAction("Save", self.saveFile, "Ctrl+S")
        fileMenu.addAction(action)
        action = self.newAction("Save As...", self.saveAs, "Ctrl+Shift+S")
        fileMenu.addAction(action)

        # Separator
        fileMenu.addSeparator()

        # Recent files menu
        menu = fileMenu.addMenu("Recent Files")

        # Add recent files
        for recentFile in self.readRecentFile():
            if recentFile:
                RecentFile = QAction(recentFile, self, self.openRecentFile)
                menu.addAction(RecentFile)

        # Separator
        fileMenu.addSeparator()

        # Workspace actions
        action = self.newAction("Save Workspace", self.saveWorkspace)
        fileMenu.addAction(action)

        # Open Workspace menu
        menu = fileMenu.addMenu("Open Workspace")

        # Add workspaces
        for workspace in self.getWorkspaces():
            Workspace = QAction(workspace, self, self.openWorkspace)
            menu.addAction(Workspace)

        # Delete Workspace menu
        menu = fileMenu.addMenu("Delete Workspace")

        # Add workspaces
        for workspace in self.getWorkspaces():
            Workspace = QAction(workspace, self, self.deleteWorkspace)
            menu.addAction(Workspace)

        # Separator
        fileMenu.addSeparator()

        # Closing and quiting
        action = self.newAction("Close", self.closeTab, "Ctrl+W")
        fileMenu.addAction(action)
        action = self.newAction("Close All", self.closeTabs, "Ctrl+Shift+W")
        fileMenu.addAction(action)
        action = self.newAction("Quit", self.close, "Ctrl+Q")
        fileMenu.addAction(action)

        ## Add the "Edit" menu ##
        editMenu = self.menu_bar.addMenu(pre + "Edit")
        action = self.newAction("Undo", self.undo, "Ctrl+Z")
        editMenu.addAction(action)
        action = self.newAction("Redo", self.redo, "Ctrl+Shift+Z")
        editMenu.addAction(action)

        editMenu.addSeparator()

        # Edit actions
        action = self.newAction("Cut", self.cut, "Ctrl+X")
        editMenu.addAction(action)
        action = self.newAction("Copy", self.copy, "Ctrl+C")
        editMenu.addAction(action)
        action = self.newAction("Paste Backwards", self.paste_reverse, "Ctrl+Alt+V")
        editMenu.addAction(action) # (< and ^) Pastes words backwards
        action = self.newAction("Paste - Terminal", self.paste, "Ctrl+Shift+V")
        editMenu.addAction(action) # (< and ^) For unix user copying terminal
        action = self.newAction("Paste", self.paste, "Ctrl+V")
        editMenu.addAction(action)
        action = self.newAction("Select All", self.selectAll, "Ctrl+A")
        editMenu.addAction(action)

        editMenu.addSeparator()

        # Edit actions continued
        action = self.newAction("Find...", self.find, "Ctrl+F")
        editMenu.addAction(action)
        action = self.newAction("Find Again", self.findAgain, "Ctrl+G")
        editMenu.addAction(action)
        #action = self.newAction("Find Again Backwards", self.findAgainBW, "Shift+G")
        #editMenu.addAction(action)
        action = self.newAction("Replace...", self.replace, "Ctrl+H")
        editMenu.addAction(action)
        action = self.newAction("Go to Line", self.goto_line, "Alt+G")
        editMenu.addAction(action)
        action = self.newAction("Show Completions", self.showCompletions, "Ctrl+Space")
        editMenu.addAction(action)

        editMenu.addSeparator()
        #action = self.newAction("Use GVim", self.gvim, "Ctrl+Alt+G")
        #editMenu.addAction(action)

        #action = self.newAction("Preferences", self.preferences, "Ctrl+Alt+P")
        #editMenu.addAction(action)

        ## Add the "Format" menu ##
        formatMenu = self.menu_bar.addMenu("F{}ormat".format(pre))
        action = self.newAction("Indent Region", self.indent_region, 'Ctrl+]')
        formatMenu.addAction(action)
        action = self.newAction("Dedent Region", self.dedent_region, 'Ctrl+[')
        formatMenu.addAction(action)
        action = self.newAction("Comment Out Region", self.comment_out_region, 'Alt+3')
        formatMenu.addAction(action)
        action = self.newAction("Uncomment Region", self.uncomment_region, 'Alt+4')
        formatMenu.addAction(action)
        action = self.newAction("Tabify Region", self.tabify_region, 'Alt+5')
        formatMenu.addAction(action)
        action = self.newAction("Untabify Region", self.untabify_region, 'Alt+6')
        formatMenu.addAction(action)

        formatMenu.addSeparator()

        # More format actions
        action = self.newAction("Strip trailing whitespace", self.strip_wspace)
        formatMenu.addAction(action)

        ## Add the "Debug" menu ##
        debugMenu = self.menu_bar.addMenu(pre + "Debug")
        action = self.newAction("Debugger", self.start_debugger)
        debugMenu.addAction(action)
        action = self.newAction("Stack Viewer", self.stack_viewer)
        debugMenu.addAction(action)
        action = self.newAction("Auto-open Stack Viewer", self.auto_stack_view)
        debugMenu.addAction(action)

        ## Add the "Help" menu ##
        helpMenu = self.menu_bar.addMenu(pre + "Help")
        action = self.newAction("About IDLE-R", self.about)
        helpMenu.addAction(action)
        action = self.newAction("About Qt", self.about_qt)
        helpMenu.addAction(action)

    def about(self):
        AboutIDLE_R(self).show()

    def about_qt(self):
        QtWidgets.QMessageBox.aboutQt(self, 'About Qt')

    def auto_stack_view(self):
        pass

    def changeWindowName(self):
        editor = self.tab_bar.currentWidget()
        try:
            # Set window name based on file name
            name = os.path.basename(editor.filename)
            title = 'IDLE-R: ' + name + ' - ' + editor.filename
            if editor.isModified():
                title = '* ' + title + ' *'
            self.setWindowTitle(title)
            editor = self.tab_bar.currentWidget()
        except AttributeError:
            pass

    def closeEvent(self, event):
        edited = False
        for tab in range(self.tab_bar.count()):
            if self.tab_bar.widget(tab).isModified():
                edited = True
                break

        if edited:
            msgBox = QtWidgets.QMessageBox(self)

            # Set pos
            msgBox = self.setMsgBoxPos(msgBox)

            # Info
            msgBox.setText("Some documents have been modified.")
            msgBox.setInformativeText(
                "Do you want to discard the changes?"
            )
            msgBox.setIcon(msgBox.Warning)

            # Buttons
            msgBox.setStandardButtons(msgBox.Cancel | msgBox.Discard)
            msgBox.setDefaultButton(msgBox.Cancel)

            # Run
            ret = msgBox.exec_()

            if ret == msgBox.Discard:
                self.close()
            else:
                event.ignore()
        else:
            self.close()

    def closeTab(self, index=-1):
        if index == -1:
            index = self.tab_bar.currentIndex()
        self.tab_bar.closeTab(index, self.saveFile, self.setMsgBoxPos, self)

    def closeTabs(self):
        for index in range(self.tab_bar.count(), -1, -1):
            self.closeTab(index)

    def comment_out_region(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.comment_out_region()

    def copy(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.copy()

    def cut(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.cut()

    def dedent_region(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.dedent_region()

    def deleteWorkspace(self, action):
        home = os.path.expanduser('~') + os.path.sep
        name = action
        message = "Are you sure you want to delete the workspace " + name + "?"
        delete = QtWidgets.QMessageBox.question(
                self, 'Delete Workspace', message,
                QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Yes)
        if delete == QtWidgets.QMessageBox.Yes:
            os.remove(home + '.idle-r/workspaces/' + name)
            self.addMenuActions()

    def editorUpdateStatusBar(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.updateStatusBar()

    def event(self, event):
        if event.type() == QtCore.QEvent.Type.WindowDeactivate:
            self.setAlt()
        return super(IDLE_R, self).event(event)

    def find(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.find()

    def findAgain(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.find(editor.find_text)

    def getTemplates(self):
        home = os.path.expanduser('~') + os.path.sep
        cwd = os.path.dirname(os.path.realpath(__file__)) + '/'
        templates = []
        for template in os.listdir(home + '.idle-r/templates'):
            if not template[0] == '.':  # Not a hidden file
                templates.append(home + '.idle-r/templates/' + template)
        if os.path.isdir(cwd + 'templates'):
            for template in os.listdir(cwd + 'templates'):
                if not template[0] == '.':  # Not a hidden file
                    templates.append(cwd + 'templates/' + template)
        return templates

    def getWorkspaces(self):
        home = os.path.expanduser('~') + os.path.sep
        workspaces = []
        for workspace in os.listdir(home + '.idle-r/workspaces'):
            workspaces.append(workspace)
        return workspaces

    def goto_line(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.goto_line()

    def indent_region(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.indent_region()

    def keyPressEvent(self, event):
        if event.key() == 16777251:
            self.setAlt(self.alt ^ 1)
        super(IDLE_R, self).keyPressEvent(event)

    def newAction(self, name, action, shortcut=None, icon=None):
        """Make actions quickly"""
        if icon:
            Action = QtWidgets.QAction(QtWidgets.QIcon(icon), name, self)
        else:
            Action = QtWidgets.QAction(name, self)
        Action.triggered.connect(action)
        if shortcut:
            Action.setShortcut(shortcut)
        return Action

    def newFile(self, filename=0, ow=0, text=0, cpos=0, template=0):
        """Make a new file"""
        if not filename:
            filename = "untitled{}.py".format(self.file_index)
            self.file_index += 1

        # Make editor and configure
        editor = Editor(self.statusBar)
        editor.filename = filename
        editor.isUntitled = True  # Makes untitled files distinguishable

        # Change tab text and window title to show file has been edited
        editor.textChanged.connect(self.unsaved)
        editor.textChanged.connect(self.changeWindowName)

        # Add given text if any
        if text:
            if not template:
                editor.isUntitled = False
            editor.setPlainText(text)

            # Set cursor pos
            if cpos:
                cursor = QtWidgets.QTextCursor
                textCursor = editor.textCursor()
                textCursor.movePosition(cursor.Right, n=cpos)
                editor.setTextCursor(textCursor)

        # Add the tab
        if ow:
            # Overwrite current tab if it is untitled and not modified
            index = self.tab_bar.currentIndex()
            self.tab_bar.removeTab(index)
        tab = self.tab_bar.addTab(editor, os.path.basename(filename))
        self.tab_bar.setCurrentIndex(tab)

        # Set focus to the editor
        editor.setFocus(True if template else False)

    def newShortcut(self, action, shortcut):
        """A function so I can make keyboard shortcuts"""
        Action = QtWidgets.QAction(self)
        Action.setShortcut(shortcut)
        Action.triggered.connect(action)
        return Action

    def openFile(self, filenames=False):
        """Open a new file"""
        # Ask user for file
        if not filenames:
            filenames = QtWidgets.QFileDialog.getOpenFileNames(
                self, 'Open File', os.curdir,
                "Python files (*.py *.pyw *.py3);; All files (*)"
            )[0]
            if not filenames:  # Filenames was blank ('')
                return

        # Make filenames a list if it is not a list
        if not isinstance(filenames, list):
            filenames = [filenames]

        # Iterate through filenames
        for filename in filenames:
            # Rewrite recent files & Update Recent Files list
            self.writeRecentFile(filename)
            self.addMenuActions()

            # Read file and display
            text = open_file(filename, 'r').read()

            # Check which way to open file & open
            editor = self.tab_bar.currentWidget()
            if editor:
                if editor.isUntitled and not editor.document().isModified():
                    # Overwrite this tab if it is untitled and not modified
                    self.newFile(filename, True, text)
                    continue
            self.newFile(filename, False, text)

    def openRecentFile(self, rfile):
        """Open a recent file"""
        self.openFile(rfile)

    def openTemplate(self, template):
        """Load a template"""
        self.readTemplate(template)

    def openWorkspace(self, action):
        home = os.path.expanduser('~') + os.path.sep
        with open_file(home + '.idle-r/workspaces/' + action) as workspace:
            data = workspace.read().split('\n')
            files = data[:-2]
            tab_index = int(data[-2])
            for f in files:
                if os.path.isfile(f):
                    self.openFile(f)
                else:
                    self.newFile(f)
            self.tab_bar.setCurrentIndex(tab_index)

    def paste(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.paste()

    def paste_reverse(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.paste_reverse()

    def readRecentFile(self):
        """Returns the recent files"""
        home = os.path.expanduser('~') + os.path.sep
        top_ten = []
        with open_file(home + '.idle-r/recent_files') as recentFiles:
            for fpath in recentFiles.read().split('\n'):
                if os.path.isfile(fpath):
                    top_ten.append(fpath)
                if len(top_ten) is 10:
                    break
            return top_ten

    def readTemplate(self, template_file, tooltip=False):
        """Work with templates"""
        with open_file(template_file) as template:
            # Initialize
            txt = template.read().split('\n')
            info = []
            text = []
            inInfo = True

            # Process the lines
            for line in txt:
                if line[:3] == '***' and inInfo:
                    inInfo = False
                elif inInfo:
                    info += [line]
                else:
                    text += [line]

            # Remove the last line if it is blank
            if not line:
                text.pop()

            # Join the text together
            info = '\n'.join(info)
            text = '\n'.join(text)

            # Return the text
            text = text.replace('<year>', str(date.today().year))
            if tooltip:
                return info
            else:
                self.newFile(text=text, template=True)

    def redo(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.redo()

    def replace(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.replace()

    def saveAs(self):
        """Save current file"""
        self.saveFile(True)

    def saveFile(self, saveAs=False):
        """Save current file"""
        editor = self.tab_bar.currentWidget()
        pos = editor.textCursor().anchor()

        # Get text
        text = editor.toPlainText()

        # Append newline to end of file
        try:
            if text[-1] != '\n': text += '\n'
        except IndexError:
            pass

        # Save file
        if editor.isUntitled or saveAs:
            # Get name for the file to save to
            fsave = QtWidgets.QFileDialog.getSaveFileName
            filename = fsave(
                self, 'Save As', os.curdir,
                "Python files (*.py *.pyw *.py3);; All files (*)"
            )[0]
            if not filename:  # Filename was blank ('')
                return False

            # Add .py if not in the filename
            if not filename[-3:] == '.py':
                filename += '.py'

            # Write to file
            with open_file(filename, 'w') as f:
                f.write(text)

            # Read file and display
            text = open_file(filename, 'r').read()
            name = os.path.split(str(filename))[-1]
            self.newFile(name, True, editor.toPlainText(), filename, pos)

        else:
            # Write to file
            filename = editor.filename
            with open_file(editor.filename, 'w') as f:
                f.write(text)

        # Add to recent files
        if not filename in self.readRecentFile():
            self.writeRecentFile(filename)
            self.addMenuActions()

        # Make isUntitled false
        editor.isUntitled = False

        # Fix editor vars
        editor.setModified(False)
        self.unsaved()

    def saveWorkspace(self):
        files = []

        # Check if we can save a workspace and get all of the files paths
        for index in range(self.tab_bar.count()):
            editor = self.tab_bar.widget(index)
            if editor.isUntitled:
                if editor.isModified():
                    message = """Cannot save workspace with"""
                    message += """\nmodified untitled documents."""
                    QtWidgets.QMessageBox.information(
                        self, 'Workspace Save Aborted!', message)
                    return
            files.append(editor.filename)

        # Get workspace name
        name, ok = QtWidgets.QInputDialog.getText(
                self, 'Save Workspace',
                'What would you like this workspace to be called?:')

        # Write workspace
        if ok:
            # Check if we are going to overwrite another workspace
            workspaces = self.getWorkspaces()
            if name in workspaces:
                message = """Are you sure you want to replace"""
                message += """\nthe pre-existing workspace:\n"""
                message += name
                dupe = QtWidgets.QMessageBox.question(
                        self, 'Duplicate Workspace', message,
                        QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Yes)
                if dupe == QtWidgets.QMessageBox.No:
                    self.saveWorkspace()
            # Save workspace
            self.writeWorkspace(str(name), files)
            self.addMenuActions()

    def selectAll(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.selectAll()

    def setAlt(self, value=0):
        if self.alt != value:
            self.alt = value
            self.addMenuActions()

    def setMsgBoxPos(self, msgBox):
        rect = msgBox.geometry()
        w = self.width() / 2
        h = self.height() / 2
        pos = QtCore.QPoint(w - 100, h + 50)
        rect.moveCenter(pos)
        msgBox.setGeometry(rect)
        return msgBox

    def showCompletions(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            # Start autocompleting if the cursor has no selection (so as to not
            # overwrite the selection)
            if not editor.textCursor().hasSelection():
                editor.autocomplete()

    def stack_viewer(self):
        pass

    def start_debugger(self):
        pass

    def strip_wspace(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.strip_whitespace()

    def tabify_region(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.tabify_region()

    def uncomment_region(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.uncomment_region()

    def undo(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.undo()

    def unsaved(self):
        """Checks if the current file is saved/unsaved"""
        editor = self.tab_bar.currentWidget()
        if editor:
            index = self.tab_bar.currentIndex()
            name = self.tab_bar.tabText(index)
            if editor.isModified():
                if not '* ' in name:
                    self.tab_bar.setTabText(index, '* ' + name)
            else:
                self.tab_bar.setTabText(index, name.replace('* ', ''))

    def untabify_region(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.untabify_region()

    def writeRecentFile(self, filename):
        """Write the recent files"""
        filename = os.path.realpath(filename)  # make path absolute
        home = os.path.expanduser('~') + os.path.sep
        # Get the old data in the "recent_files" file
        with open_file(home + '.idle-r/recent_files') as f:
            old_data = f.read().split('\n')

        # Write the new data
        with open_file(home + '.idle-r/recent_files', 'w') as f:
            f.write(filename + '\n')
            # Write old data
            count = 1
            for rfile in old_data:
                # Check if not duped or deleted
                if rfile == filename or not os.path.isfile(rfile):
                    pass
                else:
                    # Write if count not 10 because max recent files num
                    if not count >= 10:
                        f.write(rfile + '\n')
                        count += 1

    def writeWorkspace(self, name, files):
        home = os.path.expanduser('~') + os.path.sep
        with open_file(home + '.idle-r/workspaces/' + name, 'w') as workspace:
            for f in files:
                workspace.write(f + '\n')
            workspace.write(str(self.tab_bar.currentIndex()))


if __name__ == '__main__':
    # Make the default settings
    make_settings()

    # Run the IDE
    app = QtWidgets.QApplication(sys.argv)
    cwd = os.path.dirname(os.path.realpath(__file__)) + '/'
    with open(cwd + 'theme' + os.path.sep + 'style.qss') as stylesheet:
        app.setStyleSheet(stylesheet.read())
    window = IDLE_R()
    window.show()
    sys.exit(app.exec_())
