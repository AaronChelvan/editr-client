from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QGroupBox, QDesktopWidget
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import QTimer
import sys, socket
from lib import showErrorMessage

# The menu window which contains:
# - Contains a menu for inputting an IP address and port number
# - A list of recent connections

class serverMenuWindow(QtWidgets.QMainWindow):
    connectSuccessful = QtCore.pyqtSignal(object)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setFixedSize(450,400)
        self.menu()
        self.center()

        central = QWidget()
        self.setCentralWidget(central)

        self.grid = GridLayout(central,self.emitObject)

        self.errorMessages = []
        self.errorMessages.append("Invalid Port") #0
        self.errorMessages.append("Connection Failed") #1

        label = QLabel()
        label.setText("IP Address:")
        label.setFixedSize(60,50)

        label2 = QLabel()
        label2.setText("Port:")
        label2.setFixedSize(40,50)

        self.setStyleSheet("QLabel {font: 9pt Helvetica}")
        #label.setStyleSheet()

        self.lineEditIP = QLineEdit('')
        self.lineEditIP.setFixedSize(100,50)

        self.lineEditPort = QLineEdit('')
        self.lineEditPort.setFixedSize(100,50)

        connectButton = QPushButton('Connect')
        connectButton.clicked.connect(self.connectToServer)
        connectButton.setFixedSize(120,40)

        connectionLayout = QGridLayout()
        connectionLayout.addWidget(label,0,0)
        connectionLayout.addWidget(label2,1,0)
        connectionLayout.addWidget(self.lineEditIP,0,1)
        connectionLayout.addWidget(self.lineEditPort,1,1)
        connectionLayout.addWidget(connectButton,1,2)
        connectionBox = QGroupBox()
        connectionBox.setLayout(connectionLayout)
        connectionBox.setTitle("Server Connection")

        totalLayout = QVBoxLayout()
        totalLayout.addWidget(connectionBox)
        totalLayout.addWidget(self.grid)


        central.setLayout(totalLayout)


    def center(self):
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


    def emitObject(self,object):
        self.connectSuccessful.emit(object)

    def text(self):
        print("main switch")
        self.switch_window.emit()

    def menu(self):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(exitAct)

        ##Will be used to add new connections
        menubar.addMenu('&Add')

        menubar.addMenu('&Settings')

        helpmenu = menubar.addMenu('&Help')
        aboutAct = QAction('&About', self)

        feedbackAct = QAction('&Feedback', self)
        helpAct = QAction('&Help', self)

        helpmenu.addAction(aboutAct)
        helpmenu.addAction(feedbackAct)
        helpmenu.addAction(helpAct)


    def newRecent(self, ip, port):
        check = False
        for object in self.grid.returnList():
            ipTest = object.ipAddress()
            portTest = object.portReturn()
            if str(ip) == ipTest and str(port) == portTest:
                check = True
                break
            else:
                continue

        if not check:
            self.grid.addNew(ip, port)
            with open("recents.txt", "a+") as f:
                f.write(str(ip) + ":" + str(port) + "\n")


    def connectToServer(self):
        # Get the IP address and port number
        ip = self.lineEditIP.text()
        port = self.lineEditPort.text()
        print("ip = %s, port = %s"% (ip, port))

        # Check if the port number is valid
        if not port.isdigit():
            showErrorMessage("Invalid port number")
            return
        
        # Attempt to connect to the server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((ip, int(port)))
        except socket.error:
            showErrorMessage("Failed to connect")
            return

        # Switch to the text editor window
        self.newRecent(ip, port)
        self.connectSuccessful.emit(clientSocket)

    def connectionError(self, errorNum):
        self.error = notificationWindow(self.errorMessages[errorNum])
        self.error.setFixedSize(130,70)
        self.error.show()

class notificationWindow(QWidget):
    def __init__(self,name):
        super().__init__()

        self.name = name
        self.initUI()
        self.setStyleSheet("QLabel {font: 9pt Helvetica}")

    def initUI(self):
        notwindow = QLabel(self.name,self)



class GridLayout(QtWidgets.QGroupBox):
    def __init__(self, parent,win):
        QtWidgets.QWidget.__init__(self,"Recent Connections", parent=parent)
        self.recentList = []
        self.xCur = 0
        self.xMax = 4
        self.yCur = 0
        self.yMax = 3
        self.win = win
        self.currentTask = None


        self.move(50,200)

        layout = QGridLayout()
        self.layout = layout
        self.layout.setColumnStretch(1, 1)
        self.layout.setRowStretch(2, 4)

        self.setLayout(self.layout)


        try:

            with open('recents.txt') as content_file:
                content = content_file.read()
                lines = content.splitlines()
                size = len(lines)
                #if size > 1:

                for i in range(0,size):
                    print(lines[i])
                    split = lines[i].split(":")
                    ip = split[0]
                    port = split[1]
                    new = self.addNew(ip,port)
                    self.recentList.append(new)
        except FileNotFoundError:
            pass


    def addNew(self, ip, port):
        if self.yCur < self.yMax:
            ySet = self.yCur
            self.yCur += 1
        else:
            self.yCur = 0
            self.xCur += 1
            ySet = 0

        if self.xCur < self.xMax:
            push = QPushButton(str(ip) + ":" + str(port))
            self.layout.addWidget(push, self.xCur, ySet)
            new = Savedrecent(str(ip), str(port), self.win, self.getTask, self.setTask)
            push.clicked.connect(new.schedule)
            self.recentList.append(new)

    def returnList(self):
        return self.recentList

    def setTask(self,task):
        self.currentTask = task

    def getTask(self):
        return self.currentTask



class Savedrecent:

    def __init__(self, ip, port,win, getTask, setTask):
        self.ip = ip
        self.port = port
        self.win = win
        self.getTask = getTask
        self.setTask = setTask

    def ipAddress(self):
        return self.ip

    def portReturn(self):
        return self.port

    def connectToServer(self):

        # Get the IP address and port number
        ip = self.ip
        port = self.port
        print("ip = %s, port = %s" % (ip, port))

        # Check if the port number is valid
        if not port.isdigit():
            showErrorMessage("Invalid port number")
            return

        # Attempt to connect to the server
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((ip, int(port)))
        except socket.error:
            showErrorMessage("Failed to connect")
            return
        self.win(clientSocket)

    def connectionError(self):
        self.error = notificationWindow("Connection Failed")
        self.error.setFixedSize(130,70)
        self.error.show()


    def schedule(self):
        try:
            task = self.getTask()
            task.stop()
        except AttributeError:
            # No task currently running
            pass

        timer = QtCore.QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self.connectToServer)
        timer.start(10)
        self.setTask(timer)



