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
from PyQt4 import Qt, QtCore, QtGui
from datetime import date

# Import all seperate parts of the IDE
from src.editor import Editor
from src.tabBar import TabWidget
from src.extended import QAction

class IDLE_R(QtGui.QMainWindow):
    
    def __init__(self):
        # Init & Tweak
        super(IDLE_R, self).__init__()
        self.setWindowTitle("IDLE_R")
        self.resize(950, 600)
        
        # Set the number for file names
        self.file_index = 1
        
        # Add menubar
        self.menu_bar = QtGui.QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # Add menubar actions
        self.addMenuActions()
        
        # Add toolbar
        self.tab_bar = TabWidget()
        self.tab_bar.setMovable(True)
        
        # Set tabs to be closable
        self.tab_bar.tabCloseRequested.connect(self.tab_bar.closeTab)
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
        
        action = self.newAction("Close", self.closeFile, "Ctrl+W")
        fileMenu.addAction(action)
    
    def closeFile(self):
        editor = self.tab_bar.currentWidget()
        if editor and editor.isModified():
            self.saveFile()
        self.tab_bar.removeTab(self.tab_bar.currentIndex())
    
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
        editor = Editor()
        editor.isUntitled = True  # Makes untitled files distinguishable
        editor.textChanged.connect(self.unsaved)
        
        # Add given text if any
        if text:
            editor.isUntitled = False
            editor.fname = fname
            editor.setText(text)
            
            # Set cursor pos
            for i in range(cpos):
                editor.moveCursor(19, 0)
        
        # Add the tab
        if ow:
            index = self.tab_bar.currentIndex()
            self.tab_bar.removeTab(index)
        tab = self.tab_bar.addTab(editor, name)
        self.tab_bar.setCurrentIndex(tab)
        
        # Set focus to editor
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
            fopen = QtGui.QFileDialog.getOpenFileName
            filename = fopen(
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
                return
            
            # Add .py if not in the filename
            if not filename[-3:] == '.py':
                filename += '.py'
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(editor.toPlainText())
            
            # Read file and display
            text = open(filename, 'r').read()
            name = os.path.split(str(filename))[-1]
            self.newFile(name, True, text, filename, pos)
            
        else:
            # Write to file
            filename = editor.fname
            with open(editor.fname, 'w') as f:
                f.write(editor.toPlainText())
        
        # Add to recent files
        if not filename in self.readRecentFile():
            self.writeRecentFile(filename)
            self.addMenuActions()
        
        # Make isUntitled false
        editor.isUntitled = False
        
        # Fix editor vars
        #editor.textCursor().setPosition(pos)
        editor.setModified(False)
        self.unsaved()
    
    def template(self):
        """Make a new file with a template"""
        with open('templates/py.template') as template:
            txt = template.read()
            txt = txt.replace('<year>', str(date.today().year))
            self.newFile(text=txt)
    
    def unsaved(self):
        """Checks if the current file is saved/unsaved"""
        editor = self.tab_bar.currentWidget()
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

if __name__ == '__main__':
    # Run the IDE
    QtGui.QApplication.setStyle("plastique")
    app = QtGui.QApplication(sys.argv)
    window = IDLE_R()
    window.show()
    sys.exit(app.exec_())
