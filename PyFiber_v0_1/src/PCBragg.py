# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QWidget, QGridLayout, QMenu, QMainWindow, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QDoubleValidator, QActionGroup
import numpy as np
import warnings

# ------------------------------------------
# Braggs Angles for reference
# ------------------------------------------
class BraggCalc(QMainWindow):
    def __init__(self, parent=None):
        super(BraggCalc, self).__init__(parent)
        self.MainWindow = self
        self.setWindowTitle('Bragg Calculator')

        _width = 400
        _height = 300

        self.n = [1, 2, 3, 4, 5, 6, 7]

        self.setGeometry(self.parent().i_xpos+20, self.parent().i_ypos+20, _width, _height)
        self.initui()

    def initui(self):
        # ------------------------------------------
        # Main Widget
        # ------------------------------------------
        mainwidget = QWidget(self)
        self.MainWindow.setCentralWidget(mainwidget)

        # clear previous values
        self.parent().plotwin.bragg.set_data(x1=[], x2=[])

        # ------------------------------------------
        # Crystal Menu
        # ------------------------------------------
        self.layout = QGridLayout()
        mainwidget.setLayout(self.layout)

        CrystalMenu = QMenu('Crystal Type', self)
        CrystalGroup = QActionGroup(CrystalMenu)

        menubar = self.MainWindow.menuBar()
        menubar.addMenu(CrystalMenu)

        # crystal lattices
        Cubic = CrystalMenu.addAction('Cubic', self.calc_cubic)
        Cubic.setCheckable(True)
        Cubic.setChecked(True)
        Hexagonal = CrystalMenu.addAction('Hexagonal', self.calc_hex)
        Hexagonal.setCheckable(True)
        Monoclinic = CrystalMenu.addAction('Monolinic', self.calc_mono)
        Monoclinic.setCheckable(True)
        Orthorhombic = CrystalMenu.addAction('Orthorhombic', self.calc_ortho)
        Orthorhombic.setCheckable(True)
        Tetragonal = CrystalMenu.addAction('Tetragonal', self.calc_tetra)
        Tetragonal.setCheckable(True)
        Triclinic = CrystalMenu.addAction('Triclinic', self.calc_tric)
        Triclinic.setCheckable(True)
        Trigonal = CrystalMenu.addAction('Trigonal/Rhomohedral', self.calc_trig)
        Trigonal.setCheckable(True)

        CrystalMenu.addAction(Cubic)
        CrystalGroup.addAction(Cubic)
        CrystalMenu.addAction(Hexagonal)
        CrystalGroup.addAction(Hexagonal)
        CrystalMenu.addAction(Monoclinic)
        CrystalGroup.addAction(Monoclinic)
        CrystalMenu.addAction(Orthorhombic)
        CrystalGroup.addAction(Orthorhombic)
        CrystalMenu.addAction(Tetragonal)
        CrystalGroup.addAction(Tetragonal)
        CrystalMenu.addAction(Triclinic)
        CrystalGroup.addAction(Triclinic)
        CrystalMenu.addAction(Trigonal)
        CrystalGroup.addAction(Trigonal)

        CrystalGroup.setExclusive(True)

        # ------------------------------------------
        # Caculator Field
        # ------------------------------------------
        # Radio Buttons for chain Axis
        RBlabel = QLabel()
        RBlabel.setText('Select crystal type above')
        self.layout.addWidget(RBlabel, 0, 1, 1, 3)

        # Wavelength
        Wlabel = QLabel()
        Wlabel.setText('Wavelength [\u212B]')
        self.layout.addWidget(Wlabel, 1, 1, 1, 3)
        self.w = QLineEdit(self)
        self.w.setPlaceholderText('1.5418')
        self.w.setValidator(QDoubleValidator())
        self.layout.addWidget(self.w, 2, 2, 1, 1)

        # Crystal Parameters
        Clabel = QLabel()
        Clabel.setText('Crystal Parameters [\u212B]')
        self.layout.addWidget(Clabel, 3, 1, 1, 3)
        self.a = QLineEdit(self)
        self.a.setPlaceholderText('a')
        self.a.setValidator(QDoubleValidator())
        self.layout.addWidget(self.a, 4, 1, 1, 1)
        self.b = QLineEdit(self)
        self.b.setPlaceholderText('b')
        self.b.setValidator(QDoubleValidator())
        self.layout.addWidget(self.b, 4, 2, 1, 1)
        self.c = QLineEdit(self)
        self.c.setPlaceholderText('c')
        self.c.setValidator(QDoubleValidator())
        self.layout.addWidget(self.c, 4, 3, 1, 1)

        Alabel = QLabel()
        Alabel.setText('Crystal Angles [\u00B0]')
        self.layout.addWidget(Alabel, 5, 1, 1, 3)
        self.alpha = QLineEdit(self)
        self.alpha.setPlaceholderText('\u03B1')
        self.alpha.setValidator(QDoubleValidator())
        self.layout.addWidget(self.alpha, 6, 1, 1, 1)
        self.beta = QLineEdit(self)
        self.beta.setPlaceholderText('\u03B2')
        self.beta.setValidator(QDoubleValidator())
        self.layout.addWidget(self.beta, 6, 2, 1, 1)
        self.gamma = QLineEdit(self)
        self.gamma.setPlaceholderText('\u03B3')
        self.gamma.setValidator(QDoubleValidator())
        self.layout.addWidget(self.gamma, 6, 3, 1, 1)

        # plane 1
        P1label = QLabel()
        P1label.setText('Primary Plane (solid)')
        self.layout.addWidget(P1label, 7, 1, 1, 3)
        self.h1 = QLineEdit(self)
        self.h1.setPlaceholderText('h')
        self.h1.setValidator(QDoubleValidator())
        self.layout.addWidget(self.h1, 8, 1, 1, 1)
        self.k1 = QLineEdit(self)
        self.k1.setPlaceholderText('k')
        self.k1.setValidator(QDoubleValidator())
        self.layout.addWidget(self.k1, 8, 2, 1, 1)
        self.l1 = QLineEdit(self)
        self.l1.setPlaceholderText('l')
        self.l1.setValidator(QDoubleValidator())
        self.layout.addWidget(self.l1, 8, 3, 1, 1)

        # plane 2
        P2label = QLabel()
        P2label.setText('Secondary Plane (dashed)')
        self.layout.addWidget(P2label, 9, 1, 1, 3)
        self.h2 = QLineEdit(self)
        self.h2.setPlaceholderText('h')
        self.h2.setValidator(QDoubleValidator())
        self.layout.addWidget(self.h2, 10, 1, 1, 1)
        self.k2 = QLineEdit(self)
        self.k2.setPlaceholderText('k')
        self.k2.setValidator(QDoubleValidator())
        self.layout.addWidget(self.k2, 10, 2, 1, 1)
        self.l2 = QLineEdit(self)
        self.l2.setPlaceholderText('l')
        self.l2.setValidator(QDoubleValidator())
        self.layout.addWidget(self.l2, 10, 3, 1, 1)

        # calculate button
        Calc = QPushButton('Calculate Angles')
        self.layout.addWidget(Calc, 11, 2, 1, 1)
        Calc.clicked.connect(self.calc_angles)

        self.calc_cubic()
        # ------------------------------------------
        # Status Bar
        # ------------------------------------------
        # self.statusBar().showMessage('Ready')

    def clearlineedits(self):
        self.a.clear()
        self.b.clear()
        self.c.clear()
        self.alpha.clear()
        self.beta.clear()
        self.gamma.clear()
        self.h1.clear()
        self.k1.clear()
        self.l1.clear()
        self.h2.clear()
        self.k2.clear()
        self.l2.clear()
        self.a.setEnabled(True)
        self.b.setEnabled(True)
        self.c.setEnabled(True)
        self.alpha.setEnabled(True)
        self.beta.setEnabled(True)
        self.gamma.setEnabled(True)
        self.h1.setEnabled(True)
        self.k1.setEnabled(True)
        self.l1.setEnabled(True)
        self.h2.setEnabled(True)
        self.k2.setEnabled(True)
        self.l2.setEnabled(True)

    def calc_cubic(self):
        # a = b = c; alpha = beta = gamma
        self.clearlineedits()
        self.b.setText('a')
        self.b.setEnabled(False)
        self.c.setText('a')
        self.c.setEnabled(False)
        self.alpha.setText('90')
        self.alpha.setEnabled(False)
        self.beta.setText('90')
        self.beta.setEnabled(False)
        self.gamma.setText('90')
        self.gamma.setEnabled(False)
        self.calcmod = 0

    def calc_hex(self):
        # a = b |= c; alpha = beta = 90, gamma = 120
        self.clearlineedits()
        self.b.setText('a')
        self.b.setEnabled(False)
        self.alpha.setText('90')
        self.alpha.setEnabled(False)
        self.beta.setText('90')
        self.beta.setEnabled(False)
        self.gamma.setText('120')
        self.gamma.setEnabled(False)
        self.calcmod = 1

    def calc_mono(self):
        # a |= b |= c; alpha = gamma = 90;  beta |= 90
        self.clearlineedits()
        self.alpha.setText('90')
        self.alpha.setEnabled(False)
        self.gamma.setText('90')
        self.gamma.setEnabled(False)
        self.calcmod = 2

    def calc_ortho(self):
        # a |= b |= c; alpha = beta = gamma
        self.clearlineedits()
        self.alpha.setText('90')
        self.alpha.setEnabled(False)
        self.beta.setText('90')
        self.beta.setEnabled(False)
        self.gamma.setText('90')
        self.gamma.setEnabled(False)
        self.calcmod = 3

    def calc_tetra(self):
        # a = b |= c; alpha = beta = gamma
        self.clearlineedits()
        self.b.setText('a')
        self.b.setEnabled(False)
        self.alpha.setText('90')
        self.alpha.setEnabled(False)
        self.beta.setText('90')
        self.beta.setEnabled(False)
        self.gamma.setText('90')
        self.gamma.setEnabled(False)
        self.calcmod = 4

    def calc_tric(self):
        # a |= b |= c; alpha |= beta |= gamma
        self.clearlineedits()
        self.calcmod = 5

    def calc_trig(self):
        self.clearlineedits()
        self.b.setText('a')
        self.b.setEnabled(False)
        self.c.setText('a')
        self.c.setEnabled(False)
        self.beta.setText('\u03B1')
        self.beta.setEnabled(False)
        self.gamma.setText('\u03B1')
        self.gamma.setEnabled(False)
        self.calcmod = 6

    def calc_angles(self):

        if self.calcmod == 0:
            self.b.setText(str(self.a.text()))
            self.c.setText(str(self.a.text()))
            self.beta.setText(str(self.alpha.text()))
            self.beta.setText(str(self.gamma.text()))
        elif self.calcmod == 1:
            self.b.setText(str(self.a.text()))
        elif self.calcmod == 4:
            self.b.setText(str(self.a.text()))
        elif self.calcmod == 6:
            self.b.setText(str(self.a.text()))
            self.c.setText(str(self.a.text()))
            self.beta.setText(str(self.alpha.text()))
            self.beta.setText(str(self.gamma.text()))

        if len(self.w.text()) == 0:
            self.parent().parent().statusBar.showMessage('No Xray wavelength specified')
            raise ValueError('No Xray wavelength specified')
        else:
            lam = float(self.w.text())

        if len(self.a.text()) == 0:
            self.parent().parent().statusBar.showMessage('Lattice parameter \"a\" not specified')
            raise ValueError('Lattice parameter \"a\" not specified')
        else:
            aval = float(self.a.text())

        if len(self.b.text()) == 0:
            self.parent().parent().statusBar.showMessage('Lattice parameter \"b\" not specified')
            raise ValueError('Lattice parameter \"b\" not specified')
        else:
            bval = float(self.b.text())

        if len(self.c.text()) == 0:
            self.parent().parent().statusBar.showMessage('Lattice parameter \"c\" not specified')
            raise ValueError('Lattice parameter \"c\" not specified')
        else:
            cval = float(self.c.text())

        if len(self.alpha.text()) == 0:
            self.parent().parent().statusBar.showMessage('Lattice angle \"alpha\" not specified')
            raise ValueError('Lattice angle \"alpha\" not specified')
        else:
            alval = float(self.alpha.text()) * np.pi / 180.0

        if len(self.beta.text()) == 0:
            self.parent().parent().statusBar.showMessage('Lattice angle \"beta\" not specified')
            raise ValueError('Lattice angle \"beta\" not specified')
        else:
            beval = float(self.beta.text()) * np.pi / 180.0

        if len(self.gamma.text()) == 0:
            self.parent().parent().statusBar.showMessage('Lattice angle \"gamma\" not specified')
            raise ValueError('Lattice angle \"gamma\" not specified')
        else:
            gaval = float(self.gamma.text()) * np.pi / 180.0

        if len(self.h1.text()) == 0:
            self.parent().parent().statusBar.showMessage('h1 plane interval not specified')
            raise ValueError('h1 plane interval not specified')
        else:
            h1val = float(self.h1.text())

        if len(self.k1.text()) == 0:
            self.parent().parent().statusBar.showMessage('k1 plane interval not specified')
            raise ValueError('k1 plane interval not specified')
        else:
            k1val = float(self.k1.text())

        if len(self.l1.text()) == 0:
            self.parent().parent().statusBar.showMessage('l1 plane interval not specified')
            raise ValueError('l1 plane interval not specified')
        else:
            l1val = float(self.l1.text())

        if len(self.h2.text()) == 0:
            self.parent().parent().statusBar.showMessage('h2 plane interval not specified')
            raise ValueError('h2 plane interval not specified')
        else:
            h2val = float(self.h2.text())

        if len(self.k2.text()) == 0:
            self.parent().parent().statusBar.showMessage('k2 plane interval not specified')
            raise ValueError('k2 plane interval not specified')
        else:
            k2val = float(self.k2.text())

        if len(self.l2.text()) == 0:
            self.parent().parent().statusBar.showMessage('l2 plane interval not specified')
            raise ValueError('l2 plane interval not specified')
        else:
            l2val = float(self.l2.text())

        # d spacings http://pd.chem.ucl.ac.uk/pdnn/unit1/unintro.htm
        # http://duffy.princeton.edu/sites/default/files/pdfs/links/xtalgeometry.pdf

        # cubic
        if self.calcmod == 0:
            # cubic D Spacing
            dnum = aval ** 2
            ddenom1 = h1val ** 2 + k1val ** 2 + l1val ** 2
            ddenom2 = h2val ** 2 + k2val ** 2 + l2val ** 2

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        # hexagonal
        elif self.calcmod == 1:
            # hexagonal D Spacing
            dnum = 3 * aval ** 2 + cval ** 2
            ddenom1 = 4 * (h1val ** 2 + h1val * k1val + k1val ** 2) * cval ** 2 + 3 * l1val ** 2 * aval ** 2
            ddenom2 = 4 * (h2val ** 2 + h2val * k2val + k2val ** 2) * cval ** 2 + 3 * l2val ** 2 * aval ** 2

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        # monoclinic
        elif self.calcmod == 2:
            # Monoclinic
            # PVA hkl to braggs angle

            # Monoclinic D Spacing
            dnum = aval ** 2 * bval ** 2 * cval ** 2 * np.sin(beval) ** 2
            ddenom1 = h1val ** 2 * bval ** 2 * cval ** 2 + k1val ** 2 * aval ** 2 * cval ** 2 * np.sin(
                bval) ** 2 + l1val ** 2 * aval ** 2 * bval ** 2 - 2 * h1val * l1val * np.cos(
                beval) * aval * bval ** 2 * cval
            ddenom2 = h2val ** 2 * bval ** 2 * cval ** 2 + k2val ** 2 * aval ** 2 * cval ** 2 * np.sin(
                bval) ** 2 + l2val ** 2 * aval ** 2 * bval ** 2 - 2 * h1val * l2val * np.cos(
                beval) * aval * bval ** 2 * cval

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        # orthorhombix
        elif self.calcmod == 3:
            # Orthorhombic D Spacing
            dnum = aval ** 2 * bval ** 2 * cval ** 2
            ddenom1 = h1val ** 2 * aval ** 2 * bval ** 2 + k1val ** 2 * aval ** 2 * cval ** 2 + l1val ** 2 * aval ** 2 * cval ** 2
            ddenom2 = h2val ** 2 * aval ** 2 * bval ** 2 + k2val ** 2 * aval ** 2 * cval ** 2 + l2val ** 2 * aval ** 2 * cval ** 2

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        # tetragonal
        elif self.calcmod == 4:
            # Tetragonal D Spacing
            dnum = aval ** 2 * cval ** 2
            ddenom1 = cval ** 2 * (h1val ** 2 + k1val ** 2) + aval ** 2 * l1val ** 2
            ddenom2 = cval ** 2 * (h2val ** 2 + k2val ** 2) + aval ** 2 * l2val ** 2

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        # triclinic
        elif self.calcmod == 5:
            # Triclinic D Spacing
            S11 = bval ** 2 * cval ** 2 * np.sin(alval) ** 2
            S22 = aval ** 2 * cval ** 2 * np.sin(beval) ** 2
            S33 = bval ** 2 * bval ** 2 * np.sin(gaval) ** 2
            S12 = aval * bval * cval ** 2 * (np.cos(alval) * np.cos(beval) - np.cos(gaval))
            S23 = aval ** 2 * bval * cval * (np.cos(beval) * np.cos(gaval) - np.cos(alval))
            S13 = aval * bval ** 2 * cval * (np.cos(gaval) * np.cos(alval) - np.cos(beval))
            V = aval * bval * cval * np.sqrt(
                1 - np.cos(alval) ** 2 - np.cos(beval) ** 2 - np.cos(gaval) ** 2 + 2 * np.cos(alval) * np.cos(
                    beval) * np.cos(gaval))

            dnum = V ** 2
            ddenom1 = S11 * h1val ** 2 + S22 * k1val ** 2 + S33 * l1val ** 2 + 2 * S12 * h1val * k1val + 2 * S23 * k1val * l1val + 2 * S13 * h1val * l1val
            ddenom2 = S11 * h2val ** 2 + S22 * k2val ** 2 + S33 * l2val ** 2 + 2 * S12 * h2val * k2val + 2 * S23 * k2val * l2val + 2 * S13 * h1val * l1val

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        # trigonal/rhombohedral
        elif self.calcmod == 6:
            # Trigonal / Rhombohedral D Spacing
            dnum = aval ** 2 * (1 - 3 * np.cos(alval) ** 2 + 2 * np.cos(alval) ** 3)
            ddenom1 = (h1val ** 2 + k1val ** 2 + l1val ** 2) * np.sin(alval) ** 2 + 2 * (
                    h1val * k1val + k1val * l1val + h1val * l1val) * (np.cos(alval) ** 2 - np.cos(alval))
            ddenom2 = (h2val ** 2 + k2val ** 2 + l2val ** 2) * np.sin(alval) ** 2 + 2 * (
                    h2val * k2val + k2val * l2val + h2val * l2val) * (np.cos(alval) ** 2 - np.cos(alval))

            d1 = np.sqrt(dnum / ddenom1)
            d2 = np.sqrt(dnum / ddenom2)

        self.theta1 = []
        self.theta2 = []

        for i in self.n:
            # Runtime warning on some hkl plane inputs (go off screen)
            # warnings.filterwarnings('ignore', category=RuntimeWarning)
            self.theta1.append(round(np.arcsin(i * lam / (2 * d1)) * 180 / np.pi, 4))
            self.theta2.append(round(np.arcsin(i * lam / (2 * d2)) * 180 / np.pi, 4))

        self.parent().plotwin.bragg.set_data(x1=self.theta1, x2=self.theta2)

