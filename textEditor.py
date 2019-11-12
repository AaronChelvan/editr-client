from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, difflib, socket, sys

# The text editor window
class textEditorWindow(QMainWindow):
	stopEditing = pyqtSignal(object)
	closing = pyqtSignal(object)
	updateOpen = pyqtSignal(str)
	# Constructor
	def __init__(self, clientSocket, fileName, openFiles, curList):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.textBoxList = []
		self.text = Textbox(clientSocket, fileName, self.signalEvent)
		self.textBoxList.append(self.text)
		self.openFiles = openFiles
		self.fileList = curList
		self.plusPosition = 1

		#self.setCentralWidget(text) # Add a Textbox to the window
		self.clientSocket = clientSocket
		self.fileName = fileName
		#need to add this button back
		closeButton = QPushButton('Save & Close', self)
		closeButton.move(450, 450)
		closeButton.clicked.connect(self.stopEditingFunction)

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
		open = self.openFiles()
		if fileName in open:
			showErrorMessage("File is already open!")
		else:
			response = sendMessage(self.clientSocket, "open", fileName)
			if "Err" in response["OpenResp"]:
				showErrorMessage(response["OpenResp"]["Err"])
			else:

				self.tabs.removeTab(self.plusPosition)
				tab = QWidget()
				text = Textbox(self.clientSocket, fileName, self.signalEvent)
				self.tabs.addTab(tab, fileName)
				tab.layout = QVBoxLayout(self)

				tab.layout.addWidget(text)
				tab.setLayout(tab.layout)
				self.textBoxList.append(text)
				self.addPlusTab()
				self.plusPosition += 1

				self.updateOpen.emit(fileName)


	def addPlusTab(self):
		tab2 = QWidget()
		self.tabs.addTab(tab2, "+")
		# Just make a function for Tabs
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


	def stopEditingFunction(self):
		# Save the changes made and close the file
		sendMessage(self.clientSocket, "save")
		sendMessage(self.clientSocket, "close")
		self.stopEditing.emit(self.clientSocket)

	def closeEvent(self, event: QCloseEvent):
		print("Window {} closed".format(self))
		self.closing.emit(self.fileName)
		super().closeEvent(event)

	def signalEvent(self, fileName):
		self.closing.emit(fileName)

	def setFileList(self, fileList):
		self.fileList = fileList


# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket,fileName, signalEvent):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.clientSocket = clientSocket # Save the socket
		self.signalEvent = signalEvent
		self.fileName = fileName
		# Read the file contents and display it in the textbox
		response = sendMessage(self.clientSocket, "read", 0, 999)
		fileContents = response["ReadResp"]["Ok"]
		fileContents = bytearray(fileContents).decode("utf-8")
		self.setText(fileContents)
		
		# Start detecting edits made to the textbox contents
		self.textChanged.connect(self.textChangedHandler)
		self.prevText = self.toPlainText() # The content currently in the textbox

	# This functions executes everytime the contents of the textbox changes
	def textChangedHandler(self):
		# Use sequence matcher to find what changes were made to the textbox contents
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())

		# Iterate through the changes
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace": # If characters were overwritten
				sendMessage(self.clientSocket, "remove", i1, i2-i1)
				sendMessage(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])
			elif tag == "remove": # If characters were removed
				sendMessage(self.clientSocket, "remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendMessage(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()

	def closeEvent(self, event: QCloseEvent):
		print("Window {} closed".format(self))
		self.signalEvent(self.fileName)
		super().closeEvent(event)
