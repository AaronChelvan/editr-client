from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, difflib, socket, sys, threading, time

listenerThread = None

# The text editor window
class textEditorWindow(QMainWindow):

	updateOpen = pyqtSignal(str)
	removeOpen = pyqtSignal(object)
	sigConnectionCreated = pyqtSignal(str,int)

	# Constructor
	def __init__(self, clientSocket, fileName, openFiles, curList, port):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.textBoxList = []
		self.openFiles = openFiles

		self.connFileMap = {}
		self.port = port
		self.ip = clientSocket.getsockname()[0]
		self.names = []
		self.onlineIndex = 1

		clientSocket = self.createSocket(fileName, False)
		if clientSocket is None:
			self.close()

		self.text = Textbox(clientSocket, fileName, 0)
		self.text.stopEditing.connect(self.removeTab)
		self.textBoxList.append(self.text)
		self.fileName = fileName

		self.fileList = curList
		self.plusPosition = 1
		self.tabsNextIndex = 2

		self.tabs = QTabWidget()
		self.tab1 = QWidget()

		self.tabs.resize(300,200)

		self.tabs.addTab(self.tab1, fileName)
		self.addPlusTab()
		self.layout = QVBoxLayout(self)
		self.tab1.layout = QVBoxLayout(self)

		self.tab1.layout.addWidget(self.text)
		self.tab1.setLayout(self.tab1.layout)

		self.setCentralWidget(self.tabs)

		self.menu()

		self.names.append("David")
		self.names.append("Aaron")
		self.names.append("Ben")
		self.names.append("Tony")
		self.names.append("Samuel")

		self.docked = QDockWidget("Online Users", self)
		self.addDockWidget(Qt.LeftDockWidgetArea, self.docked)
		self.dockedWidget = QWidget(self)
		self.docked.setWidget(self.dockedWidget)

		fileusers = QGridLayout()
		i = 0
		y = 0
		for x in self.names:
			label = QLabel(x)
			fileusers.addWidget(label, i, y)
			i += 1
			if i == 2:
				y+=1
				i = 0

		onlineBox = QGroupBox()
		onlineBox.setMaximumHeight(120)
		onlineBox.setLayout(fileusers)
		onlineBox.setTitle(fileName)

		self.text.onlineBox = onlineBox

		self.docklayout = QVBoxLayout()
		self.docklayout.addStretch(1)
		#self.docklayout.addWidget(onlineBox)
		self.docklayout.insertWidget(0,onlineBox)
		self.dockedWidget.setLayout(self.docklayout)
		self.docked.hide()



	def createNewTab(self):
		if len(self.qlwFileSelect.selectedItems()) == 0:
			return
		if len(self.qlwConnSelect.selectedItems()) == 0:
			return
		ip, port = self.qlwConnSelect.currentItem().text().split(':')
		fileName = self.qlwFileSelect.currentItem().text()

		clientSocket = self.createSocketNew(ip, port, fileName)
		if clientSocket is None:
			return
		
		tab = QWidget()
		text = Textbox(clientSocket, fileName, self.tabsNextIndex)
		self.tabsNextIndex += 1
		
		text.stopEditing.connect(self.removeTab)
		self.tabs.addTab(tab, ip+":"+port+" "+fileName)
		tab.layout = QVBoxLayout(self)
		self.tabs.tabBar().moveTab(self.tabsNextIndex - 2, self.tabsNextIndex-1)
		tab.layout.addWidget(text)
		tab.setLayout(tab.layout)
		self.textBoxList.append(text)
		self.updateOpen.emit(fileName)

		fileusers = QGridLayout()
		##Temporary

		i = 0
		y = 0
		for x in self.names:
			label = QLabel(x)
			fileusers.addWidget(label, i, y)
			i += 1
			if i == 2:
				y += 1
				i = 0


		onlineBox = QGroupBox()
		onlineBox.setMaximumHeight(120)
		onlineBox.setLayout(fileusers)
		onlineBox.setTitle(fileName)

		text.onlineBox = onlineBox

		#self.docklayout.addWidget(onlineBox)
		self.docklayout.insertWidget(self.onlineIndex, onlineBox)
		self.onlineIndex += 1


	def addPlusTab(self):
		tabNew = QWidget()
		self.tabs.addTab(tabNew, "+")
		lytTab = QVBoxLayout(self)
		# Connection Selection
		lytConnection = QHBoxLayout(self)
		self.qlwConnSelect = QListWidget(tabNew)
		self.qlwConnSelect.setFixedSize(300,150)
		self.qlwConnSelect.itemSelectionChanged.connect(self.refreshFileList)
		# Add/Remove Connection buttons
		self.btnAddConnection = QPushButton("+")
		self.btnAddConnection.setFixedSize(25,25)
		self.btnAddConnection.clicked.connect(self.addConnection)
		self.btnRemoveConnection = QPushButton("-")
		self.btnRemoveConnection.setFixedSize(25,25)
		lytAddRemoveConn = QVBoxLayout(self)
		lytAddRemoveConn.addWidget(self.btnAddConnection)
		lytAddRemoveConn.addWidget(self.btnRemoveConnection)
		# Host/Port Inputs
		self.lblHost = QLabel("Host", self)
		self.lneHost = QLineEdit(parent=self)
		self.lneHost.placeholderText = 'Hostname'
		self.lblPort = QLabel("Port", self)
		self.lnePort = QLineEdit(parent=self)
		self.lnePort.placeholderText = 'Port'
		lytHostPort = QVBoxLayout(self)
		lytHostPort.addWidget(self.lblHost)
		lytHostPort.addWidget(self.lneHost)
		lytHostPort.addWidget(self.lblPort)
		lytHostPort.addWidget(self.lnePort)
		# Setting up Layout
		lytConnection.addWidget(self.qlwConnSelect)
		lytConnection.addLayout(lytAddRemoveConn)
		lytConnection.addStretch(1)
		lytConnection.addLayout(lytHostPort)
		lytConnection.addStretch(1)
		# File Selection
		self.qlwFileSelect = QListWidget(tabNew)
		self.qlwFileSelect.setFixedSize(300,150)
		# Connection Button
		self.btnConnect = QPushButton("Open File")
		self.btnConnect.setFixedSize(150,50)
		self.btnConnect.clicked.connect(self.createNewTab)
		lytTab.addLayout(lytConnection)
		lytTab.addWidget(self.qlwFileSelect)
		lytTab.addWidget(self.btnConnect)
		tabNew.setLayout(lytTab)

	def addConnection(self):
		host = self.lneHost.text()
		port = self.lnePort.text()
		# print("host = %s, port = %s"% (host, port))
		# Check if the port number is valid
		if not port.isdigit():
			showErrorMessage("Invalid port number")
			return
		# Attempt to connect to the server
		self.lneHost.setText('')
		self.lnePort.setText('')
		combinedName = host + ":" + port
		# If this is already an existing connection
		if combinedName in self.connFileMap:
			return

		self.refreshFileList(ip=host, port=port)
		# If the refreshFileList operation failed
		if combinedName not in self.connFileMap:
			return

		qliNewConn = QListWidgetItem()
		qliNewConn.setText(combinedName)
		self.qlwConnSelect.addItem(qliNewConn)
		self.qlwConnSelect.setCurrentItem(qliNewConn)

	
	# Called when a new connection is selected
	def refreshFileList(self, ip="", port=""):
		if ip=="" and port=="":
			if len(self.qlwConnSelect.selectedItems()) == 0:
				return
			ip, port = self.qlwConnSelect.currentItem().text().split(':')

		combinedName = ip + ":" + port
		# If this is the first refresh
		if (combinedName not in self.connFileMap):
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				clientSocket.connect((ip, int(port)))
			except socket.error:
				showErrorMessage("Failed to connect")
				return
			response = sendMessage(clientSocket, True, "getFiles")
			if "Err" in response["FilesListResp"]:
				self.showErrorMessage(response["FilesListResp"]["Err"])
				return
			self.connFileMap[combinedName] = sorted(response["FilesListResp"]["Ok"])
		self.qlwFileSelect.clear()
		for file in self.connFileMap[combinedName]:
			self.qlwFileSelect.addItem(file)
	
	def removeTab(self, index, text):
		self.tabs.removeTab(index)
		self.textBoxList.remove(text)
		list = []
		list.append(text)
		self.removeOpen.emit(list)
		for object in self.textBoxList:
			if object.index > index:
				object.index += -1
		self.tabsNextIndex += -1
		self.plusPosition += -1

	def setFileList(self, fileList):
		self.fileList = fileList

	def closeEvent(self, event: QCloseEvent):
		print("Window {} closed".format(self))
		self.removeOpen.emit(self.textBoxList)
		for object in self.textBoxList:
			sendMessage(object.clientSocket, False, "close")
		super().closeEvent(event)


	def createSocket(self, fileName, bool):
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientSocket.connect((self.ip, self.port))
		except socket.error:
			showErrorMessage("Failed to connect")
			return None
		if not bool:
			open = self.openFiles()
			if fileName in open:
				showErrorMessage("File is already open!")
			else:
				response = sendMessage(clientSocket, True, "open", fileName)
				if "Err" in response["OpenResp"]:
					showErrorMessage(response["OpenResp"]["Err"])
					return None
				else:
					return clientSocket
	
	def createSocketNew(self, ip, port, fileName):
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientSocket.connect((ip, int(port)))
		except socket.error:
			showErrorMessage("Failed to connect")
			return None
		open = self.openFiles()
		if fileName in open:
			showErrorMessage("File is already open!")
		else:
			response = sendMessage(clientSocket, True, "open", fileName)
			if "Err" in response["OpenResp"]:
				showErrorMessage(response["OpenResp"]["Err"])
				return None
			else:
				return clientSocket

	def menu(self):
		exitAct = QAction(QIcon('exit.png'), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)

		self.menubar = self.menuBar()
		filemenu = self.menubar.addMenu('&File')
		filemenu.addAction(exitAct)

		##Will be used to add new connections
		users = self.menubar.addMenu('&Users')

		userAction = QAction('View Online Users', self, checkable=True)
		userAction.setChecked(False)
		userAction.triggered.connect(self.toggleOnline)

		users.addAction(userAction)


		#self.menubar.addMenu('&Settings')

		#helpmenu = self.menubar.addMenu('&Help')
		#aboutAct = QAction('&About', self)

		#feedbackAct = QAction('&Feedback', self)
		#helpAct = QAction('&Help', self)

		#helpmenu.addAction(aboutAct)
		#helpmenu.addAction(feedbackAct)
		#helpmenu.addAction(helpAct)

	def toggleOnline(self, state):
		if state:
			self.docked.show()

		if not state:
			self.docked.hide()

	#Does nothing for the second,will need to make this so I can update the online list
	#Either remake the layout or just remove the labels, but that would need the grid to be rearranged
	def updateOnline(self, textbox):
		fileusers = QGridLayout()
		i = 0
		y = 0
		for x in self.names:
			label = QLabel(x)
			fileusers.addWidget(label, i, y)
			i += 1
			if i == 2:
				y += 1
				i = 0
		textbox.onlineBox.setLayout(fileusers)

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# This signal gets triggered by the listener thread when an update is received from the server
	updateTextbox = pyqtSignal(str)

	# Constructor
	stopEditing = pyqtSignal(int, object)
	def __init__(self, clientSocket,fileName, index):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.clientSocket = clientSocket # Save the socket

		self.fileName = fileName
		# Read the file contents and display it in the textbox
		response = sendMessage(self.clientSocket, True, "read", 0, 999)
		fileContents = response["ReadResp"]["Ok"]
		fileContents = bytearray(fileContents).decode("utf-8")
		self.setText(fileContents)
		self.index = index

		#self.onlineWidget = None
		self.onlineBox = None

		# Start detecting edits made to the textbox contents
		self.textChanged.connect(self.textChangedHandler)
		self.prevText = self.toPlainText() # The content currently in the textbox

		closeButton = QPushButton('Save && Close')
		closeButton.setFixedSize(180, 50)
		closeButton.clicked.connect(self.stopEditingFunction)

		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(closeButton)

		vbox = QVBoxLayout()
		vbox.addStretch(1)
		vbox.addLayout(hbox)

		self.setLayout(vbox)

		# Make the socket non-blocking
		self.clientSocket.setblocking(False)

		# Start the listener thread
		global listenerThread
		listenerThread = ListenerThread(self.toPlainText(), self.clientSocket)
		listenerThread.updateTextbox.connect(self.updateTextboxHandler)
		listenerThread.start()

	# This functions executes everytime the contents of the textbox changes
	def textChangedHandler(self):
		# Use sequence matcher to find what changes were made to the textbox contents
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())

		# Iterate through the changes
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace": # If characters were overwritten
				sendMessage(self.clientSocket, False, "remove", i1, i2-i1)
				sendMessage(self.clientSocket, False, "write", i1, self.toPlainText()[j1:j2])
			elif tag == "delete": # If characters were deleted
				sendMessage(self.clientSocket, False, "remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendMessage(self.clientSocket, False, "write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()
		global listenerThread
		listenerThread.updateTextboxContents(self.toPlainText())

	# This function gets triggered when the listener thread receives an update
	def updateTextboxHandler(self, newText):
		self.blockSignals(True)
		self.setText(newText)
		self.prevText = newText
		self.blockSignals(False)

	def stopEditingFunction(self):

		# Stop the listener thread
		global listenerThread
		listenerThread.terminate()
		listenerThread.wait()
		# need to add true to messages
		# Enable socket blocking
		self.clientSocket.setblocking(True)

		# Save the changes made and close the file
		sendMessage(self.clientSocket, True, "save")
		sendMessage(self.clientSocket, False, "close")
		self.stopEditing.emit(self.index, self)

		self.onlineBox.hide()

	def getFileName(self):
		return self.fileName

# This thread constantly checks for updates from the server
class ListenerThread(QThread):
	updateTextbox = pyqtSignal(str)

	def __init__(self, textboxContents, clientSocket):
		super(ListenerThread, self).__init__()
		self.textboxContents = textboxContents
		self.clientSocket = clientSocket

	def updateTextboxContents(self, textboxContents):
		self.textboxContents = textboxContents

	def run(self):
		decoder = json.JSONDecoder()
		while True:
			try:
				data = self.clientSocket.recv(1024)

				# The client may have received multiple responses, so we need to split them
				count = 0
				listObjects = []
				while count < len(data.decode()):
					jsonObject = decoder.raw_decode(data.decode()[count:])
					listObjects.append(jsonObject[0])
					count += jsonObject[1]
				for o in listObjects:
					print("listener received: " + str(o))
					if "UpdateMessage" in o:
						prevText = self.textboxContents
						newText = ""
						if "Add" in o["UpdateMessage"]:
							offset = o["UpdateMessage"]["Add"]["offset"]
							dataToAdd = bytearray(o["UpdateMessage"]["Add"]["data"]).decode("utf-8")
							newText = prevText[:offset] + dataToAdd + prevText[offset:]
						elif "Remove" in o["UpdateMessage"]:
							offset = o["UpdateMessage"]["Remove"]["offset"]
							lenToRemove = o["UpdateMessage"]["Remove"]["len"]
							newText = prevText[:offset] + prevText[offset+lenToRemove:]
						self.updateTextbox.emit(newText) # Signal to the textbox that we have received an update
						self.textboxContents = newText # Update this thread's copy to the textbox contents
			except socket.error:
				time.sleep(0.1)

		print("listener is stopping")



