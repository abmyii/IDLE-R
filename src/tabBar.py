#
#  tabbar.py
#
from PySide import QtCore, QtGui


class TabBar(QtGui.QTabWidget):

    def __init__(self, parent):
        super(TabBar, self).__init__(parent)

        # Add a + button for adding new tabs
        button = QtGui.QPushButton(QtGui.QIcon("images/plus.png"), '')
        button.setFlat(True)
        button.pressed.connect(parent.newFile)
        self.setCornerWidget(button)

        # Customise look
        tB = QtGui.QTabBar
        self.tabBar().setShape(tB.RoundedNorth)

    def closeTab(self, index, saveFile, setMsgBoxPos, mainwindow):
        """Called when closing tabs"""
        editor = self.currentWidget()
        if editor:
            if not editor.document().isModified():
                self.removeTab(index)
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
                    self.removeTab(index)

    def mousePressEvent(self, event):
        """
        Fix bug where MMB (Middle Mouse Button)
        inserts text into current widget.
        """
        if event.button().__int__() is 4:  # MMB
            parent = self.parent()
            point = event.globalPos() - parent.pos() - self.pos()
            # Include statusbar size when finding position
            point -= QtCore.QPoint(0, parent.statusBar.size().height())
            if self.tabBar().tabAt(point) != -1:
                self.closeTab(self.tabBar().tabAt(point),
                        parent.saveFile, parent.setMsgBoxPos, parent)
        super(TabBar, self).mousePressEvent(event)
