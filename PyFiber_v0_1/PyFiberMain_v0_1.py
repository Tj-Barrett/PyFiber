# Tj Barrett
# Minus Lab, Northeastern University
# external
import sys

import numpy as np
from PySide6.QtWidgets import QStatusBar, QVBoxLayout, QMenuBar, QHBoxLayout, QCheckBox, QApplication, QLineEdit, QTextEdit
from PySide6.QtGui import QDoubleValidator

# classes
from src.PCBragg import *
from src.PCWindow import *
from src.PCAxis import *

# functions
from src.PCfgetfile import *
from src.PCfconfig import *


# -------------------------------------------------------------------------
# Application
# -------------------------------------------------------------------------
class PCwindow(QMainWindow):
    def __init__(self, parent=None):
        super(PCwindow, self).__init__(parent)
        # ------------------------------------------
        # Main Widget
        # ------------------------------------------
        self.MainWindow = self
        self.setWindowTitle('pyFiber')

        # ini file
        self.destination = os.path.dirname(os.path.realpath(__file__))
        _config = configparser.ConfigParser()
        _config.read('src/PCconfig.ini')

        # primary screen geometry
        _available_geometry = QApplication.primaryScreen().size()
        _i_xpos, _i_ypos, _i_width, _i_height = getinitconfig(self, 'src/PCconfig.ini', _available_geometry)

        # overall window geometry
        self.setGeometry(_i_xpos, _i_ypos, _i_width, _i_height)

        # clear unneeded local variables
        del _i_xpos, _i_ypos, _i_width, _i_height, _available_geometry

        self.mainwidget = PercentCrystallinity(self)
        self.MainWindow.setCentralWidget(self.mainwidget)
        self.MainWindow.setMenuBar(self.mainwidget.menubar)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Ready')

    # On resizing, snap handles to new location. Resizing the frame here gets overridden by the paint event
    def resizeEvent(self, e):
        QMainWindow.resizeEvent(self, e)
        self.mainwidget.plotwin.update_handles()
        self.mainwidget.plotwin.update_q_handles()
        self.mainwidget.plotwin.update()


