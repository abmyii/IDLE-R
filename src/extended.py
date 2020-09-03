#
#  extended.py
#
from PySide2 import QtCore, QtGui, QtWidgets


class QAction(QtWidgets.QAction):

    def __init__(self, *args):
        super(QAction, self).__init__(*args[:-1])
        def doAction():
            args[-1](self.text())
        self.triggered.connect(doAction)


class StatusBar(QtWidgets.QStatusBar):
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


class FindDialog(QtWidgets.QDialog):

    def __init__(self, states, parent=None):
        super(FindDialog, self).__init__(parent)
        self._succesful = True

        label = QtWidgets.QLabel("Find what:")
        self.lineEdit = QtWidgets.QLineEdit()
        if states['find_text']:
            self.lineEdit.setText(states['find_text'])
        label.setBuddy(self.lineEdit)

        self.caseSensitiveCheckBox = QtWidgets.QCheckBox("Match case")
        if states['caseSensitive']:
            self.caseSensitiveCheckBox.setChecked(True)
        self.fromStartCheckBox = QtWidgets.QCheckBox("Search from start")
        if states['fromStart']:
            self.fromStartCheckBox.setChecked(True)

        findButton = QtWidgets.QPushButton("Find")
        findButton.setDefault(True)
        findButton.clicked.connect(self.close)
        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close_)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(findButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(closeButton, QtWidgets.QDialogButtonBox.ActionRole)

        extension = QtWidgets.QWidget()

        self.wholeWordsCheckBox = QtWidgets.QCheckBox("Whole words")
        if states['wholeWord']:
            self.wholeWordsCheckBox.setChecked(True)
        self.backwardCheckBox = QtWidgets.QCheckBox("Search backward")
        if states['backward']:
            self.backwardCheckBox.setChecked(True)

        extensionLayout = QtWidgets.QVBoxLayout()
        extensionLayout.addWidget(self.wholeWordsCheckBox)
        extensionLayout.addWidget(self.backwardCheckBox)
        extension.setLayout(extensionLayout)

        topLeftLayout = QtWidgets.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.lineEdit)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addWidget(self.caseSensitiveCheckBox)
        leftLayout.addWidget(self.fromStartCheckBox)
        leftLayout.addStretch(1)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
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


class ReplaceDialog(QtWidgets.QDialog):

    def __init__(self, states, parent=None):
        super(ReplaceDialog, self).__init__(parent)
        self._succesful = True
        self.buttonPressed = ''

        label = QtWidgets.QLabel("Find:")
        self.find = QtWidgets.QLineEdit()
        if states['replace_text']:
            self.find.setText(states['replace_text'])
        label.setBuddy(self.find)

        label_rep = QtWidgets.QLabel("Replace With:")
        self.replace = QtWidgets.QLineEdit()
        if states['replace_with']:
            self.replace.setText(states['replace_with'])
        label.setBuddy(self.replace)

        self.caseSensitiveCheckBox = QtWidgets.QCheckBox("Match case")
        if states['caseSensitive']:
            self.caseSensitiveCheckBox.setChecked(True)

        replaceButton = QtWidgets.QPushButton("Replace")
        replaceButton.setDefault(True)
        replaceButton.clicked.connect(self.close)
        replaceAllButton = QtWidgets.QPushButton("Replace All")
        replaceAllButton.clicked.connect(self.close)
        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close_)

        buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        buttonBox.addButton(replaceButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(replaceAllButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.addButton(closeButton, QtWidgets.QDialogButtonBox.ActionRole)
        buttonBox.clicked.connect(self.setPressed)

        extension = QtWidgets.QWidget()

        self.wholeWordsCheckBox = QtWidgets.QCheckBox("Whole words")
        if states['wholeWord']:
            self.wholeWordsCheckBox.setChecked(True)
        self.backwardCheckBox = QtWidgets.QCheckBox("Search backward")
        if states['backward']:
            self.backwardCheckBox.setChecked(True)

        topLeftLayout = QtWidgets.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.find)
        topLeftLayout.addWidget(label_rep)
        topLeftLayout.addWidget(self.replace)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addWidget(self.caseSensitiveCheckBox)
        leftLayout.addWidget(self.wholeWordsCheckBox)
        leftLayout.addWidget(self.backwardCheckBox)
        leftLayout.addStretch(1)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
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


class MenuBar(QtWidgets.QMenuBar):

    def focusOutEvent(self, event):
        self.parent().setAlt()
        super(MenuBar, self).focusOutEvent(event)


def codeToolTip(widget, text):
    # Fix for different font sizes
    # Make sure tooltip doesn't close at the wrong times
    rect = widget.cursorRect()
    winpos = QtWidgets.QApplication.activeWindow().pos()
    x = winpos.x()+45+(rect.width()*rect.x()/2)
    y = winpos.y()+100+(rect.height()*rect.y()/16)
    pos = QtCore.QPoint(x, y)
    QtWidgets.QToolTip.showText(pos, text, widget, rect)
