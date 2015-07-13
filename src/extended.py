#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  extended.py
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

class QAction(QtGui.QAction):
    """Extend to be able to hold data in the var stored'"""
    stored = None

    def connect(self, action):
        self.action = action
        self.triggered.connect(self.doAction)

    def doAction(self):
        self.action(self)

class StatusBar(QtGui.QStatusBar):
    widget = None
    
    def addPermanentWidget(self, widget):
        self.widget = widget
        super(StatusBar, self).addPermanentWidget(widget)

class FindDialog(QtGui.QDialog):
    
    def __init__(self, states, parent=None):
        super(FindDialog, self).__init__(parent)
        self._succesful = True

        label = QtGui.QLabel("Find what:")
        self.lineEdit = QtGui.QLineEdit()
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
        extensionLayout.setMargin(0)
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
        self.close()
        self._succesful = False
    
    def exec_(self):
        super(FindDialog, self).exec_()
        checkBoxesStates = {
            'caseSensitive': self.caseSensitiveCheckBox.checkState(),
            'fromStart': self.fromStartCheckBox.checkState(),
            'wholeWord': self.wholeWordsCheckBox.checkState(),
            'backward': self.backwardCheckBox.checkState(),
        }
        return self.lineEdit.text(), checkBoxesStates, self._succesful
