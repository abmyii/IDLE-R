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
    
    def __init__(self, parent=None):
        super(FindDialog, self).__init__(parent)

        label = QtGui.QLabel("Find what:")
        self.lineEdit = QtGui.QLineEdit()
        label.setBuddy(self.lineEdit)

        caseCheckBox = QtGui.QCheckBox("Match case")
        fromStartCheckBox = QtGui.QCheckBox("Search from start")
        fromStartCheckBox.setChecked(True)

        findButton = QtGui.QPushButton("Find")
        findButton.setDefault(True)
        findButton.clicked.connect(self.close)

        moreButton = QtGui.QPushButton("More")
        moreButton.setCheckable(True)
        moreButton.setAutoDefault(False)

        buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(findButton, QtGui.QDialogButtonBox.ActionRole)
        buttonBox.addButton(moreButton, QtGui.QDialogButtonBox.ActionRole)

        extension = QtGui.QWidget()

        wholeWordsCheckBox = QtGui.QCheckBox("Whole words")
        backwardCheckBox = QtGui.QCheckBox("Search backward")
        searchSelectionCheckBox = QtGui.QCheckBox("Search selection")

        moreButton.toggled.connect(extension.setVisible)

        extensionLayout = QtGui.QVBoxLayout()
        extensionLayout.setMargin(0)
        extensionLayout.addWidget(wholeWordsCheckBox)
        extensionLayout.addWidget(backwardCheckBox)
        extensionLayout.addWidget(searchSelectionCheckBox)
        extension.setLayout(extensionLayout)

        topLeftLayout = QtGui.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.lineEdit)

        leftLayout = QtGui.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addWidget(caseCheckBox)
        leftLayout.addWidget(fromStartCheckBox)
        leftLayout.addStretch(1)

        mainLayout = QtGui.QGridLayout()
        mainLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        mainLayout.addLayout(leftLayout, 0, 0)
        mainLayout.addWidget(buttonBox, 0, 1)
        mainLayout.addWidget(extension, 1, 0, 1, 2)
        self.setLayout(mainLayout)
    
    def exec_(self):
        super(FindDialog, self).exec_()
        return self.lineEdit.text()
