from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import sys


class Login(QtWidgets.QMainWindow):

    switch_window = QtCore.pyqtSignal()

    def __init__(self,app):
        QtWidgets.QMainWindow.__init__(self)
        #win = QMainWindow()
        self.setGeometry(400,400,700,500)
        self.setWindowTitle("Editr")
        #self.setWindowIcon(QIcon('imageTest.jpg'))

        label = QLabel(self)
        label.setText("Username:")
        label.move(50,50)

        label2 = QtWidgets.QLabel(self)
        label2.setText("Password:")
        label2.move(50,100)

        lineEditUser = QLineEdit('', self)
        lineEditUser.move(150, 50)

        lineEditPass = QLineEdit('', self)
        lineEditPass.setEchoMode(QLineEdit.Password)
        lineEditPass.move(150,100)

        loginButton = QPushButton('Login', self)
        #self.loginButton = QtWidgets.QPushButton('Login')
        loginButton.move(150,150)
        loginButton.clicked.connect(self.login)

        exitButton = QPushButton('Exit', self)
        exitButton.move(265,150)
        exitButton.clicked.connect(app.quit)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        #grid = QGridLayout()
        #widget = QWidget()
        #widget.
        #testButton = QPushButton('Test')
        #grid.setSpacing(10)
        #grid.addWidget(testButton,50,50)
        #self.setLayout(grid)
        #hbox1 = QHBoxLayout(self)
        #hbox1.addStretch(1)
        #hbox1.addWidget(testButton)
        #hbox1.addWidget(lineEditUser)

        #vbox1 = QVBoxLayout(self)

        #vbox1.addStretch(1)
        #vbox1.addLayout(hbox1)

        #self.setLayout(hbox1)

        #hbox2 = QHBoxLayout()
        #hbox2.addStretch(1)
        #hbox2.addWidget(label2)
        #hbox2.addWidget(lineEditPass)

    def login(self):

        self.switch_window.emit()



class MainWindow(QtWidgets.QMainWindow):

    switch_window = QtCore.pyqtSignal(str)

    def __init__(self,app):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Testing')

        layout = QtWidgets.QGridLayout()

        self.line_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.line_edit)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)


class Controller:

    def __init__(self,app):
        self.app = app
        pass

    def show_login(self):
        self.login = Login(self.app)
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self):
        self.window = MainWindow(self.app)
        self.login.close()
        self.window.show()



def palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ToolTipBase, Qt.white)
    # palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    return palette


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = palette()
    app.setPalette(pal)
    controller = Controller(app)
    controller.show_login()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
