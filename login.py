from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
import sys
import client


class Login(QtWidgets.QMainWindow):

    switch_window = QtCore.pyqtSignal()

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)

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
        lineEditUser.setGeometry(150,50,215,30)

        lineEditPass = QLineEdit('', self)
        lineEditPass.setEchoMode(QLineEdit.Password)
        lineEditPass.setGeometry(150,100,215,30)
        #lineEditPass.move(150,100)

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
        #widget =
        #testButton = QPushButton('Test')
        #grid.setSpacing(10)
        #grid.addWidget(testButton,100,100)
        #widget.setLayout(grid)
        #self.setCentralWidget(widget)
        #hbox1 = QHBoxLayout()
        #hbox1.addStretch(1)
        #hbox1.addWidget(testButton)
        #hbox1.addWidget(lineEditUser)

        #vbox1 = QVBoxLayout(self)

        #vbox1.addStretch(1)
        #vbox1.addLayout(hbox1)

        #widget.setLayout(hbox1)

        #hbox2 = QHBoxLayout()
        #hbox2.addStretch(1)
        #hbox2.addWidget(label2)
        #hbox2.addWidget(lineEditPass)

        #self.setCentralWidget()

    def login(self):

        self.switch_window.emit()



class Menu(QtWidgets.QMainWindow):

    switch_window = QtCore.pyqtSignal()

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Editr')
        self.setGeometry(400,400,600,500)

        label = QLabel(self)
        label.setText("IP Address:")
        label.move(50, 50)

        label2 = QtWidgets.QLabel(self)
        label2.setText("Port:")
        label2.move(50, 100)

        labelP = QLabel(self)
        labelP.setBaseSize(2000,2000)
        pixmap = QPixmap('crab.png').scaled(50,50)
        labelP.setPixmap(pixmap)
        labelP.move(200,200)
        labelP.hasScaledContents()
        #pixmap.scaled(20050,2550)
        labelP.raise_()


        recents = QtWidgets.QLabel(self)
        recents.setText("Put recent connections here")
        recents.setGeometry(300,50,200,20)
        #recents.width(100)
        #recents.move(400,50)

        lineEditIP = QLineEdit('', self)
        lineEditIP.move(150, 50)

        lineEditPort = QLineEdit('', self)
        lineEditPort.setEchoMode(QLineEdit.Password)
        lineEditPort.move(150, 100)

        connectButton = QPushButton('Connect', self)
        connectButton.move(150, 150)
        connectButton.clicked.connect(self.text)

        self.menu(app)


    def text(self):
        print("main switch")
        self.switch_window.emit()

    def menu(self, app):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAct)

        ##Will be used to add new connections
        menubar.addMenu('&Add')

        menubar.addMenu('&Settings')

        helpmenu = menubar.addMenu('&Help')
        aboutAct = QAction('&About',self)

        feedbackAct = QAction('&Feedback', self)
        helpAct = QAction('&Help',self)

        helpmenu.addAction(aboutAct)
        helpmenu.addAction(feedbackAct)
        helpmenu.addAction(helpAct)


class Savededitr:

    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    def displayWindows(self):
        label = QLabel(self)
        label.setText(self.name)
        label.move(50, 50) ##Needs relative location

        pixmap = QPixmap('crab.png')
        label.setPixmap(pixmap)


    def windowClicked(self):
        pass


class Controller:

    def __init__(self,app):
        self.app = app
        pass

    def show_login(self):
        self.login = Login(self.app)
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self):
        self.window = Menu(self.app)
        self.window.switch_window.connect(self.show_text)
        self.login.close()
        self.window.show()

    def show_text(self):
        print("before client ")
        self.text = client.MainWindow()
        self.window.close()
        self.text.show()
        self.app.exec_()



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
    app.setApplicationName("Editr")
    pal = palette()
    app.setPalette(pal)
    controller = Controller(app)
    controller.show_login()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
