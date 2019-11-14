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
	# Constructor
	def __init__(self, clientSocket, fileName, openFiles, curList, port):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.textBoxList = []
		self.openFiles = openFiles

		self.port = port
		self.ip = clientSocket.getsockname()[0]
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

	def newTabFunction(self):
		fileName = self.comboBox.currentText()

		clientSocket = self.createSocket(fileName, False)
		if clientSocket is None:
			return

		self.tabs.removeTab(self.plusPosition)
		self.tabsNextIndex += -1
		tab = QWidget()
		text = Textbox(clientSocket, fileName, self.tabsNextIndex)
		self.tabsNextIndex += 1
		self.plusPosition = self.tabsNextIndex
		self.tabsNextIndex += 1
		text.stopEditing.connect(self.removeTab)
		self.tabs.addTab(tab, fileName)
		tab.layout = QVBoxLayout(self)

		tab.layout.addWidget(text)
		tab.setLayout(tab.layout)
		self.textBoxList.append(text)
		self.addPlusTab()

		self.updateOpen.emit(fileName)


	def addPlusTab(self):
		tab2 = QWidget()
		self.tabs.addTab(tab2, "+")
		self.pushButton1 = QPushButton("Add New Connection")
		self.pushButton1.clicked.connect(self.newTabFunction)
		tab2.layout = QVBoxLayout(self)
		tab2.layout.addWidget(self.pushButton1)
		tab2.setLayout(tab2.layout)

		self.comboBox = QComboBox(tab2)
		self.comboBox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

		#self.comboBox.clear()
		for file in self.fileList:
			self.comboBox.addItem(file)

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