class BraggManual(QMainWindow):
    def __init__(self, parent=None):
        super(BraggManual, self).__init__(parent)
        _width = 400
        _height = 100

        self.n = [1, 2, 3, 4, 5, 6, 7]

        self.setGeometry(self.parent().i_xpos+20, self.parent().i_ypos+20, _width, _height)
        self.initUI()

    def initUI(self):

        # ------------------------------------------
        # Main Widget
        # ------------------------------------------
        self.MainWindow = self
        self.setWindowTitle('Bragg Manual')
        _mainwidget = QWidget(self)
        self.MainWindow.setCentralWidget(_mainwidget)

        # clear previous values
        self.parent().plotwin.bragg.set_data(x1=[], x2=[])

        # ------------------------------------------
        # Crystal Menu
        # ------------------------------------------
        self.layout = QGridLayout()
        _mainwidget.setLayout(self.layout)

        _t1label = QLabel()
        _t1label.setText('Primary Plane Crystal Angles [\u00B0]')
        self.layout.addWidget(_t1label, 0, 1, 1, 10)
        # primary plane
        self.a1 = QLineEdit(self)
        self.layout.addWidget(self.a1, 1, 1, 1, 1)
        self.a2 = QLineEdit(self)
        self.layout.addWidget(self.a2, 1, 2, 1, 1)
        self.a3 = QLineEdit(self)
        self.layout.addWidget(self.a3, 1, 3, 1, 1)
        self.a4 = QLineEdit(self)
        self.layout.addWidget(self.a4, 1, 4, 1, 1)
        self.a5 = QLineEdit(self)
        self.layout.addWidget(self.a5, 1, 5, 1, 1)
        self.a6 = QLineEdit(self)
        self.layout.addWidget(self.a6, 1, 6, 1, 1)
        self.a7 = QLineEdit(self)
        self.layout.addWidget(self.a7, 1, 7, 1, 1)

        _t2label = QLabel()
        _t2label.setText('Secondary Plane Crystal Angles [\u00B0]')
        self.layout.addWidget(_t2label, 2, 1, 1, 10)
        # primary plane
        self.b1 = QLineEdit(self)
        self.layout.addWidget(self.b1, 3, 1, 1, 1)
        self.b2 = QLineEdit(self)
        self.layout.addWidget(self.b2, 3, 2, 1, 1)
        self.b3 = QLineEdit(self)
        self.layout.addWidget(self.b3, 3, 3, 1, 1)
        self.b4 = QLineEdit(self)
        self.layout.addWidget(self.b4, 3, 4, 1, 1)
        self.b5 = QLineEdit(self)
        self.layout.addWidget(self.b5, 3, 5, 1, 1)
        self.b6 = QLineEdit(self)
        self.layout.addWidget(self.b6, 3, 6, 1, 1)
        self.b7 = QLineEdit(self)
        self.layout.addWidget(self.b7, 3, 7, 1, 1)

        # commit button
        _commit = QPushButton('Commit Angles')
        self.layout.addWidget(_commit, 4, 3, 1, 3)
        _commit.clicked.connect(self.commit_angles)

    def commit_angles(self):

        self.x1 = [self.a1.text(), self.a2.text(), self.a3.text(), self.a4.text(), self.a5.text(), self.a6.text(),
                   self.a7.text()]
        self.x2 = [self.b1.text(), self.b2.text(), self.b3.text(), self.b4.text(), self.b5.text(), self.b6.text(),
                   self.b7.text()]
        _theta1 = []
        _theta2 = []
        for i in range(0, 6):
            try:
                _theta1 += [float(self.x1[i])]
            except:
                _theta1 += [0]
            try:
                _theta2 += [float(self.x2[i])]
            except:
                _theta2 += [0]
        self.parent().plotwin.bragg.set_data(x1=_theta1, x2=_theta2)


class BraggClear(QMainWindow):
    def __init__(self, parent=None):
        super(BraggClear, self).__init__(parent)
        self.parent().plotwin.bragg.set_data(x1=[], x2=[])
