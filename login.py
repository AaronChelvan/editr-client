from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
import sys

##need to change to layout stuff
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

    label = QLabel(win)
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

    grid = QGridLayout(win)
    grid.setSpacing(10)
    grid.addWidget(label,5,5)
    win.setLayout(grid)
    #hbox1 = QHBoxLayout()
    #hbox1.addStretch(500)
    #hbox1.addWidget(label)
    #hbox1.addWidget(lineEditUser)

    #vbox1 = QVBoxLayout()
    #vbox1.addStretch(1)
    #vbox1.addLayout(hbox1)

    #win.setLayout(vbox1)

    #hbox2 = QHBoxLayout()
    #hbox2.addStretch(1)
    #hbox2.addWidget(label2)
    #hbox2.addWidget(lineEditPass)


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
    #mainApp = QApplication(sys.argv)
    extra = QMainWindow()
    extra.setGeometry(400,400,700,500)
    extra.show()
    print("Login")


if __name__ == '__main__':
    app()
