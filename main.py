import sys
import textEditor
import serverMenu
import fileMenu
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt

class Controller:

    def __init__(self):
        pass

    def show_server_menu(self): # The menu where we select a server
        #if self.window != None:
        #    self.window.close()
        self.menu = serverMenu.serverMenuWindow()
        self.menu.connectSuccessful.connect(self.show_file_menu)
        self.menu.show()

    
    def show_file_menu(self, clientSocket, port): # The menu where we select a file
        self.port = port
        self.menu.close()
        self.window = fileMenu.fileMenuWindow(clientSocket)
        self.window.startEditing.connect(self.show_text_editor)
        self.window.closeConnection.connect(self.show_server_menu)
        self.window.updateList.connect(self.updateTextList)
        self.window.show()


    def show_text_editor(self, clientSocket, fileName, curList, username): # The textbox
        text = textEditor.textEditorWindow(clientSocket, fileName,self.window.returnOpenFiles, curList, self.port, username)
        text.updateOpen.connect(self.updateOpenFiles)
        text.removeOpen.connect(self.removeOpenFiles)
        self.window.appendTextList(text)

    def updateTextList(self, listFiles):
        for object in self.window.textlist:
            object.setFileList(listFiles)

    def updateOpenFiles(self, fileName):
        self.window.updateOpenFiles(fileName)

    def removeOpenFiles(self,fileNameList):
        self.window.removeOpenFiles(fileNameList)

# The colour scheme
def palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    return palette

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Editr")
    app.setPalette(palette())
    app.setWindowIcon(QIcon("EditrLogo"))
    controller = Controller()
    controller.show_server_menu()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
