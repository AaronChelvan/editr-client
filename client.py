from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import json, string, difflib

# The main window for the client program
class MainWindow(QMainWindow):
	# Constructor
	def __init__(self):
		super(MainWindow, self).__init__()
		self.setCentralWidget(Textbox()) # Add a Textbox to the window

# The textbox where the file contents will be displayed
class Textbox(QTextEdit):
	# Constructor
	def __init__(self):
		super(Textbox, self).__init__()
		self.setFont(QFont('Monospace', 14)) # Set the font
		self.textChanged.connect(self.textChangedHandler)
		#self.prevCursorPosition = self.textCursor().selectionStart()
		#self.cursorPositionChanged.connect(self.cursorPositionChangedHandler)
		self.prevCursorPosition2 = self.textCursor().selectionStart()
		#self.selectionChanged.connect(self.selectionChangedHandler)
		self.prevCursorPosition3 = self.textCursor().selectionStart()
		self.prevText = self.toPlainText()
	
	# to use setText() without triggering textChanged, disable signals, call setText(), then enable signals again
	def textChangedHandler(self): #doesn't handle if the cursor moves without writing/removing		
		# The location of the cursor
		cursorPosition = self.textCursor().selectionStart()

		'''
		if len(self.toPlainText()) > len(self.prevText):
			print("char(s) were added")
			numCharsAdded
		elif len(self.toPlainText()) == len(self.prevText):
			print("one char was overwritten")
		else:
			print("one char was backspaced or deleted, or multiple chars were highlighted and deleted (and maybe overwritten with one char)")
		'''
		s = difflib.SequenceMatcher(None, self.prevText, self.toPlainText())
		'''
		blocks = s.get_matching_blocks()
		numBlocks = len(blocks)
		
		# TODO handle when char(s) are overwritten by an equal number of char(s)
		
		if numBlocks == 1:
			if blocks[0].a > 0: # Input was added to an empty textbox
				print("inserted %d chars at %d" % (blocks[0].a, 0))
			elif blocks[0].b > 0: # All input in the textbox was deleted
				print("deleted %d chars at %d" % (blocks[0].b, 0))
			else:
				print("error")
				exit()
		elif numBlocks == 2:
			if blocks[0].a > blocks[0].b: # Chars inserted at the beginning
				print("inserted %d chars at %d" % (blocks[0].a - blocks[0].b, 0))
			elif blocks[0].b > blocks[0].a: # Chars removed from beginning
				print("deleted %d chars at %d" % (blocks[0].b - blocks[0].a, 0))
			elif blocks[1].a > blocks[1].b: # Chars inserted at the end
				print("inserted %d chars at %d" % (blocks[1].a - blocks[1].b, blocks[0].size))
			elif blocks[1].b > blocks[1].a: # Chars removed from end
				print("deleted %d chars at %d" % (blocks[1].b - blocks[1].a, blocks[0].size))
		elif numBlocks == 3:
			# Text was added/deleted from the middle, or text was overwritten
			if blocks[1].a > blocks[1].b:
				print("inserted %d chars at %d" % (blocks[1].a - blocks[1].b, blocks[1].b))
			elif blocks[1].b > blocks[1].a:
				print("deleted %d chars at %d" % (blocks[1].b - blocks[1].a, blocks[1].a))
		'''
		for tag, i1, i2, j1, j2 in s.get_opcodes():
			if tag == "replace":
				print("remove %d chars from %d" % (i2-i1, i1))
				print("insert %d chars at %d" % (j2-j1, i1))
			elif tag == "delete":
				print("remove %d chars from %d" % (i2-i1, i1))
			elif tag == "insert":
				print("insert %d chars at %d" % (j2-j1, i1))

		print()
		self.prevText = self.toPlainText()
		#print("cursor moved from %d to %d" % (self.prevCursorPosition3, cursorPosition))
		#self.prevCursorPosition = cursorPosition
	
	
	def cursorPositionChangedHandler(self):
		# The location of the cursor
		print("cursor position changed")
		cursorPosition = self.textCursor().selectionStart()
		print("cursor moved from %d to %d" % (self.prevCursorPosition3, cursorPosition))
		self.prevCursorPosition3 = self.prevCursorPosition2
		self.prevCursorPosition2 = cursorPosition

		# To determine the characters that were deleted, use undo, get the new cursor location, then redo,
		# and compute the difference

	'''
	def selectionChangedHandler(self):
		print("selection changed")
		cursorPosition = self.textCursor().selectionStart()
		if cursorPosition
	'''


	'''
	# When a key is pressed
	def keyPressEvent(self, event):
		# The location of the cursor
		cursorPosition = self.textCursor().selectionStart()

		# The number of characters highlighted (0 == no characters highlighted)
		numHighlightedChars = self.textCursor().selectionEnd() - self.textCursor().selectionStart()

		# User pressed backspace
		if event.key() == Qt.Key_Backspace:
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)
			elif self.textCursor().atStart() == False: # Is there a character to the left of the cursor?
				sendUpdate("remove", cursorPosition-1, 1)
			else:
				print("Nothing to delete")

		# User pressed delete
		elif event.key() == Qt.Key_Delete:
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)
			elif self.textCursor().atEnd() == False: # Is there a character to the right of the cursor?
				sendUpdate("remove", cursorPosition, 1)
			else:
				print("Nothing to delete")

		# User pressed a printable character
		elif event.text() in string.printable and event.text() != "":
			# If one or more characters are highlighted, they will get overwritten
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)

			# Write the new character
			if event.text() == "\r": # \r should be a newline char
				char = "\n"
			else:
				char = event.text()
			sendUpdate("write", cursorPosition, char)
		
		# User pressed cut (Ctrl + X)
		elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
			if numHighlightedChars > 0:
				sendUpdate("remove", cursorPosition, numHighlightedChars)

		# User pressed paste (Ctrl + V)
		elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
			sendUpdate("write", cursorPosition, QApplication.clipboard().text())

		# Process the key press in the textbox
		super(Textbox, self).keyPressEvent(event)
	'''

# When the contents of the textbox is edited, generate a JSON string describing the edit
# and send it to the server
def sendUpdate(*args):
	message = {}
	if args[0] == "open":
		# TODO
		pass
	elif args[0] == "write":
		data = list(bytes(args[2], "utf-8"))
		message["WriteReq"] = {"offset": args[1], "data": data}
	elif args[0] == "read":
		# TODO
		pass
	elif args[0] == "remove":
		message["RemoveReq"] = {"offset": args[1], "len": args[2]}
	else:
		print("Unknown operation")
		exit()
	print(message)

	# TODO 
	# convert "message" to a JSON string and send it to the server


app = QApplication([])
app.setApplicationName("Editr Client")

window = MainWindow()
window.show()
app.exec_()