class PercentCrystallinity(QWidget):
    def __init__(self, parent=None):
        super(PercentCrystallinity, self).__init__(parent)
        # allows change of main windows colors
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        # init variables
        self.openname = ''
        self.typefile = ''
        self.plotwin = ''

        # ------------------------------------------
        # Default Settings
        # ------------------------------------------
        # starting directory
        self.destination = os.path.dirname(os.path.realpath(__file__))

        # Read config file
        _available_geometry = QApplication.primaryScreen().size()
        getconfig(self, 'src/PCconfig.ini',_available_geometry)

        _names = ['XRDBin', 'XRDCoord', 'XRDCount', 'XRDCountTot', 'Extra']
        _ref = pd.read_csv(self.reference,
                           header=3,
                           names=_names,
                           sep=" ")
        self.angle = np.array(_ref.XRDBin)
        self.reference_count = np.array(_ref.XRDCount)
        self.newrun = 1

        # these are initial values for the plot
        self.xrd_max = 0.02

        # ------------------------------------------
        # Init Plot
        # ------------------------------------------
        _layout = QVBoxLayout(self)
        self.setLayout(_layout)
        self.menubar = QMenuBar(self)
        self.menubar.setMinimumWidth(self.width())
        self.menubar.setNativeMenuBar(False)

        # ------------------------------------------
        # File
        # ------------------------------------------
        _file = self.menubar.addMenu('File')
        _new = _file.addAction('New', self.newstate)
        _open = _file.addAction('Open', self.loadstate)
        _save = _file.addAction('Save', self.savestate)
        _print = _file.addAction('Print', self.print)

        # ------------------------------------------
        # Preferences
        # ------------------------------------------
        _pref = self.menubar.addMenu('Preferences')
        # Axis
        self.palette = ThemeSelect()
        _axis = _pref.addMenu('Axis')
        _axis_group = QActionGroup(self)
        _axis_group.setExclusive(True)
        self.axisauto = _axis_group.addAction('Auto')
        _axis.addAction(self.axisauto)
        self.axismanual = _axis_group.addAction('Manual')
        _axis.addAction(self.axismanual)
        self.axisauto.setCheckable(True)
        self.axisauto.setChecked(True)
        self.axisauto.triggered.connect(lambda: self.axis_clear())
        self.axismanual.setCheckable(True)
        self.axismanual.triggered.connect(self.axis_dialog)

        # Backround Theme
        self.palette = ThemeSelect()
        _theme = _pref.addMenu('Theme')
        _theme_group = QActionGroup(self)
        _theme_group.setExclusive(True)
        self.dark = _theme_group.addAction('Dark Theme')
        _theme.addAction(self.dark)
        self.light = _theme_group.addAction('Light Theme')
        _theme.addAction(self.light)
        self.dark.setCheckable(True)
        self.dark.triggered.connect(self.palette.dark)
        self.dark.triggered.connect(self.theme_update)
        self.light.setCheckable(True)
        self.light.triggered.connect(self.palette.light)
        self.light.triggered.connect(self.theme_update)
        if self.bTheme == 0:
            self.dark.setChecked(True)
            self.palette.dark()
        else:
            self.light.setChecked(True)
            self.palette.light()

        # Show Contributors
        self.contributors = _pref.addAction('Show Contributing Curves')
        self.contributors.setCheckable(True)
        self.contributors.setChecked(self.b_contributors)

        # Show Cursor
        self.showcursor = _pref.addAction('Show Cursor')
        self.showcursor.setCheckable(True)
        self.showcursor.setChecked(self.b_cursor)
        # ------------------------------------------
        # Braggs
        # ------------------------------------------
        _Braggs = self.menubar.addMenu('Bragg')
        _BraggsCalc = _Braggs.addAction('Calculator')
        _BraggsCalc.triggered.connect(self.bragg_dialog)

        _BraggsManual = _Braggs.addAction('Manual Entry')
        _BraggsManual.triggered.connect(lambda: self.bragg_dialog(b_bragg_type=1))

        _BraggsClear = _Braggs.addAction('Clear')
        _BraggsClear.triggered.connect(lambda: self.bragg_clear())

        # ------------------------------------------
        # Import
        # ------------------------------------------
        _import = self.menubar.addMenu('Import')
        _import_lammps = _import.addAction('LAMMPS')
        _import_lammps.triggered.connect(lambda: getfile(self, input_type='LAMMPS'))
        _import_waxd = _import.addAction('WAXD')
        _import_waxd.triggered.connect(lambda: getfile(self, input_type='WAXD'))
        _import_ref = _import.addAction('Reference')
        _import_ref.triggered.connect(lambda: getfile(self, input_type='Ref', filename=self.reference))

        # crystallinity amount title
        _crystal_sub_layout = QHBoxLayout()
        self.crystal_label = QLabel()
        self.crystal_label.setText('Percent Crystallinity: 0.0%')
        self.crystal_label.setAlignment(Qt.AlignCenter)
        self.crystal_label.setFixedHeight(20)
        _crystal_sub_layout.addWidget(self.crystal_label)

        _layout.addLayout(_crystal_sub_layout)

        # Setting up plot
        self.plotwin = PlotWin(self)
        _layout.addWidget(self.plotwin)

        # ------------------------------------------
        # Node Controls
        # ------------------------------------------
        _controls_layout = QHBoxLayout()
        self.label_frame = QFrame()

        # labels
        _labels_layout = QVBoxLayout()
        _labels_layout.addWidget(QLabel('Curve Active'))
        _labels_layout.addWidget(QLabel('Morphology'))
        _labels_layout.addWidget(QLabel('Shift'))
        _labels_layout.addWidget(QLabel('Height'))
        _labels_layout.addWidget(QLabel('Width'))
        _labels_layout.addWidget(QLabel('Skew'))

        _controls_layout.addWidget(self.label_frame)

        # boxes
        self.nodes = []
        self.active_node = []
        self.node_dict = []
        # defaults

        # moved to config
        # self.total_handles = 8

        # _deffs = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0]
        _deffs = np.linspace(self.plotwin.xaxis.min+10.0, self.plotwin.xaxis.max -10.0, self.i_total_nodes)
        _mid = round((self.plotwin.laxis.max - self.plotwin.laxis.min) / 2, 2)
        for i in range(0, self.i_total_nodes):
            # color box around inputs
            _node_frame = ActiveNode(index=i)

            _checkbox = QCheckBox('On/Off')
            _crystal = QCheckBox('Crystalline')

            # shift textbox
            _shift_txt = QLineEdit(str(round(_deffs[i],0)))
            _shift_valid = QDoubleValidator()
            _shift_valid.setBottom(self.plotwin.xaxis.min)
            _shift_valid.setTop(self.plotwin.xaxis.max)
            _shift_valid.setDecimals(5)
            _shift_txt.setValidator(_shift_valid)

            # height textbox
            _height_txt = QLineEdit(str(_mid))
            _height_valid = QDoubleValidator()
            _height_valid.setBottom(self.plotwin.laxis.min)
            _height_valid.setTop(self.plotwin.laxis.max)
            _height_valid.setDecimals(5)
            _height_txt.setValidator(_height_valid)

            # Q textbod
            _q_txt = QLineEdit('5.0')
            _q_valid = QDoubleValidator()
            _q_valid.setBottom(0.1)
            _q_valid.setTop(25)
            _q_valid.setDecimals(5)
            _q_txt.setValidator(_q_valid)

            # Skew textbod
            _skew_txt = QLineEdit('0.0')
            _skew_valid = QDoubleValidator()
            _skew_valid.setBottom(-2.5)
            _skew_valid.setTop(2.5)
            _skew_valid.setDecimals(5)
            _skew_txt.setValidator(_skew_valid)

            # nodeLayout call
            # calls PCWindow
            _node = NodeLayout(i, self)
            _node.add_controls(_checkbox,
                               _crystal,
                               _shift_txt,
                               _height_txt,
                               _q_txt,
                               _skew_txt)
            _node.set_controls_enabled(False)
            self.nodes.append(_node)
            _node_frame.setLayout(_node)

            self.active_node.append(_node_frame)
            _controls_layout.addWidget(_node_frame)
            _controls_layout.setAlignment(Qt.AlignBottom)

            _node_value = NodeValues()
            _node_value.set_values(round(_deffs[i],0),
                                   Tools.convert_height(_mid,
                                                        self.plotwin.raxis,
                                                        self.plotwin.laxis),
                                   5.0,
                                   0.0)
            self.node_dict.append(_node_value)

            _node.ctrls[1].clicked.connect(self.on_crystal_toggle)
            _node.enabled.connect(self.on_enable_change)
            _node.updated.connect(self.parameter_change)

        self.label_frame.setLayout(_labels_layout)
        _layout.addLayout(_controls_layout)

        # Set Defaults after everything is initialized
        self.theme_update()

    # ------------------------------------------
    # AxisDialog
    # ------------------------------------------
    def axis_dialog(self):
        _dialog = AxisWin(self)
        self.parent().statusBar.showMessage('Manual Axis Window Opened')
        _dialog.show()

    def axis_clear(self):
        self.angle_min = self.angle.min()
        self.angle_max = self.angle.max()

        # check this try except, cant remember why its here
        try:
            self.xrd_max = self.xrd_contot.max() * 1.1
        except AttributeError:
            self.xrd_max = 0.20
        self.parent().statusBar.showMessage('Auto Axis Restored')

    # ------------------------------------------
    # BraggDialog
    # ------------------------------------------
    def bragg_dialog(self, b_bragg_type):
        if b_bragg_type == 0:
            _dialog = BraggCalc(self)
            self.parent().statusBar.showMessage('Bragg Calculator Window Opened')
        else:
            _dialog = BraggManual(self)
            self.parent().statusBar.showMessage('Bragg Manual Window Opened')
        _dialog.show()

    def bragg_clear(self):
        _dialog = BraggClear(self)
        self.parent().statusBar.showMessage('Bragg Angles Cleared')

    # ------------------------------------------
    # Saving and exporting
    # ------------------------------------------
    def newstate(self):
        self.plotwin.update_axis()

        _deffs = np.linspace(self.plotwin.xaxis.min+10.0, self.plotwin.xaxis.max -10.0, self.i_total_nodes)
        _mid = round((self.xrd_max - 0) / 2, 2)
        for i in range(0, len(self.node_dict)):
            # values
            self.node_dict[i].shift = round(_deffs[i],0)
            self.node_dict[i].height = Tools.convert_height(_mid, to_axis=self.plotwin.raxis,
                                                            from_axis=self.plotwin.laxis)
            self.node_dict[i].q = 2.0
            self.node_dict[i].skew = 0.0

        self.plotwin.update_plot(self.angle, [])
        self.plotwin.update_gmm_curves()
        self.plotwin.update_handles(new=True)
        self.plotwin.update_q_handles(new=True)

        for i in range(0, len(self.node_dict)):
            self.nodes[i].ctrls[0].setChecked(False)
            self.nodes[i].ctrls[1].setChecked(False)
        self.plotwin.update_handles()
        self.parent().statusBar.showMessage('New selected, window reset')

    def print(self):
        if self.dark.isChecked():
            _orig_dark = True
        else:
            _orig_light = True

        self.light.setChecked(True)
        self.theme_update()

        ThemeSelect.printlight(self, widget=self)
        ThemeSelect.printlight(self, frame=self.label_frame)
        ThemeSelect.printlight(self, crystal=self.crystal_label)
        ThemeSelect.printlight(self, menu=self.menubar)
        self.plotwin.curve_xrd.pen = QPen(QColor(self.palette.light_text))
        self.plotwin.curve_xrd.pen.setWidth(2)

        self.plotwin.focused = -2
        self.plotwin.update_handles()

        _figure = self.plotwin
        _figure.setStyleSheet('QFrame {background-color: #FFFFFF}')
        _figure.setStyleSheet('QFrame {border: 2px solid black}')

        _img = QWidget.grab(_figure)
        _filename = QFileDialog.getSaveFileName(self,
                                                'Print File',
                                                self.destination,
                                                'Images (*.jpg *.jpeg *.png)',
                                                options=QFileDialog.DontUseNativeDialog)
        _base = os.path.basename(_filename[0])
        if len(_base) > 0:
            _ext = os.path.splitext(_base)[-1].lower()
            _head, tail = os.path.split(_filename[0])
            # if image file
            if _ext in ['.png', '.jpg', '.jpeg']:
                _img.save('/'.join([_head, _base]))
                self.parent().statusBar.showMessage(''.join(['Printed: ', _base]))
            else:  # if no extension, just make sure it prints. misspelling of ext should still pass
                _img.save(''.join(['/'.join([_head, _base]), '.png']))
                self.parent().statusBar.showMessage(''.join(['Printed: ', _base, '.png']))

            self.plotwin.focused = -1
            self.plotwin.update_handles()
            if _orig_dark:
                self.dark.setChecked(True)
                self.theme_update()
        else:
            self.plotwin.focused = -1
            self.plotwin.update_handles()
            if _orig_dark:
                self.dark.setChecked(True)
                self.theme_update()
            self.parent().statusBar.showMessage('No Print Performed')

    def savestate(self):
        _filename = QFileDialog.getSaveFileName(self,
                                                'Save File',
                                                self.destination,
                                                'State Values (*.csv)',
                                                options=QFileDialog.DontUseNativeDialog)
        _basefile = os.path.basename(_filename[0])
        _base = os.path.splitext(_basefile)[0]
        _file = ''.join([_base, '.csv'])

        if len(_base) > 0:
            _state = []
            for i in range(0, len(self.nodes)):
                _state.append([self.nodes[i].ctrls[0].isChecked(),
                               self.nodes[i].ctrls[1].isChecked(),
                               self.nodes[i].ctrls[2].text(),
                               round(self.node_dict[i].height, 5),
                               self.nodes[i].ctrls[4].text(),
                               self.nodes[i].ctrls[5].text()])
            _state = pd.DataFrame(_state)
            # filename
            _openfile = pd.DataFrame([[self.openname]])
            _openfile.to_csv(_file,
                             header=['Filename'],
                             index=False)
            # type
            _typefile = pd.DataFrame([[self.typefile]])
            _typefile.to_csv(_file,
                             mode='a',
                             header=['Type'],
                             index=False)
            # data
            _header = ['Node', 'Crystal', 'Shift', 'Height', 'Q', 'Skew']
            _state.to_csv(_file,
                          mode='a',
                          header=_header,
                          sep=',',
                          index=False)
            self.parent().statusBar.showMessage(''.join(['Saved ', _file]))
        else:
            self.parent().statusBar.showMessage('No Save File Made')

    def loadstate(self):
        _filename = QFileDialog.getOpenFileName(self,
                                                'Open State File',
                                                self.destination,
                                                'State Values (*.csv)',
                                                options=QFileDialog.DontUseNativeDialog)
        _file = os.path.basename(_filename[0])

        if len(_file) > 0:

            # Directory switch maybe at some point
            # _path = os.path.split(_filename[0])
            # _path = _path[0]

            # load data
            _loadthis = pd.read_csv(_file, nrows=1)

            # type
            _type = pd.read_csv(_file,
                                nrows=1,
                                skiprows=2)
            try:
                getfile(self,
                        input_type=_type.Type[0],
                        filename=_loadthis.Filename[0])
                self.openname = _loadthis.Filename[0]
                # data
                _data = pd.read_csv(_file, header=4)
                for i in range(0, len(self.nodes)):
                    # values
                    if _data.Node[i]:
                        self.nodes[i].ctrls[0].setChecked(True)
                    else:
                        self.nodes[i].ctrls[0].setChecked(False)

                    if _data.Crystal[i]:
                        self.nodes[i].ctrls[1].setChecked(True)
                    else:
                        self.nodes[i].ctrls[1].setChecked(False)
                    # pandas has methods called skew and shift, so just made ours capitals
                    self.node_dict[i].shift = _data.Shift[i]
                    self.node_dict[i].height = _data.Height[i]
                    self.node_dict[i].q = _data.Q[i]
                    self.node_dict[i].skew = _data.Skew[i]

                    # labels
                    self.nodes[i].ctrls[2].setText(str(round(_data.Shift[i], 5)))
                    self.nodes[i].ctrls[3].setText(str(round(Tools.convert_height(_data.Height[i],
                                                                                  self.plotwin.laxis,
                                                                                  self.plotwin.raxis), 5)))
                    self.nodes[i].ctrls[4].setText(str(round(_data.Q[i], 5)))
                    self.nodes[i].ctrls[5].setText(str(round(_data.Skew[i], 5)))

                self.plotwin.update_handles()
                self.plotwin.update_q_handles()
                self.plotwin.update()
                self.parent().statusBar.showMessage(''.join(['Loaded ', _file]))
            except FileNotFoundError:
                # get file error if incorrect file selected
                self.parent().statusBar.showMessage('Non-save file selected')
            except KeyError:
                # get file error if config file has more nodes than save, will still load if config has less nodes
                self.parent().statusBar.showMessage('Save - config file node amount mismatch. Please resave to current configuration.')
        else:
            self.parent().statusBar.showMessage('No Data File Selected')

    # ------------------------------------------
    # Control responses
    # ------------------------------------------
    def on_crystal_toggle(self):
        self.plotwin.update_crystallinity()

    def on_enable_change(self, index):
        if self.nodes[index].ctrls[0].isChecked():
            self.nodes[index].set_controls_enabled(True)
        else:
            self.nodes[index].set_controls_enabled(False)

        self.plotwin.update_handles()
        self.plotwin.update_q_handles()
        self.plotwin.update()
        self.plotwin.update_crystallinity()

    def parameter_change(self, index):
        self.node_dict[index].shift = self.nodes[index].shift
        self.node_dict[index].height = Tools.convert_height(self.nodes[index].height,
                                                            self.plotwin.raxis,
                                                            self.plotwin.laxis)
        self.node_dict[index].q = self.nodes[index].q
        self.node_dict[index].skew = self.nodes[index].skew
        self.plotwin.update_handles()
        self.plotwin.update_q_handles()
        self.plotwin.update()
        self.plotwin.update_crystallinity()

    def update_controls(self):
        self.plotwin.update()
        self.plotwin.update_crystallinity()

    def theme_update(self):
        if self.light.isChecked():
            ThemeSelect.light(self, widget=self)
            ThemeSelect.light(self, frame=self.label_frame)
            ThemeSelect.light(self, crystal=self.crystal_label)
            ThemeSelect.light(self, menu=self.menubar)
            self.plotwin.curve_xrd.pen = QPen(QColor(self.palette.light_text))
            self.plotwin.curve_xrd.pen.setWidth(2)

        if self.dark.isChecked():
            ThemeSelect.dark(self, widget=self)
            ThemeSelect.dark(self, frame=self.label_frame)
            ThemeSelect.dark(self, crystal=self.crystal_label)
            ThemeSelect.dark(self, menu=self.menubar)
            self.plotwin.curve_xrd.pen = QPen(QColor(self.palette.dark_text))
            self.plotwin.curve_xrd.pen.setWidth(2)


# -------------------------------------------------------------------------
# Application
# -------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PCwindow()
    window.show()

    sys.exit(app.exec())
