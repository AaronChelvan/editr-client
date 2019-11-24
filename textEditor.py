from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, socket, sys, threading, time

listenerThread = None

# TODO: Refactor this into a class
fontName = 'Lucida Console'
fontSize = 14

BUFFER_SIZE = 4096 * 10

# The text editor window
class textEditorWindow(QMainWindow):

	updateOpen = pyqtSignal(str)
	removeOpen = pyqtSignal(object)
	sigConnectionCreated = pyqtSignal(str,int)

	# Constructor
	def __init__(self):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.textBoxList = []
		self.openFiles = []

		self.connFileMap = {}
		self.names = []
		self.onlineIndex = 1


		self.fileList = []
		self.tabsNextIndex = 2

		self.tabs = QTabWidget()

		self.tabs.resize(300,200)
		self.tabs.setTabsClosable(True)
		self.addPlusTab()
		self.layout = QVBoxLayout(self)
		self.tabs.tabBar().setTabsClosable(True)
		self.tabs.tabBar().tabCloseRequested.connect(self.closeRequestedTab)

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

		self.docklayout = QVBoxLayout()
		self.docklayout.addStretch(1)
		self.docklayout.insertWidget(0,onlineBox)
		self.dockedWidget.setLayout(self.docklayout)
		self.docked.hide()
	# 	self.configureMenubarAndToolbar()

	# # TODO: Refactor constructor, it's way too long :(
	# def configureMenubarAndToolbar(self):
	# 	mainMenu = self.menuBar()

	# 	toolbar = QToolBar('Toolbar', self)
	# 	self.addToolBar(toolbar)

	# 	fileMenu = mainMenu.addMenu('&File')
	# 	editMenu = mainMenu.addMenu('&Edit')

	# 	# =========== Actions =========== #
	# 	# === File === #
	# 	saveAct = QAction('&Save and close', self)
	# 	saveAct.setStatusTip('Save the current file andstopEditingFunction close the editor.')
	# 	# saveAct.triggered.connect(self.stopEditingFunction)
	# 	fileMenu.addAction(saveAct)

	# 	# === Edit === #
	# 	cutAct = QAction('&Cut', self)
	# 	cutAct.setStatusTip('Cut the current selection')
	# 	cutAct.triggered.connect(self.textbox.cut)
	# 	editMenu.addAction(cutAct)

	# 	copyAct = QAction('&Copy', self)
	# 	copyAct.setStatusTip('Copy the current selection')
	# 	copyAct.triggered.connect(self.textbox.copy)
	# 	editMenu.addAction(copyAct)

	# 	pasteAct = QAction('&Paste', self)
	# 	pasteAct.setStatusTip('Paste the current selection')
	# 	pasteAct.triggered.connect(self.textbox.paste)
	# 	editMenu.addAction(pasteAct)

	# 	editMenu.addSeparator()

	# 	undoAct = QAction('&Undo', self)
	# 	undoAct.setStatusTip('Undo the current selection')
	# 	undoAct.triggered.connect(self.textbox.undo)
	# 	editMenu.addAction(undoAct)

	# 	redoAct = QAction('&Redo', self)
	# 	redoAct.setStatusTip('Redo the current selection')
	# 	redoAct.triggered.connect(self.textbox.redo)
	# 	editMenu.addAction(redoAct)

	# 	editMenu.addSeparator()

	# 	findAct = QAction('&Find', self)
	# 	editMenu.addAction(findAct)

	# 	replaceAct = QAction('&Replace', self)
	# 	editMenu.addAction(replaceAct)

	# 	# Toolbar things #
	# 	fontFamilySelect = QFontComboBox(toolbar)
	# 	fontFamilySelect.setCurrentFont(QFont(fontName, fontSize))
	# 	fontFamilySelect.setWritingSystem(QFontDatabase.WritingSystem.Any)
	# 	# Monospaced fonts only
	# 	fontFamilySelect.setFontFilters(QFontComboBox.MonospacedFonts)
	# 	fontFamilySelect.currentFontChanged.connect(self.updateFontFamily)

	# 	self.fontSizes = ['8','9','10','11','12','14','16','18','20','22','24','26','28','36','48','72']
	# 	fontSizeSelect = QComboBox(toolbar)
	# 	fontSizeSelect.setSizeAdjustPolicy(QComboBox.AdjustToContents)
	# 	fontSizeSelect.move(150,0)
	# 	fontSizeSelect.addItems(self.fontSizes)
	# 	fontSizeSelect.setCurrentIndex(6)
	# 	# TODO: Fix the manual text input (it breaks when it is editable and certain control keys are pressed)
	# 	# fontSizeSelect.setEditable(True)
	# 	# fontSizeSelect.setValidator(QIntValidator(1,1638))
	# 	fontSizeSelect.currentIndexChanged.connect(self.updateFontSizeIndex)
	# 	# fontSizeSelect.currentTextChanged.connect(self.updateFontSizeText)

	def closeRequestedTab(self, index):
		childrenList = self.tabs.widget(index).children()
		textBox = QWidget()
		for name in childrenList:
			if name.metaObject().className() == "Textbox":
				textBox = name
		textBox.stopEditingFunction(index)


	def updateFontFamily(self, qfont):
		global fontName
		fontName = qfont.family()
		self.textbox.setFont(QFont(fontName, fontSize))

	def updateFontSizeIndex(self, qsize):
		global fontSize
		fontSize = int(self.fontSizes[qsize])
		self.textbox.setFont(QFont(fontName, fontSize))

	# def updateFontSizeText(self, newText):
	#   global fontSize
	# 	fontSize = int(newText)
	# 	self.textbox.setFont(QFont(fontName, fontSize))
	##END

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
		# self.tabs.tabBar().tabCloseRequested.connect(text.stopEditingFunction)
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
		self.tabsNextIndex += -1

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
			open = self.openFiles
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
		open = self.openFiles
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
	# Constructor
	stopEditing = pyqtSignal(int, object)
	def __init__(self, clientSocket,fileName, index):
		super(Textbox, self).__init__()
		self.clientSocket = clientSocket # Save the socket

		self.fileName = fileName
		# Read the file contents and display it in the textbox
		fileContentsBytes = []
		readLength = 100
		i = 0
		while True:
			response = sendMessage(self.clientSocket, True, "read", 0 + i*readLength, readLength)
			fileContentsPart = response["ReadResp"]["Ok"]
			fileContentsBytes += fileContentsPart
			if len(fileContentsPart) < readLength: # If we have reached the end of the file
				break
			i += 1
		byteOrder = b"\xff\xfe" # UTF-16 byte order
		fileContents = (byteOrder + bytearray(fileContentsBytes)).decode("utf-16")

		# Create a text document object
		self.textDocument = QTextDocument()
		self.textDocument.setPlainText(fileContents)
		self.textDocument.setDefaultFont(QFont(fontName, fontSize)) # Set the font
		self.setDocument(self.textDocument)

		# Do not accept rich text
		self.setAcceptRichText(False)

		# Start detecting edits made to the textbox contents
		self.textDocument.contentsChange.connect(self.contentsChangeHandler)

		# Make the socket non-blocking
		self.clientSocket.setblocking(False)

		# Start the listener thread
		global listenerThread
		listenerThread = ListenerThread(self.clientSocket)
		listenerThread.updateTextbox.connect(self.updateTextboxHandler)
		listenerThread.start()

	# This functions executes everytime the contents of the textbox changes
	def contentsChangeHandler(self, charPosition, charsRemoved, charsAdded):
		print("charPosition = %d, charsRemoved = %d, charsAdded = %d" % (charPosition, charsRemoved, charsAdded))
		
		# Encode as UTF-16
		encodedStringUtf16 = list(self.toPlainText().encode("utf-16"))[2:] # [2:] removes the byte order bytes
		
		# charPosition, charsRemoved, and charsAdded all need to be multiplied by 2 since
		# each char is represented by 2 bytes
		if charsRemoved > 0:
			sendMessage(self.clientSocket, False, "remove", charPosition*2, charsRemoved*2)
		if charsAdded > 0:
			bytesToAdd = encodedStringUtf16[charPosition*2: charPosition*2 + charsAdded*2]
			sendMessage(self.clientSocket, False, "write", charPosition*2, bytesToAdd)

	# This function gets triggered when the listener thread receives an update from the server
	def updateTextboxHandler(self, update):
		self.textDocument.blockSignals(True)
		byteOrderSize = 2
		if "Add" in update["UpdateMessage"]:
			offset = update["UpdateMessage"]["Add"]["offset"]
			dataToAdd = bytearray(update["UpdateMessage"]["Add"]["data"])
			encodedText = self.toPlainText().encode("utf-16")
			newText = encodedText[:offset+byteOrderSize] + dataToAdd + encodedText[offset+byteOrderSize:]
		elif "Remove" in update["UpdateMessage"]:
			offset = update["UpdateMessage"]["Remove"]["offset"]
			lenToRemove = update["UpdateMessage"]["Remove"]["len"]
			encodedText = self.toPlainText().encode("utf-16")
			newText = encodedText[:offset+byteOrderSize] + encodedText[offset+byteOrderSize+lenToRemove:]
		self.textDocument.setPlainText(newText.decode("utf-16"))
		self.textDocument.blockSignals(False)

	def stopEditingFunction(self,index):
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
		self.stopEditing.emit(index, self)

		self.onlineBox.hide()

	def getFileName(self):
		return self.fileName

# This thread constantly checks for updates from the server
class ListenerThread(QThread):
	updateTextbox = pyqtSignal(object)

	def __init__(self, clientSocket):
		super(ListenerThread, self).__init__()
		self.clientSocket = clientSocket

	def run(self):
		decoder = json.JSONDecoder()
		while True:
			try:
				data = self.clientSocket.recv(BUFFER_SIZE)

				# The client may have received multiple responses, so we need to split them
				count = 0
				listObjects = []
				while count < len(data.decode()):
					jsonObject = decoder.raw_decode(data.decode()[count:])
					listObjects.append(jsonObject[0])
					count += jsonObject[1]
				for o in listObjects:
					if "UpdateMessage" in o:
						self.updateTextbox.emit(o) # Signal to the textbox that we have received an update
			except socket.error:
				time.sleep(0.1)

		print("listener is stopping")



