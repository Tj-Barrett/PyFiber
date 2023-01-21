# This Python file uses the following encoding: utf-8
import os

import pandas.errors
from PySide6.QtWidgets import QFileDialog
import pandas as pd

from src.PCfCurveFit import *


# ------------------------------------------
# Get File
# ------------------------------------------
def getfile(self, input_type, filename=None):
    # ------------------------------------------
    # Get File Window
    # ------------------------------------------
    if filename is None:
        _fname = QFileDialog.getOpenFileName(self,
                                             'Select data file...',
                                             self.destination,
                                             'Data Files (*.csv *.xlsx *.xls *.txt)',
                                             options=QFileDialog.DontUseNativeDialog)
        _fname = ''.join(_fname[0])
        # Needed by save state
        self.openname = _fname
        _head, _tail = os.path.split(_fname)
        # reset where getfile looks
        self.destination = _head
        _ext = os.path.splitext(_fname)[-1].lower()
    else:
        _fname = filename
        _head, _tail = os.path.split(_fname)
        # reset where getfile looks
        self.destination = _head
        _ext = os.path.splitext(_fname)[-1].lower()

    # ------------------------------------------
    # Clear previous data
    # ------------------------------------------
    if self.newrun == 0:
        self.parent().mainwidget.newstate()

    _names = ['XRDBin', 'XRDCoord', 'XRDCount', 'XRDCountTot', 'Extra']
    _ref = pd.read_csv(self.reference, header=3, names=_names, sep=" ")
    # Used globally
    self.angle = _ref.XRDBin
    self.refcount = _ref.XRDCount
    # ------------------------------------------
    # LAMMPS
    # ------------------------------------------
    # integer error code
    _iError = 0
    _data = []
    if input_type == 'LAMMPS':
        self.typefile = 'LAMMPS'
        try:
            if _ext == '.csv':
                _names = ['XRDBin', 'XRDCoord', 'XRDCount', 'XRDCountTot', 'Extra']
                _data = pd.read_csv(filename=_fname,
                                    header=3,
                                    names=_names)

            elif _ext in ['.xls', '.xlsx']:
                _names = ['XRDBin', 'XRDCoord', 'XRDCount', 'XRDCountTot', 'Extra']
                _data = pd.read_excel(_fname, header=3, names=_names, engine='openpyxl')

            elif _ext == '.txt':
                _names = ['XRDBin', 'XRDCoord', 'XRDCount', 'XRDCountTot', 'Extra']
                _data = pd.read_csv(_fname, header=3, names=_names, sep=" ")
        except TypeError:
            _iError = 1
        except ValueError:
            _iError = 1
        except pandas.errors.ParserError:
            _iError = 2

    # ------------------------------------------
    # XRD
    # ------------------------------------------
    elif input_type == 'WAXD':
        self.typefile = 'WAXD'
        try:
            if _ext == '.csv':
                try: # PDXL
                    _names = ['XRD2T', 'XRDInt', 'ycal', 'bkg', 'diff', 'nan']
                    _data = pd.read_csv(_fname, header=1, names=_names)
                except:
                    _names = ['XRD2T', 'XRDInt']
                    _data = pd.read_csv(_fname, header=1, names=_names)

            elif _ext in ['.xls', '.xlsx']:
                _names = ['XRD2T', 'XRDInt']
                _data = pd.read_excel(_fname, header=1, names=_names, engine='openpyxl')

            elif _ext == '.txt':
                _names = ['XRD2T', 'XRDInt']
                _data = pd.read_csv(_fname, header=1, names=_names, sep=" ")

        except TypeError:
            _iError = 1
        except pandas.errors.ParserError:
            _iError = 2

    # ------------------------------------------
    # Reference
    # ------------------------------------------
    elif input_type == 'Ref':
        self.typefile = 'Ref'
        _xrd_count = np.absolute(self.refcount)

    # ------------------------------------------
    # Handling data
    # ------------------------------------------
    if input_type == 'LAMMPS':
        try:
            _xrdbin = _data.XRDBin.values.tolist()
            _xrd_count = _data.XRDCount.values.tolist()

            if np.max(_xrdbin) < 180.0:
                # Make sure there is only one timestep

                # Remove over 5 degrees
                _AC = [(i, j) for (i, j) in zip(_xrdbin, _xrd_count) if i >= 5]
                _xrdbin, _xrd_count = zip(*_AC)
                self.angle = np.array(_xrdbin)
                _xrd_count = np.array(_xrd_count)

                # adjust any linear difference
                _left_adj = 0
                _steps = len(_xrd_count)
                _right_adj = np.sum(_xrd_count[int(_steps - 5):_steps]) / 5
                _xrd_adj = np.linspace(_left_adj, _right_adj, _steps)

                # decrease noise from lammps
                _lammps_adj = max(_xrd_count) * (1 - np.exp(1 / self.angle))

                _xrd_count = _xrd_count - _xrd_adj + _lammps_adj
                _xrd_count = [0 if i < 0 else i for i in _xrd_count]

                _xrd_consum = np.nansum(_xrd_count)

                # make into a pdf
                self.xrd_contot = _xrd_count / _xrd_consum
                self.xrd_max = self.xrd_contot.max() * 1.1
                self.angle_min = self.angle.min()
                self.angle_max = self.angle.max()
                self.newrun = 0
                self.plotwin.update_plot(self.angle, self.xrd_contot)
                # need to update axis values before things are compared against it
                self.plotwin.update_axis()
                CurveFit.fcurvefit(self, self.angle, self.xrd_contot)
                self.parent().statusBar.showMessage(_tail + ' successfully imported')
            else:
                self.parent().statusBar.showMessage(
                    'Incorrect file configuration likely. Please double check LAMMPS output to ensure single timestep')
        except AttributeError:
            self.parent().statusBar.showMessage('No Data File Selected')
            if _iError == 1:
                self.parent().statusBar.showMessage('Incorrect data file selected. Please check LAMMPS/WAXD match')
            elif _iError == 2:
                self.parent().statusBar.showMessage('Incorrect data file selected. Possibly selected save file instead of data?')

    elif input_type == 'WAXD':
        try:
            _xrd2theta = _data.XRD2T.values.tolist()
            _xrd_count = _data.XRDInt.values.tolist()

            if np.max(_xrd2theta) < 180:
                AC = [(i, j) for (i, j) in zip(_xrd2theta, _xrd_count) if i >= 5]
                _xrd2theta, _xrd_count = zip(*AC)
                self.angle = np.array(_xrd2theta)
                _xrd_count = np.array(_xrd_count)

                _left_adj = np.sum(_xrd_count[0:5]) / 5
                _steps = len(_xrd_count)
                _right_adj = np.sum(_xrd_count[int(_steps - 5):_steps]) / 5
                _xrd_adj = np.linspace(_left_adj, _right_adj, _steps)
                _xrd_count = np.absolute(_xrd_count - _xrd_adj)

                _xrd_consum = np.nansum(_xrd_count)

                # make into a pdf
                self.xrd_contot = _xrd_count / _xrd_consum
                self.xrd_max = self.xrd_contot.max() * 1.1
                self.angle_min = self.angle.min()
                self.angle_max = self.angle.max()
                self.newrun = 0
                self.plotwin.update_plot(self.angle, self.xrd_contot)
                self.plotwin.update_axis()
                CurveFit.fcurvefit(self, self.angle, self.xrd_contot)
                self.parent().statusBar.showMessage(_tail + ' successfully imported')
            else:
                # binning in LAMMPS will cause overflow error when it gets interpreted as the angle
                self.parent().statusBar.showMessage('Incorrect data file selected. LAMMPS file loaded as WAXD')

        except AttributeError:
            self.parent().statusBar.showMessage('No Data File Selected')
            if _iError == 1:
                self.parent().statusBar.showMessage('Incorrect data file selected. Please check LAMMPS/WAXD match')
            elif _iError == 2:
                self.parent().statusBar.showMessage('Incorrect data file selected. Possibly selected save file instead of data?')

    elif input_type == 'Ref':
        try:
            _AC = [(i, j) for (i, j) in zip(self.angle, _xrd_count) if i >= 5]
            _xrd2theta, _xrd_count = zip(*_AC)
            self.angle = np.array(_xrd2theta)
            _xrd_count = np.array(_xrd_count)

            # decrease noise from lammps
            _lammps_adj = max(_xrd_count) * (1 - np.exp(1 / self.angle))

            _xrd_count = _xrd_count + _lammps_adj
            _xrd_count = [0 if i < 0 else i for i in _xrd_count]

            _xrd_consum = np.nansum(_xrd_count)
            # make into a pdf
            self.xrd_contot = _xrd_count / _xrd_consum
            self.xrd_max = self.xrd_contot.max() * 1.1
            self.angle_min = self.angle.min()
            self.angle_max = self.angle.max()
            self.newrun = 0
            self.plotwin.update_plot(self.angle, self.xrd_contot)
            self.plotwin.update_axis()
        except AttributeError:
            self.parent().statusBar.showMessage('Reference Data Error')

    else:
        print('No Data File Selected')
