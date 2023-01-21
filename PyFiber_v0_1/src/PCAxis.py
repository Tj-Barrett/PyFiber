# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QWidget, QGridLayout, QMenu, QMainWindow, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QActionGroup
import numpy as np


# ------------------------------------------
# Braggs Angles for reference
# ------------------------------------------
class AxisWin(QMainWindow):
    def __init__(self, parent=None):
        super(AxisWin, self).__init__(parent)
        _width = 300
        _height = 100

        self.n = [1, 2]

        # dialog window
        self.setGeometry(self.parent().i_xpos+20, self.parent().i_ypos+20, _width, _height)
        self.initUI()

    def initUI(self):

        # ------------------------------------------
        # Main Widget
        # ------------------------------------------
        self.MainWindow = self
        self.setWindowTitle('Axis Manual')
        _mainwidget = QWidget(self)
        self.MainWindow.setCentralWidget(_mainwidget)

        # ------------------------------------------
        # Axis Menu
        # ------------------------------------------
        self.layout = QGridLayout()
        _mainwidget.setLayout(self.layout)

        _t1label = QLabel()
        _t1label.setText('Angle [\u00B0]')
        self.layout.addWidget(_t1label, 0, 1, 1, 10)
        # primary plane
        _a1 = QLabel()
        _a1.setText('Low')
        self.layout.addWidget(_a1, 1, 1, 1, 1)
        self.a2 = QLineEdit(self)
        self.a2.setText('5')
        self.layout.addWidget(self.a2, 1, 2, 1, 1)
        _a3 = QLabel()
        _a3.setText('High')
        self.layout.addWidget(_a3, 1, 3, 1, 1)
        self.a4 = QLineEdit(self)
        self.a4.setText('60')
        self.layout.addWidget(self.a4, 1, 4, 1, 1)

        _t2label = QLabel()
        _t2label.setText('Intensity')
        self.layout.addWidget(_t2label, 2, 1, 1, 10)
        # primary plane
        _b1 = QLabel()
        _b1.setText('Low')
        self.layout.addWidget(_b1, 3, 1, 1, 1)
        self.b2 = QLineEdit(self)
        self.b2.setText('0')
        self.layout.addWidget(self.b2, 3, 2, 1, 1)
        _b3 = QLabel()
        _b3.setText('High')
        self.layout.addWidget(_b3, 3, 3, 1, 1)
        self.b4 = QLineEdit(self)
        self.b4.setText('0.20')
        self.layout.addWidget(self.b4, 3, 4, 1, 1)

        # commit button
        _commit = QPushButton('Commit Angles')
        self.layout.addWidget(_commit, 4, 2, 1, 2)
        _commit.clicked.connect(self.commit_angles)

    def commit_angles(self):
        self.parent().xrd_max = float(self.b4.text())
        self.parent().angle_min = float(self.a2.text())
        self.parent().angle_max = float(self.a4.text())