from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from lib import *
import json, string, difflib, socket, sys

# TODO: Refactor this into a class
fontName = 'Lucida Console'
fontSize = 14

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
		# Save the changes made and close the file
		sendMessage(self.clientSocket, "save")
		sendMessage(self.clientSocket, "close")
		self.stopEditing.emit(self.clientSocket)

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self, clientSocket, fileName):
		super(Textbox, self).__init__()
		self.setFont(QFont(fontName, fontSize)) # Set the font
		self.clientSocket = clientSocket # Save the socket
		
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
			elif tag == "delete": # If characters were deleted
				sendMessage(self.clientSocket, "remove", i1, i2-i1)
			elif tag == "insert": # If characters were inserted
				sendMessage(self.clientSocket, "write", i1, self.toPlainText()[j1:j2])

		self.prevText = self.toPlainText()
