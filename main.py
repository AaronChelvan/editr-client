import sys
import textEditor
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, qApp, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QStackedLayout, QWidget, QToolBox
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt

class Controller:

    def __init__(self):
        pass


    def show_text_editor(self): # The textbox
        self.text = textEditor.textEditorWindow()
        self.text.show()

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
    controller.show_text_editor()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
