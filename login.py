from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
import sys


def app():
    mainApp = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(400,400,700,500)
    win.setWindowTitle("Editr")
    win.setWindowIcon(QIcon('imageTest.jpg'))

    label = QtWidgets.QLabel(win)
    label.setText("Username:")
    label.move(50,50)

    label2 = QtWidgets.QLabel(win)
    label2.setText("Password:")
    label2.move(50,100)

    lineEditUser = QLineEdit('', win)
    lineEditUser.move(150, 50)

    lineEditPass = QLineEdit('', win)
    lineEditPass.setEchoMode(QLineEdit.Password)
    lineEditPass.move(150,100)

    loginButton = QPushButton('Login', win)
    loginButton.move(150,150)
    loginButton.clicked.connect(loginClick)

    exitButton = QPushButton('Exit', win)
    exitButton.move(265,150)
    exitButton.clicked.connect(mainApp.quit)

    exitAct = QAction(QIcon('exit.png'), '&Exit', win)
    exitAct.setShortcut('Ctrl+Q')
    exitAct.setStatusTip('Exit application')
    exitAct.triggered.connect(mainApp.quit)

    menubar = win.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(exitAct)
    win.show()
    sys.exit(mainApp.exec_())

#Will make open login window
def loginClick():
    print("Login")


app()
