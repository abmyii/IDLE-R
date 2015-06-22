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
    """Extend to be able to hold data as var 'stored'"""
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
