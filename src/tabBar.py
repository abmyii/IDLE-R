#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tabbar.py
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

class TabBar(QtGui.QTabWidget):
    
    def __init__(self, parent):
        super(TabBar, self).__init__(parent)
        
        # Draw the plus button
        button = QtGui.QPushButton(QtGui.QIcon("images/plus.png"), '')
        button.setFlat(True)
        button.pressed.connect(parent.newFile)
        self.setCornerWidget(button)
    
    def closeTab(self, index, saveFile, setMsgBoxPos, mainwindow):
        """Called when closing tabs"""
        old_index = self.currentIndex()
        self.setCurrentIndex(index)
        editor = self.currentWidget()
        if editor:
            if not editor.document().isModified():
                self.removeTab(index)
                old_index -= 1
            else:
                msgBox = QtGui.QMessageBox(mainwindow)
                
                # Set pos
                msgBox = setMsgBoxPos(msgBox)
            
                # Info
                msgBox.setText("The document has been modified.")
                msgBox.setInformativeText(
                    "Do you want to save your changes?"
                )
                msgBox.setIcon(msgBox.Warning)
                
                # Buttons
                buttons = msgBox.Cancel | msgBox.Discard | msgBox.Save
                msgBox.setStandardButtons(buttons)
                msgBox.setDefaultButton(msgBox.Save)
                
                # Run
                ret = msgBox.exec_()
                
                # Process return code
                if ret == msgBox.Discard or ret == msgBox.Save and saveFile():
                    self.removeTab(self.currentIndex())
                    
            self.setCurrentIndex(old_index)
    
    def mousePressEvent(self, QMouseEvent):
        """
        Fix bug where MMB (Middle Mouse Button)
        inserts text into current widget.
        """
        event = QMouseEvent
        if event.button().__int__() is 4:  # MMB
            point = event.globalPos() - self.parentWidget().pos()
            point -= QtCore.QPoint(0, 55)  # Space between win & tab bar
            parent = self.parent()  # Shorter variable name
            self.closeTab(self.tabBar().tabAt(point),
                        parent.saveFile, parent.setMsgBoxPos, parent)
        else:
            super(TabBar, self).mousePressEvent(event)
