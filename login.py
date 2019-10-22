from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import sys


def app():
    mainApp = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(400,400,700,500)
    win.setWindowTitle("Editr")
    win.setWindowIcon(QIcon('imageTest.jpg'))
    mainApp.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53,53,53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ToolTipBase, Qt.white)
    # palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    mainApp.setPalette(palette)

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

#Will make open logged in window
def loginClick():
    print("Login")


app()
