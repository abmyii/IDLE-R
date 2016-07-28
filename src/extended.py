#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  extended.py
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
import PySide
from PySide import QtCore, QtGui
import threading

class QAction(QtGui.QAction):
    
    def __init__(self, *args):
        super(QAction, self).__init__(*args[:-1])
        def doAction():
            args[-1](self.text())
        self.triggered.connect(doAction)

class StatusBar(QtGui.QStatusBar):
    widgets = []
    
    def addWidget(self, widget):
        self.widgets.append(widget)
        super(StatusBar, self).addWidget(widget)
    
    def addPermanentWidget(self, widget):
        self.widgets.append(widget)
        super(StatusBar, self).addPermanentWidget(widget)
    
    def removeWidget(self, widget):
        self.widgets.remove(widget)
        super(StatusBar, self).removeWidget(widget)

class FindDialog(QtGui.QDialog):
    
    def __init__(self, states, parent=None):
        super(FindDialog, self).__init__(parent)
        self._succesful = True

        label = QtGui.QLabel("Find what:")
        self.lineEdit = QtGui.QLineEdit()
        if states['find_text']:
            self.lineEdit.setText(states['find_text'])
        label.setBuddy(self.lineEdit)

        self.caseSensitiveCheckBox = QtGui.QCheckBox("Match case")
        if states['caseSensitive']:
            self.caseSensitiveCheckBox.setCheckState(2)
        self.fromStartCheckBox = QtGui.QCheckBox("Search from start")
        if states['fromStart']:
            self.fromStartCheckBox.setCheckState(2)

        findButton = QtGui.QPushButton("Find")
        findButton.setDefault(True)
        findButton.clicked.connect(self.close)
        closeButton = QtGui.QPushButton("Close")
        closeButton.clicked.connect(self.close_)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(findButton, QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(closeButton, QtGui.QDialogButtonBox.ActionRole)

        extension = QtGui.QWidget()

        self.wholeWordsCheckBox = QtGui.QCheckBox("Whole words")
        if states['wholeWord']:
            self.wholeWordsCheckBox.setCheckState(2)
        self.backwardCheckBox = QtGui.QCheckBox("Search backward")
        if states['backward']:
            self.backwardCheckBox.setCheckState(2)

        extensionLayout = QtGui.QVBoxLayout()
        extensionLayout.addWidget(self.wholeWordsCheckBox)
        extensionLayout.addWidget(self.backwardCheckBox)
        extension.setLayout(extensionLayout)

        topLeftLayout = QtGui.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.lineEdit)

        leftLayout = QtGui.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addWidget(self.caseSensitiveCheckBox)
        leftLayout.addWidget(self.fromStartCheckBox)
        leftLayout.addStretch(1)

        mainLayout = QtGui.QGridLayout()
        mainLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        mainLayout.addWidget(extension, 1, 0, 1, 2)
        self.setLayout(mainLayout)
        self.setWindowTitle("Search Dialog")
    
    def close_(self):
        super(FindDialog, self).close()
        self._succesful = False
    
    def exec_(self):
        super(FindDialog, self).exec_()
        states = {
            'caseSensitive': self.caseSensitiveCheckBox.checkState(),
            'fromStart': self.fromStartCheckBox.checkState(),
            'wholeWord': self.wholeWordsCheckBox.checkState(),
            'backward': self.backwardCheckBox.checkState(),
            'find_text': self.lineEdit.text()
        }
        return self.lineEdit.text(), states, self._succesful

class ReplaceDialog(QtGui.QDialog):
    
    def __init__(self, states, parent=None):
        super(ReplaceDialog, self).__init__(parent)
        self._succesful = True
        self.buttonPressed = ''

        label = QtGui.QLabel("Find:")
        self.find = QtGui.QLineEdit()
        if states['replace_text']:
            self.find.setText(states['replace_text'])
        label.setBuddy(self.find)
        
        label_rep = QtGui.QLabel("Replace With:")
        self.replace = QtGui.QLineEdit()
        if states['replace_with']:
            self.replace.setText(states['replace_with'])
        label.setBuddy(self.replace)

        self.caseSensitiveCheckBox = QtGui.QCheckBox("Match case")
        if states['caseSensitive']:
            self.caseSensitiveCheckBox.setCheckState(2)

        replaceButton = QtGui.QPushButton("Replace")
        replaceButton.setDefault(True)
        replaceButton.clicked.connect(self.close)
        replaceAllButton = QtGui.QPushButton("Replace All")
        replaceAllButton.clicked.connect(self.close)
        closeButton = QtGui.QPushButton("Close")
        closeButton.clicked.connect(self.close_)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(replaceButton, QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(replaceAllButton, QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(closeButton, QtGui.QDialogButtonBox.ActionRole)
        buttonBox.clicked.connect(self.setPressed)

        extension = QtGui.QWidget()

        self.wholeWordsCheckBox = QtGui.QCheckBox("Whole words")
        if states['wholeWord']:
            self.wholeWordsCheckBox.setCheckState(2)
        self.backwardCheckBox = QtGui.QCheckBox("Search backward")
        if states['backward']:
            self.backwardCheckBox.setCheckState(2)

        topLeftLayout = QtGui.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.find)
        topLeftLayout.addWidget(label_rep)
        topLeftLayout.addWidget(self.replace)

        leftLayout = QtGui.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addWidget(self.caseSensitiveCheckBox)
        leftLayout.addWidget(self.wholeWordsCheckBox)
        leftLayout.addWidget(self.backwardCheckBox)
        leftLayout.addStretch(1)

        mainLayout = QtGui.QGridLayout()
        mainLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("Search Dialog")
    
    def close_(self):
        super(ReplaceDialog, self).close()
        self._succesful = False
    
    def exec_(self):
        super(ReplaceDialog, self).exec_()
        states = {
            'caseSensitive': self.caseSensitiveCheckBox.checkState(),
            'wholeWord': self.wholeWordsCheckBox.checkState(),
            'backward': self.backwardCheckBox.checkState(),
            'replace_text': self.find.text(),
            'replace_with': self.replace.text(),
            'replaceAll': False if self.buttonPressed == "Replace" else True,
        }
        return self.find.text(), self.replace.text(), states, self._succesful
    
    def setPressed(self, *args):
        if args[0]: self.buttonPressed = args[0].text()

class MenuBar(QtGui.QMenuBar):
    
    def focusOutEvent(self, event):
        self.parent().setAlt()
        super(MenuBar, self).focusOutEvent(event)
