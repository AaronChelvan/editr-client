from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox, QComboBox, QGroupBox, QMessageBox, QInputDialog
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, socket, sys, threading, time

listenerThread = None
cursorRequesterThread = None

fontName = 'Lucida Console'
fontSize = 14

BUFFER_SIZE = 4096 * 10

# The text editor window
class textEditorWindow(QMainWindow):

	updateOpen = pyqtSignal(str)
	removeOpen = pyqtSignal(object)

	# Constructor
	def __init__(self):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.textBoxList = []
		self.openFiles = []
		self.openDialog = QDialog(parent=self)
		self.openDialog.setModal(True)
		self.connFileMap = []
		self.onlineIndex = 0
		self.username = None
		self.fileList = []
		self.tabsNextIndex = 0

		self.tabs = QTabWidget()
		self.tabs.resize(300,200)
		self.tabs.setTabsClosable(True)
		self.initOpenDialog()
		self.layout = QVBoxLayout(self)
		self.tabs.tabBar().setTabsClosable(True)
		self.tabs.tabBar().tabCloseRequested.connect(self.closeRequestedTab)

		self.setCentralWidget(self.tabs)

		self.menu()
		self.setEditingMenu(False)

		self.docked = QDockWidget("Online Users", self)
		self.addDockWidget(Qt.LeftDockWidgetArea, self.docked)
		self.dockedWidget = QWidget(self)
		self.docked.setWidget(self.dockedWidget)

		self.docklayout = QVBoxLayout()
		self.docklayout.addStretch(1)
		self.dockedWidget.setLayout(self.docklayout)
		self.docked.hide()

		toolbar = QToolBar('Toolbar', self)
		self.addToolBar(toolbar)
		toolbar.setFixedHeight
		fontFamilySelect = QFontComboBox(toolbar)
		fontFamilySelect.setCurrentFont(QFont(fontName, fontSize))
		fontFamilySelect.setWritingSystem(QFontDatabase.WritingSystem.Any)
		# Monospaced fonts only
		fontFamilySelect.setFontFilters(QFontComboBox.MonospacedFonts)
		fontFamilySelect.currentFontChanged.connect(self.updateFontFamily)

		self.fontSizes = ['8','9','10','11','12','14','16','18','20','22','24','26','28','36','48','72']
		fontSizeSelect = QComboBox(toolbar)
		fontSizeSelect.setSizeAdjustPolicy(QComboBox.AdjustToContents)
		fontSizeSelect.move(150,0)
		fontSizeSelect.addItems(self.fontSizes)
		fontSizeSelect.setCurrentIndex(6)
		fontSizeSelect.currentIndexChanged.connect(self.updateFontSizeIndex)

	def closeRequestedTab(self, index):
		if index==False: # hardcoded to be from menu item
			index = self.tabs.currentIndex()
		textBox = self.getCurrentTextbox(index=index)
		textBox.stopEditingFunction(index)

	def updateFontFamily(self, qfont):
		global fontName
		fontName = qfont.family()
		if len(self.openFiles) > 0:
			self.updateFonts()
		
	def updateFontSizeIndex(self, qsize):
		global fontSize
		fontSize = int(self.fontSizes[qsize])
		if len(self.openFiles) > 0:
			self.updateFonts()

	def updateFonts(self):
		text = self.getCurrentTextbox()
		text.setFont(QFont(fontName, fontSize))

	def createNewTab(self):
		ip, port, fileName, fullName = self.readFromLists()
		print(ip + "|" + port + "|" + fileName + "|" + fullName)
		if (ip == ""):
			return
		clientSocket = self.createFileSocket(ip, port, fileName)
		if clientSocket is None:
			return
		self.setEditingMenu(True)
		newTab = QWidget()
		text = Textbox(clientSocket, fullName, self.tabsNextIndex, self.updateOnline)
		self.tabsNextIndex += 1
		text.stopEditing.connect(self.removeTab)
		self.tabs.addTab(newTab, fullName)
		newTab.layout = QVBoxLayout(self)
		self.tabs.setCurrentIndex(self.tabsNextIndex-1)
		newTab.layout.addWidget(text)
		newTab.setLayout(newTab.layout)
		self.textBoxList.append(text)
		self.openFiles.append(fullName)
		fileusers = QGridLayout()
		##Temporary
		i = 0
		y = 0
		for x in text.names:
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
		self.openDialog.hide()


	def initOpenDialog(self):
		tabNew = self.openDialog
		# tabNew = QWidget()
		# self.tabs.addTab(tabNew, "+")
		lytTab = QVBoxLayout(self)
		############################
		## Connection Layout Area ##
		############################
		lytConnection = QHBoxLayout(self)
		## Left Side: Connection List
		self.qlwConnSelect = QListWidget(tabNew)
		self.qlwConnSelect.setFixedSize(300,150)
		self.qlwConnSelect.itemSelectionChanged.connect(self.refreshFileList)
		## Middle: +/- buttons
		lytConnSettings = QVBoxLayout(self)
		btnAddConnection = QPushButton("+")
		btnAddConnection.setFixedSize(25,25)
		btnAddConnection.clicked.connect(self.addConnection)
		btnRefreshConnection = QPushButton("↻")
		btnRefreshConnection.setFixedSize(25,25)
		btnRefreshConnection.clicked.connect(self.refreshFileList)
		btnRemoveConnection = QPushButton("-")
		btnRemoveConnection.setFixedSize(25,25)
		btnRemoveConnection.clicked.connect(self.removeConnection)
		lytConnSettings.addWidget(btnAddConnection)
		lytConnSettings.addWidget(btnRefreshConnection)
		lytConnSettings.addWidget(btnRemoveConnection)
		## Right: Host/Port Inputs
		lblHost = QLabel("Host", self)
		self.lneHost = QLineEdit(parent=self)
		self.lneHost.placeholderText = 'Hostname'
		lblPort = QLabel("Port", self)
		self.lnePort = QLineEdit(parent=self)
		self.lnePort.placeholderText = 'Port'
		lytNewConn = QVBoxLayout(self)
		lytNewConn.addWidget(lblHost)
		lytNewConn.addWidget(self.lneHost)
		lytNewConn.addWidget(lblPort)
		lytNewConn.addWidget(self.lnePort)
		### Adding to Connection Layout
		lytConnection.addWidget(self.qlwConnSelect)
		lytConnection.addLayout(lytConnSettings)
		lytConnection.addStretch(1)
		lytConnection.addLayout(lytNewConn)
		lytConnection.addStretch(1)
		####################
		## File Selection ##
		####################
		lytFileList = QHBoxLayout(self)
		## Left Side
		self.qlwFileSelect = QListWidget(tabNew)
		self.qlwFileSelect.setFixedSize(300,150)
		## Middle
		lytModifyFile = QVBoxLayout(self)
		btnCreateFile = QPushButton("Create File")
		btnRenameFile = QPushButton("Rename File")
		btnDeleteFile = QPushButton("Delete File")
		btnCreateFile.setFixedSize(130,50)
		btnRenameFile.setFixedSize(130,50)
		btnDeleteFile.setFixedSize(130,50)
		btnCreateFile.clicked.connect(self.createFile)
		btnRenameFile.clicked.connect(self.renameFile)
		btnDeleteFile.clicked.connect(self.deleteFile)
		lytModifyFile.addWidget(btnCreateFile)
		lytModifyFile.addWidget(btnRenameFile)
		lytModifyFile.addWidget(btnDeleteFile)

		### Adding to File List Layout
		lytFileList.addWidget(self.qlwFileSelect)
		lytFileList.addStretch(2)
		lytFileList.addLayout(lytModifyFile)
		lytFileList.addStretch(1)
		# Connection Button
		btnConnect = QPushButton("Open File")
		btnConnect.setFixedSize(150,50)
		btnConnect.clicked.connect(self.createNewTab)
		## Final Layout Settings
		lytTab.addLayout(lytConnection)
		lytTab.addLayout(lytFileList)
		lytTab.addWidget(btnConnect)
		tabNew.setLayout(lytTab)

	def addConnection(self):
		host = self.lneHost.text()
		port = self.lnePort.text()
		# print("host = %s, port = %s"% (host, port))
		# Check if the port number is valid
		if not port.isdigit() or host == "":
			showErrorMessage("Invalid host or port")
			return
		# Attempt to connect to the server
		combinedName = host + ":" + port
		# If this is already an existing connection
		if combinedName in self.connFileMap:
			return
		if self.refreshFileList(ip=host, port=port) != True:
			return
		self.connFileMap.append(combinedName)
		self.lneHost.setText('')
		self.lnePort.setText('')
		qliNewConn = QListWidgetItem()
		qliNewConn.setText(combinedName)
		self.qlwConnSelect.addItem(qliNewConn)
		self.qlwConnSelect.setCurrentItem(qliNewConn)

	def removeConnection(self):
		if len(self.qlwConnSelect.selectedItems()) == 0:
			return
		self.connFileMap.remove(self.qlwConnSelect.currentItem().text())
		self.qlwConnSelect.takeItem(self.qlwConnSelect.currentRow())
		self.qlwFileSelect.clear()
	
	# Called when a new connection is selected
	def refreshFileList(self, ip="", port=""):
		if ip == False:
			ip = ""
		print("here1")
		if ip=="" or port=="":
			if len(self.qlwConnSelect.selectedItems()) == 0:
				return
			ip, port = self.qlwConnSelect.currentItem().text().split(':')
		combinedName = ip + ":" + port
		print("here2")
		# If this is the first refresh
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientSocket.connect((ip, int(port)))
		except socket.error:
			showErrorMessage("Failed to connect")
			return
		print("here3")
		response = sendMessage(clientSocket, True, "getFiles")
		if "Err" in response["FilesListResp"]:
			self.showErrorMessage(response["FilesListResp"]["Err"])
			return
		print("here4")
		files = sorted(response["FilesListResp"]["Ok"])
		print("we made it here!")
		self.qlwFileSelect.clear()
		for file in files:
			self.qlwFileSelect.addItem(file)
		return True

	def removeTab(self, index, text):
		self.tabs.removeTab(index)
		self.textBoxList.remove(text)
		tList = []
		tList.append(text)
		self.removeOpen.emit(tList)
		self.tabsNextIndex += -1
		self.openFiles.remove(text.fullName)
		if len(self.openFiles) == 0:
			self.setEditingMenu(False)
		for file in self.openFiles:
			print(file)

	def setEditingMenu(self, enabled):
		for child in self.fileMenu.actions():
			if child.text() == '&Save and close':
				child.setEnabled(enabled)
		for child in self.editMenu.actions():
			child.setEnabled(enabled)

	def setFileList(self, fileList):
		self.fileList = fileList

	def closeEvent(self, event: QCloseEvent):
		print("Window {} closed".format(self))
		self.removeOpen.emit(self.textBoxList)
		for object in self.textBoxList:
			sendMessage(object.clientSocket, False, "close")
		super().closeEvent(event)

	def createServerSocket(self, ip, port):
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			clientSocket.connect((ip, int(port)))
		except socket.error:
			showErrorMessage("Failed to connect")
			return None
		return clientSocket

	def createFileSocket(self, ip, port, fileName):
		clientSocket = self.createServerSocket(ip, port)
		fullName = ip + ":" + port + " " + fileName
		if fullName in self.openFiles:
			showErrorMessage("File is already open!")
		else:
			response = sendMessage(clientSocket, True, "open", fileName, self.username)
			if "Err" in response["OpenResp"]:
				showErrorMessage(response["OpenResp"]["Err"])
				return None
			else:
				return clientSocket

	def createFile(self):
		ip, port, fileName, fullName = self.readFromLists(requireFileSelection=False)
		if ip == "":
			return
		clientSocket = self.createServerSocket(ip, port)
		if clientSocket is None:
			return
		newName, okPressed = QInputDialog.getText(self, "Create file", "Enter new file name:", QLineEdit.Normal, "")
		if not okPressed:
			return
		response = sendMessage(clientSocket, True, "create", newName)
		if "Err" in response["CreateResp"]:
			showErrorMessage(response["CreateResp"]["Err"])
		else:
			self.refreshFileList()

	def renameFile(self):
		ip, port, fileName, fullName = self.readFromLists()
		if ip == "":
			return
		clientSocket = self.createServerSocket(ip, port)
		if clientSocket is None:
			return
		newName, okPressed = QInputDialog.getText(self, "Rename file", "Enter new file name:", QLineEdit.Normal, "")
		if okPressed:
			if newName != '':
				response = sendMessage(clientSocket, True, "rename", fileName, newName)
				if "Err" in response["RenameResp"]:
					showErrorMessage(response["RenameResp"]["Err"])
				else:
					newFullName = ip + ":" + port + " " + newName
					self.refreshFileList()
			else:
				showErrorMessage("File name cannot be empty")

	def deleteFile(self):
		ip, port, fileName, fullName = self.readFromLists()
		if ip == "":
			return
		clientSocket = self.createServerSocket(ip, port)
		if clientSocket is None:
			return
		if fileName in self.openFiles:
			showErrorMessage("Target file is open! Please close it first")
		else:
			response = sendMessage(clientSocket, True, "delete", fileName)
			if "Err" in response["DeleteResp"]:
				showErrorMessage(response["DeleteResp"]["Err"])
			else:
				self.refreshFileList()

	def readFromLists(self, requireFileSelection=True):
		if len(self.qlwConnSelect.selectedItems()) == 0:
			return ("","","","")
		if requireFileSelection:
			if len(self.qlwFileSelect.selectedItems()) == 0:
				return ("","","","")
		ip, port = self.qlwConnSelect.currentItem().text().split(':')
		fileName = None
		if requireFileSelection:
			fileName = self.qlwFileSelect.currentItem().text()
		else:
			fileName = ""
		fullName = ip+":"+port+" "+fileName
		if fullName in self.openFiles:
			showErrorMessage("File is open, please close it first.")
			return ("","","","")
		return (ip, port, fileName, fullName)

	def menu(self):
		menuBar = self.menuBar()
		self.fileMenu = menuBar.addMenu('&File')
		self.editMenu = menuBar.addMenu('&Edit')
		nameMenu = menuBar.addMenu('&Name')
		users = menuBar.addMenu('&Users')
		
		openAct = QAction('&Open', self)
		openAct.setShortcut('Ctrl+O')
		openAct.triggered.connect(self.showOpenDialog)
		self.fileMenu.addAction(openAct)

		saveCloseAct = QAction('&Save and close', self)
		saveCloseAct.setShortcut('Ctrl+W')
		saveCloseAct.setStatusTip('Save the current tab and close it.')
		saveCloseAct.triggered.connect(self.closeRequestedTab)
		self.fileMenu.addAction(saveCloseAct)

		exitAct = QAction(QIcon('exit.png'), '&Exit', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)
		self.fileMenu.addAction(exitAct)

	 	# === Edit === #
		cutAct = QAction('&Cut', self)
		cutAct.setStatusTip('Cut the current selection')
		cutAct.setShortcut('Ctrl+X')
		cutAct.triggered.connect(self.cutWrapper)
		self.editMenu.addAction(cutAct)

		copyAct = QAction('&Copy', self)
		copyAct.setStatusTip('Copy the current selection')
		copyAct.setShortcut('Ctrl+C')
		copyAct.triggered.connect(self.copyWrapper)
		self.editMenu.addAction(copyAct)

		pasteAct = QAction('&Paste', self)
		pasteAct.setStatusTip('Paste the current selection')
		pasteAct.setShortcut('Ctrl+V')
		pasteAct.triggered.connect(self.pasteWrapper)
		self.editMenu.addAction(pasteAct)

		self.editMenu.addSeparator()

		undoAct = QAction('&Undo', self)
		undoAct.setStatusTip('Undo the current selection')
		undoAct.setShortcut('Ctrl+Z')
		undoAct.triggered.connect(self.undoWrapper)
		self.editMenu.addAction(undoAct)

		redoAct = QAction('&Redo', self)
		redoAct.setStatusTip('Redo the current selection')
		redoAct.setShortcut('Ctrl+Y')
		redoAct.triggered.connect(self.redoWrapper)
		self.editMenu.addAction(redoAct)

		nameAction = QAction('Set Username', self)
		nameAction.triggered.connect(self.setName)
		nameMenu.addAction(nameAction)

		##Will be used to add new connections
		
		userAction = QAction('View Online Users', self, checkable=True)
		userAction.setChecked(False)
		userAction.triggered.connect(self.toggleOnline)

		users.addAction(userAction)

	def cutWrapper(self):
		text = self.getCurrentTextbox()
		text.cut()
	def copyWrapper(self):
		text = self.getCurrentTextbox()
		text.copy()
	def pasteWrapper(self):
		text = self.getCurrentTextbox()
		text.paste()
	def undoWrapper(self):
		text = self.getCurrentTextbox()
		text.undo()
	def redoWrapper(self):
		text = self.getCurrentTextbox()
		text.redo()

	def getCurrentTextbox(self, index=None):
		if index==None:
			index = self.tabs.currentIndex()
		childrenList = self.tabs.widget(index).children()
		for child in childrenList:
			if child.metaObject().className() == "Textbox":
				return child

	def showOpenDialog(self):
		self.openDialog.show()

	def setName(self):
		if len(self.openFiles) > 0:
			showErrorMessage("Cant set name when files opened")
			return

		username, okPressed = QInputDialog.getText(self, "", "Set Username", QLineEdit.Normal, "")

		if okPressed and username != "":
			self.username = username

		if okPressed and username == "":
			showErrorMessage("Name cannot be blank")

	def toggleOnline(self, state):
		if state:
			self.docked.show()

		if not state:
			self.docked.hide()

	def updateOnline(self, textbox, userlist):
		userlist.sort()
		if userlist == textbox.names:
			return
		index = self.docklayout.indexOf(textbox.onlineBox)
		textbox.onlineBox.close()

		fileusers = QGridLayout()
		i = 0
		y = 0
		count = 0
		for x in userlist:
			if x == self.username and count == 0:
				count+=1
				continue

			label = QLabel(x)
			fileusers.addWidget(label, i, y)
			i += 1
			if i == 2:
				y += 1
				i = 0

		onlineBox = QGroupBox()
		onlineBox.setMaximumHeight(120)
		onlineBox.setLayout(fileusers)
		onlineBox.setTitle(textbox.fullName)
		textbox.onlineBox = onlineBox

		self.docklayout.insertWidget(index, onlineBox)
		textbox.names = userlist

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	stopEditing = pyqtSignal(int, object)
	def __init__(self, clientSocket, fullName, index, updateOnline):
		super(Textbox, self).__init__()
		self.clientSocket = clientSocket # Save the socket
		self.fullName = fullName
		# Read the file contents and display it in the textbox
		fileContentsBytes = []
		readLength = 100
		i = 0
		self.onlineBox = None
		self.names = []
		self.updateOnline = updateOnline

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

		# Detect when the position of the cursor changes
		#self.cursorPositionChanged.connect(self.cursorPositionChangedHandler)

		# Make the socket non-blocking
		self.clientSocket.setblocking(False)

		# For sending the server the position of the cursor
		self.prevCursorPos = 0

		# Start the listener thread
		global listenerThread
		listenerThread = ListenerThread(self.clientSocket)
		listenerThread.updateTextbox.connect(self.updateTextboxHandler)
		listenerThread.updateCursors.connect(self.updateCursorsHandler)
		listenerThread.start()

		# Start the cursor requester thread
		global cursorRequesterThread
		cursorRequesterThread = CursorRequesterThread(self.clientSocket)
		cursorRequesterThread.start()

	#def cursorPositionChangedHandler(self):
	#	cursorPos = self.textCursor().position()
	#	print(cursorPos)
	#	cursorDiff = cursorPos - self.prevCursorPos
	#	self.prevCursorPos = cursorPos
	#	if cursorDiff != 0:
	#		sendMessage(self.clientSocket, False, "moveCursor", cursorDiff*2)

	#	sendMessage(self.clientSocket, False, "getCursors")
		#print(cursorPos)
		#self.unHighlightChar(self.prevCursorPos)
		#self.highlightChar(cursorPos)

		#self.unHighlightChar(cursorPos)
		#self.textDocument.blockSignals(True)
		#self.textCursor().insertText("asd")
		#self.textDocument.blockSignals(False)
		#self.setTextBackgroundColor(QColor("black"))

	def highlightChar(self, position):
		self.textDocument.blockSignals(True)
		self.blockSignals(True)
		prevPosition = self.textCursor().position()
		#print("prevPositon = ", prevPosition, " num bytes = ", len(self.toPlainText().encode("utf-16")[2:]), " position = ", position)
		cursor = self.textCursor()
		if position == len(self.toPlainText().encode("utf-16")[2:]):
			position -= 2

		cursor.setPosition(position//2)
		self.setTextCursor(cursor)
		#print("newPosition = ", self.textCursor().position(), " position = ", position)

		# Delete the existing char
		encodedText = self.toPlainText().encode("utf-16")[2:] # Ignore the byte order bytes using [2:]
		#print("encodedText = ", encodedText)
		try:
			prevChar = encodedText[position:position+2].decode("utf-16")
			self.textCursor().deleteChar()
			# Change the background colour
			self.setTextBackgroundColor(QColor("red"))
			# Put the char back
			self.textCursor().insertText(prevChar)
			# Restore the cursor and the background colour
			self.setTextBackgroundColor(QColor("black"))
			#else:
			#	self.textCursor().deleteChar()
			print("char to highlight = ", prevChar, " ", encodedText[position:position+2])
		except UnicodeDecodeError: 
			print("failed to decode char. not highlighting.")

		cursor.setPosition(prevPosition)
		self.setTextCursor(cursor)
		self.blockSignals(False)
		self.textDocument.blockSignals(False)

	def unHighlightEverything(self):
		self.textDocument.blockSignals(True)
		self.blockSignals(True)
		prevPos = self.textCursor().position()
		cursor = self.textCursor()
		self.textDocument.setPlainText(self.textDocument.toPlainText())
		cursor.setPosition(prevPos)
		self.setTextCursor(cursor)
		self.blockSignals(False)
		self.textDocument.blockSignals(False)

	def updateCursorsHandler(self, update):
		userlist = []
		self.unHighlightEverything()
		userCursorPos = update["GetCursorsResp"]["Ok"][0]
		userCursorPosFound = False
		for cursor in update["GetCursorsResp"]["Ok"][1]:
			pos = cursor[0]
			username = cursor[1]
			if (not username is None) and (not username == ""):
				userlist.append(username)
			else:
				userlist.append("Anonymous")
			print("pos = ", pos, " username = ", username)

			# Avoid rendering the current user's cursor, unless there is another user at the same position
			if pos == userCursorPos: 
				if userCursorPosFound == False:
					userCursorPosFound = True
				else:
					self.highlightChar(pos)
			else:
				self.highlightChar(pos)

		self.updateOnline(self,userlist)

	# This functions executes everytime the contents of the textbox changes
	def contentsChangeHandler(self, charPosition, charsRemoved, charsAdded):
		print("charPosition = %d, charsRemoved = %d, charsAdded = %d" % (charPosition, charsRemoved, charsAdded))
		
		# Encode as UTF-16
		encodedStringUtf16 = list(self.toPlainText().encode("utf-16"))[2:] # [2:] removes the byte order bytes
		
		# Move the cursor to charPosition
		cursorDiff = charPosition*2 - self.prevCursorPos
		print("cursorDiff = ", cursorDiff, " charPosition = ", charPosition, " self.prevCursorPos = ", self.prevCursorPos)
		self.prevCursorPos = charPosition*2
		if cursorDiff != 0:
			sendMessage(self.clientSocket, False, "moveCursor", cursorDiff)

		# charPosition, charsRemoved, and charsAdded all need to be multiplied by 2 since
		# each char is represented by 2 bytes
		if charsRemoved > 0:
			sendMessage(self.clientSocket, False, "remove", charsRemoved*2)
		if charsAdded > 0:
			bytesToAdd = encodedStringUtf16[charPosition*2: charPosition*2 + charsAdded*2]
			# TODO split up writes into multiple smaller writes less than the buffer size
			sendMessage(self.clientSocket, False, "write", bytesToAdd)

			# If chars were added, move the cursor to the right
			self.prevCursorPos += charsAdded*2

		# Request the locations of the cursors
		sendMessage(self.clientSocket, False, "getCursors")

	# This function gets triggered when the listener thread receives an update from the server
	def updateTextboxHandler(self, update):
		self.textDocument.blockSignals(True)
		print(update)
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

		# Request the new cursor positions
		sendMessage(self.clientSocket, False, "getCursors")

		
		
	def stopEditingFunction(self,index):
		# Stop the listener thread
		global listenerThread
		listenerThread.terminate()
		listenerThread.wait()

		# Stop requesting cursor positions
		global cursorRequesterThread
		cursorRequesterThread.terminate()
		cursorRequesterThread.wait()

		# need to add true to messages
		# Enable socket blocking
		self.clientSocket.setblocking(True)
		# Save the changes made and close the file
		sendMessage(self.clientSocket, True, "save")
		sendMessage(self.clientSocket, False, "close")
		self.stopEditing.emit(index, self)

		self.onlineBox.hide()

	# def getFileName(self):
	# 	return self.fileName

# This thread constantly checks for updates from the server
class ListenerThread(QThread):
	updateTextbox = pyqtSignal(object)
	updateCursors = pyqtSignal(object)

	def __init__(self, clientSocket):
		super(ListenerThread, self).__init__()
		self.clientSocket = clientSocket

	def run(self):
		decoder = json.JSONDecoder()
		while True:
			try:
				data = self.clientSocket.recv(BUFFER_SIZE)
				print(data)

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
					elif "GetCursorsResp" in o:
						self.updateCursors.emit(o)
			except socket.error:
				time.sleep(0.1)

		print("listener is stopping")

# This thread periodically requests a list of cursors
class CursorRequesterThread(QThread):
	def __init__(self, clientSocket):
		super(CursorRequesterThread, self).__init__()
		self.clientSocket = clientSocket

	def run(self):
		while True:
			sendMessage(self.clientSocket, False, "getCursors")
			time.sleep(5)

		print("cursor requester is stopping")

