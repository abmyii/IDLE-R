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
#from src.editor import Editor

class IDLE_R(QtGui.QMainWindow):
    
    def __init__(self):
        # Init & Tweak
        super(IDLE_R, self).__init__()
        self.setWindowTitle("IDLE_R")
        self.resize(950, 600)
        
        # Add toolbar
        self.tab_bar = QtGui.QTabWidget()
        self.tab_bar.setMovable(True)
        
        # Set tabs to be closable
        self.tab_bar.tabCloseRequested.connect(self.closetab)
        self.tab_bar.setTabsClosable(True)
        
        # Set central widget
        self.setCentralWidget(self.tab_bar)
    
    def closetab(self, tabindex):
        self.tab_bar.removeTab(tabindex)
    
if __name__ == '__main__':
    # Run the IDE
    QtGui.QApplication.setStyle("plastique")
    app = QtGui.QApplication(sys.argv)
    window = IDLE_R()
    window.show()
    sys.exit(app.exec_())
