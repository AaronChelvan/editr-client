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
	stopEditing = pyqtSignal(object)

	# Constructor
	# TODO: Refactor constructor, it's way too long :(
	def __init__(self, clientSocket, fileName):
		super(textEditorWindow, self).__init__()
		self.setGeometry(400, 400, 600, 500)
		self.textbox = Textbox(clientSocket, fileName)
		self.setCentralWidget(self.textbox) # Add a Textbox to the window
		self.clientSocket = clientSocket
		self.configureMenubarAndToolbar()

	def configureMenubarAndToolbar(self):
		mainMenu = self.menuBar()

		toolbar = QToolBar('Toolbar', self)
		self.addToolBar(toolbar)

		fileMenu = mainMenu.addMenu('&File')
		editMenu = mainMenu.addMenu('&Edit')

		# =========== Actions =========== #
		# === File === #
		saveAct = QAction('&Save and close', self)
		saveAct.setStatusTip('Save the current file and close the editor.')
		saveAct.triggered.connect(self.stopEditingFunction)
		fileMenu.addAction(saveAct)

		# === Edit === #
		cutAct = QAction('&Cut', self)
		cutAct.setStatusTip('Cut the current selection')
		cutAct.triggered.connect(self.textbox.cut)
		editMenu.addAction(cutAct)

		copyAct = QAction('&Copy', self)
		copyAct.setStatusTip('Copy the current selection')
		copyAct.triggered.connect(self.textbox.copy)
		editMenu.addAction(copyAct)

		pasteAct = QAction('&Paste', self)
		pasteAct.setStatusTip('Paste the current selection')
		pasteAct.triggered.connect(self.textbox.paste)
		editMenu.addAction(pasteAct)

		editMenu.addSeparator()

		undoAct = QAction('&Undo', self)
		undoAct.setStatusTip('Undo the current selection')
		undoAct.triggered.connect(self.textbox.undo)
		editMenu.addAction(undoAct)

		redoAct = QAction('&Redo', self)
		redoAct.setStatusTip('Redo the current selection')
		redoAct.triggered.connect(self.textbox.redo)
		editMenu.addAction(redoAct)

		editMenu.addSeparator()

		findAct = QAction('&Find', self)
		editMenu.addAction(findAct)

		replaceAct = QAction('&Replace', self)
		editMenu.addAction(replaceAct)

		# Toolbar things #
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
		# TODO: Fix the manual text input (it breaks when it is editable and certain control keys are pressed)
		# fontSizeSelect.setEditable(True)
		# fontSizeSelect.setValidator(QIntValidator(1,1638))
		fontSizeSelect.currentIndexChanged.connect(self.updateFontSizeIndex)
		# fontSizeSelect.currentTextChanged.connect(self.updateFontSizeText)

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

	def stopEditingFunction(self):
		# Stop the listener thread
		global listenerThread
		listenerThread.terminate()
		listenerThread.wait()

		# Enable socket blocking
		self.clientSocket.setblocking(True)

		# Save the changes made and close the file
		sendMessage(self.clientSocket, True, "save")
		sendMessage(self.clientSocket, True, "close")

		# Go to the file selection menu
		self.stopEditing.emit(self.clientSocket)

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket, fileName):
		super(Textbox, self).__init__()
		self.clientSocket = clientSocket # Save the socket

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
