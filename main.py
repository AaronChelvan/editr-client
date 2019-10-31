import sys
import textEditor
import serverMenu
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt


class ServerMenu(QtWidgets.QWidget):
    connectSuccessful = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Main Window')

        layout = QtWidgets.QGridLayout()

        self.line_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.line_edit)

        self.button = QtWidgets.QPushButton('Switch Window')
        self.button.clicked.connect(self.viewTextbox)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def viewTextbox(self):
        self.connectSuccessful.emit(self.line_edit.text())


class FileMenu(QtWidgets.QWidget):

    def __init__(self):
        # TODO
        pass
        


class TextEditor(QtWidgets.QWidget):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Login')

        layout = QtWidgets.QGridLayout()

        self.button = QtWidgets.QPushButton('Login')
        self.button.clicked.connect(self.login)

        layout.addWidget(self.button)

        self.setLayout(layout)

    def login(self):
        self.switch_window.emit()


class Controller:

    def __init__(self):
        pass

    def show_server_menu(self): # The menu where we select a server
        #if self.window != None:
        #    self.window.close()
        self.window = serverMenu.serverMenu()
        self.window.connectSuccessful.connect(self.show_text)
        self.window.show()

    '''
    def show_file_menu(self): # The menu where we select a file
        self.window.close()
        self.window = MainWindow()
        self.window.switch_window.connect(self.show_window_two)
        self.window.show()
    '''

    def show_text(self): # The textbox
        self.window.close()
        self.window = textEditor.MainWindow(None)
        self.window.stopEditing.connect(self.show_server_menu)
        self.window.show()

# The colour scheme
def palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    return palette

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Editr")
    app.setPalette(palette())
    controller = Controller()
    controller.show_server_menu()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
