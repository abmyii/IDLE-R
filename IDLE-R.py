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
import sys
from PyQt4 import Qt, QtCore, QtGui

# Import all seperate parts
from src.editor import Editor

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
        self.tab_bar = QtGui.QTabWidget()
        self.tab_bar.setMovable(True)
        
        # Set tabs to be closable
        self.tab_bar.tabCloseRequested.connect(self.closeTab)
        self.tab_bar.setTabsClosable(True)
        
        # Set central widget
        self.setCentralWidget(self.tab_bar)
        
        # Start a new file
        self.newFile()
    
    def addMenuActions(self):
        """Adds all of the actions to the menu bar"""
        # Add the "File" menu
        fileMenu = self.menu_bar.addMenu("File")
        action = self.newAction("New", self.checkUntitled, "Ctrl+N")
        fileMenu.addAction(action)
        action = self.newAction("New (with Template)", self.template)
        fileMenu.addAction(action)
    
    def closeTab(self, tabindex):
        """Called when closing tabs"""
        self.tab_bar.removeTab(tabindex)
    
    def checkUntitled(self):
        self.newFile()
    
    def newAction(self, name, action, shortcut=None):
        """A function so I can make actions"""
        Action = QtGui.QAction(name, self)
        Action.triggered.connect(action)
        if shortcut:
            Action.setShortcut(shortcut)
        return Action
        
    def newFile(self, name=None, ow=False, text=None):
        """Make a new file"""
        if name:
            name = name
        else:
            name = "untitled{}.py".format(self.file_index)
            self.file_index += 1
        
        # Make editor and configure
        editor = Editor()
        editor.textChanged.connect(self.unsaved)
        
        # Add given text if any
        if text:
            editor.setText(text)
        
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
    
    def template(self):
        """Make a new file with a template"""
        with open('templates/py.template') as template:
            self.newFile(text=template.read())
    
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

if __name__ == '__main__':
    # Run the IDE
    QtGui.QApplication.setStyle("plastique")
    app = QtGui.QApplication(sys.argv)
    window = IDLE_R()
    window.show()
    sys.exit(app.exec_())
