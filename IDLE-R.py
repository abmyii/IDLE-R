#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  IDLE-R.py
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
import sys, os
from PyQt4 import QtCore, QtGui
from datetime import date

# Import all parts of the IDE
from src.editor import Editor
from src.tabBar import TabWidget
from src.extended import QAction, StatusBar

def make_settings():
    """
    Makes the default settings folders and files for IDLE-R
    """
    # Base folder
    home = os.environ["HOME"]
    if not os.path.isdir(home + '/.idle-r'):
        os.mkdir(home + '/.idle-r')
    
    # Workspaces folder for workspace saving
    if not os.path.isdir(home + '/.idle-r/workspaces'):
        os.mkdir(home + '/.idle-r/workspaces')
    
    # Recent files file
    if not os.path.isfile(home + '/.idle-r/recent_files'):
        with open(home + '/.idle-r/recent_files', 'w') as rfile: pass

class IDLE_R(QtGui.QMainWindow):
    
    def __init__(self):
        # Init & Tweak
        super(IDLE_R, self).__init__()
        self.setWindowTitle("IDLE_R")
        self.setMinimumSize(950, 600)
        
        # Set the number for file names
        self.file_index = 1
        
        # Add menubar
        self.menu_bar = QtGui.QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # Add menubar actions
        self.addMenuActions()
        
        # Status bar
        self.statusBar = StatusBar()
        self.setStatusBar(self.statusBar)
        
        # Add toolbar
        self.tab_bar = TabWidget()
        self.tab_bar.setMovable(True)
        
        # Set tabs to be closable
        self.tab_bar.tabCloseRequested.connect(self.closeTab)
        self.tab_bar.currentChanged.connect(self.editorUpdateStatusBar)
        self.tab_bar.setTabsClosable(True)
        
        # Set central widget
        self.setCentralWidget(self.tab_bar)
        
        # Start a new file
        self.newFile()
    
    def addMenuActions(self):
        """Adds all of the actions to the menu bar"""
        # Clear menu bar in case already called
        self.menu_bar.clear()
        
        ## Add the "File" menu ##
        fileMenu = self.menu_bar.addMenu("File")
        action = self.newAction("New", self.newFile, "Ctrl+N")
        fileMenu.addAction(action)
        action = self.newAction("New (with Template)", self.template)
        fileMenu.addAction(action)
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
                rfile = QAction(recentFile, self)
                rfile.stored = recentFile
                rfile.connect(self.openRecentFile)
                menu.addAction(rfile)
        
        # Separator
        fileMenu.addSeparator()
        
        # Workspace actions
        action = self.newAction("Save Workspace", self.saveWorkspace)
        fileMenu.addAction(action)
        
        # Open Workspace menu
        menu = fileMenu.addMenu("Open Workspace")
        
        # Add workspaces
        for workspace in self.getWorkspaces():
            ws = QAction(workspace, self)
            ws.stored = workspace
            ws.connect(self.openWorkspace)
            menu.addAction(ws)
        
        # Delete Workspace menu
        menu = fileMenu.addMenu("Delete Workspace")
        
        # Add workspaces
        for workspace in self.getWorkspaces():
            ws = QAction(workspace, self)
            ws.stored = workspace
            ws.connect(self.deleteWorkspace)
            menu.addAction(ws)
        
        # Separator
        fileMenu.addSeparator()
        
        # Closing and quiting
        action = self.newAction("Close", self.closeTab, "Ctrl+W")
        fileMenu.addAction(action)
        action = self.newAction("Quit", self.close, "Ctrl+Q")
        fileMenu.addAction(action)
        
        ## Add the "Edit" menu ##
        editMenu = self.menu_bar.addMenu("Edit")
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
        action = self.newAction("Paste", self.paste, "Ctrl+Shift+V")
        self.addAction(action) # (< and ^) For unix user copying terminal
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
        action = self.newAction("Replace...", self.replace, "Ctrl+H")
        editMenu.addAction(action)
        action = self.newAction("Go to Line", self.goto_line, "Alt+G")
        editMenu.addAction(action)
        action = self.newAction("Show Completions", self.comps, "Ctrl+Space")
        editMenu.addAction(action)
    
    def closeEvent(self, QCloseEvent):
        edited = False
        for tab in range(self.tab_bar.count()):
            if self.tab_bar.widget(tab).isModified():
                edited = True
                break
        
        if edited:
            msgBox = QtGui.QMessageBox(self)
            
            # Set pos
            msgBox = self.setMsgBoxPos(msgBox)
    
            # Info
            msgBox.setText("Some documents have been modified.")
            msgBox.setInformativeText(
                "Do you want to save the files?"
            )
            msgBox.setIcon(msgBox.Warning)
            
            # Buttons
            msgBox.setStandardButtons(msgBox.Cancel | msgBox.Discard)
            msgBox.setDefaultButton(msgBox.Cancel)
            
            # Run
            ret = msgBox.exec_()
    
            if ret == msgBox.Discard:
                super(IDLE_R, self).close()
            else:
                QCloseEvent.ignore()
        else:
            super(IDLE_R, self).close()
    
    def closeTab(self, index):
        self.tab_bar.closeTab(index, self.saveFile, self.setMsgBoxPos, self)
    
    def comps(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.autocomplete()

    def copy(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.copy()
    
    def cut(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.cut()
    
    def deleteWorkspace(self, action):
        home = os.environ["HOME"]
        name = action.stored
        message = "Are you sure you want to delete the workspace " + name + "?"
        delete = QtGui.QMessageBox.question(
                self, 'Delete Workspace', message,
                QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
        if delete == QtGui.QMessageBox.Yes:
            os.remove(home + '/.idle-r/workspaces/' + name)
            self.addMenuActions()
    
    def editorUpdateStatusBar(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.updateStatusBar()
        
    def find(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.find()
    
    def findAgain(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.find(editor.find_text)
    
    def getWorkspaces(self):
        home = os.environ["HOME"]
        workspaces = []
        for workspace in os.listdir(home + '/.idle-r/workspaces'):
            workspaces.append(workspace)
        return workspaces
    
    def goto_line(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.goto_line()
    
    def newAction(self, name, action, shortcut=None):
        """A function so I can make actions"""
        Action = QtGui.QAction(name, self)
        Action.triggered.connect(action)
        if shortcut:
            Action.setShortcut(shortcut)
        return Action
        
    def newFile(self, name=0, ow=0, text=0, fname=0, cpos=0):
        """Make a new file"""
        if name:
            name = name
        else:
            name = "untitled{}.py".format(self.file_index)
            self.file_index += 1
        
        # Make editor and configure
        editor = Editor(self.statusBar)
        editor.fname = name
        editor.isUntitled = True  # Makes untitled files distinguishable
        editor.textChanged.connect(self.unsaved)
        
        # Add given text if any
        if text:
            editor.isUntitled = False
            editor.fname = fname
            editor.setPlainText(text)
            
            # Set cursor pos
            for i in range(cpos):
                editor.moveCursor(19, 0)
        
        # Add the tab
        if ow:
            index = self.tab_bar.currentIndex()
            self.tab_bar.removeTab(index)
        tab = self.tab_bar.addTab(editor, name)
        self.tab_bar.setCurrentIndex(tab)
        
        # Set focus to the editor
        editor.setFocus()

    def newShortcut(self, action, shortcut):
        """A function so I can make keyboard shortcuts"""
        Action = QtGui.QAction(self)
        Action.setShortcut(shortcut)
        Action.triggered.connect(action)
        return Action
    
    def openFile(self, filename=False):
        """Open a new file"""
        # Ask user for file
        if not filename:
            filename = QtGui.QFileDialog.getOpenFileName(
                self, 'Open File', os.curdir,
                "Python files (*.py *.pyw *.py3);; All files (*)"
            )
            if not filename:  # Filename was blank ('')
                return
            
        # Rewrite recent files & Update Recent Files list
        self.writeRecentFile(filename)
        self.addMenuActions()
        
        # Read file and display
        text = open(filename, 'r').read()
        name = os.path.split(str(filename))[-1]
        
        # Check which way to open file & open
        editor = self.tab_bar.currentWidget()
        if editor:
            if editor.isUntitled and not editor.document().isModified():
                self.newFile(name, True, text, filename)
                return
        self.newFile(name, False, text, filename)
    
    def openRecentFile(self, action):
        """Open a recent file"""
        self.openFile(action.stored)
    
    def openWorkspace(self, action):
        home = os.environ["HOME"]
        with open(home + '/.idle-r/workspaces/' + action.stored) as workspace:
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
    
    def readRecentFile(self):
        """Returns the recent files"""
        home = os.environ["HOME"]
        top_ten = []
        with open(home + '/.idle-r/recent_files') as recentFiles:
            for fpath in recentFiles.read().split('\n'):
                if os.path.isfile(fpath):
                    top_ten.append(fpath)
                if len(top_ten) is 10:
                    break
            return top_ten
    
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
        
        # Append newline to end of file
        try:
            last = editor.toPlainText()[-1]
        except IndexError:
            last = ''
        
        if last != '\n' and last != '':
            editor.append('')

        # Save file
        if editor.isUntitled or saveAs:
            # Get name for the file to save to
            fsave = QtGui.QFileDialog.getSaveFileName
            filename = fsave(
                self, 'Save As', os.curdir,
                "Python files (*.py *.pyw *.py3);; All files (*)"
            )
            if not filename:  # Filename was blank ('')
                return False
            
            # Add .py if not in the filename
            if not filename[-3:] == '.py':
                filename += '.py'
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(text)
            
            # Read file and display
            text = open(filename, 'r').read()
            name = os.path.split(str(filename))[-1]
            self.newFile(name, True, text, filename, pos)
            
        else:
            # Write to file
            filename = editor.fname
            with open(editor.fname, 'w') as f:
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
                    QtGui.QMessageBox.information(
                        self, 'Workspace Save Aborted!', message)
                    return
            files.append(editor.fname)
            
        # Get workspace name
        name, ok = QtGui.QInputDialog.getText(
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
                dupe = QtGui.QMessageBox.question(
                        self, 'Duplicate Workspace', message,
                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes)
                if dupe == QtGui.QMessageBox.No:
                    self.saveWorkspace()
            # Save workspace
            self.writeWorkspace(str(name), files)
            self.addMenuActions()
    
    def selectAll(self):
        editor = self.tab_bar.currentWidget()
        if editor:
            editor.selectAll()
        
    def setMsgBoxPos(self, msgBox):
        rect = msgBox.geometry()
        w = self.width() / 2
        h = self.height() / 2
        pos = QtCore.QPoint(w - 100, h + 50)
        rect.moveCenter(pos)
        msgBox.setGeometry(rect)
        return msgBox
    
    def template(self):
        """Make a new file with a template"""
        with open('templates/py.template') as template:
            txt = template.read()
            txt = txt.replace('<year>', str(date.today().year))
            self.newFile(text=txt)
    
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
    
    def writeRecentFile(self, filename):
        """Write the recent files"""
        home = os.environ["HOME"]
        # Get the old data in the "recent_files" file
        with open(home + '/.idle-r/recent_files') as f:
            old_data = f.read().split('\n')
        
        # Write the new data
        with open(home + '/.idle-r/recent_files', 'w') as f:
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
        home = os.environ["HOME"]
        with open(home + '/.idle-r/workspaces/' + name, 'w') as workspace:
            for f in files:
                workspace.write(f + '\n')
            workspace.write(str(self.tab_bar.currentIndex()))

if __name__ == '__main__':
    # Make the default settings
    make_settings()
    
    # Run the IDE
    QtGui.QApplication.setStyle("plastique")
    app = QtGui.QApplication(sys.argv)
    window = IDLE_R()
    window.show()
    sys.exit(app.exec_())
