# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QFrame, QApplication, QGridLayout
from PySide6.QtGui import QPen, QBrush, QPainter, QPolygon, QPalette, QLinearGradient, QPainterPath
from PySide6.QtCore import QRectF, QPointF, Signal, Qt
from src.PCTools import *
from src.PCThemes import *

from time import sleep, time

# ------------------------------------------
# Name axis for call
# ------------------------------------------
class Axis(object):
    def __init__(self, axis_type, axis_min, axis_max):
        self.type = axis_type
        self.min = axis_min
        self.max = axis_max


# ------------------------------------------
# Main Plot Window
# ------------------------------------------
class PlotWin(QFrame):
    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.setFrameStyle(QFrame.Box)
        self.setAutoFillBackground(True)

        self.setMinimumHeight(round(0.75 * self.parent().height()))
        self.show()

        self.xaxis = Axis('bottom', self.parent().angle_min, self.parent().angle_max)
        self.qaxis = Axis('Top', 0.25, 50)
        self.skewaxis = Axis('right', -25, 25)
        self.laxis = Axis('left', 0, self.parent().xrd_max)
        self.raxis = Axis('right', 0, 1)
        self.rect = QRectF()

        self.calltype = []
        # xrd
        _pen_xrd = QPen(QColor(self.parent().palette.light_text))
        _pen_xrd.setWidth(2)
        self.curve_xrd = PlotCurve(_pen_xrd)

        # gmm
        _colour_gmm = QColor('#ef5350')
        _colour_gmm.setAlpha(255)
        _pen_gmm = QPen(_colour_gmm)
        _pen_gmm.setWidth(2)
        self.curve_gmm = PlotCurve(_pen_gmm)

        # bragg
        self.bragg = CPlotBragg(_pen_gmm)

        # area under curve
        # these colors dont matter, get overwritten. Ok as reference though
        _colour_line = QColor('#ef5350')
        _pen3 = QPen(_colour_line)
        _pen3.setWidth(1)
        self.area = PlotArea(_pen3, QBrush(QColor(255, 255, 255, 50)))

        # Handle Directory
        self.handles = [QPoint()] * self.parent().i_total_nodes
        self.handles_qr = [QPoint()] * self.parent().i_total_nodes
        self.handles_ql = [QPoint()] * self.parent().i_total_nodes
        # Booleans
        self.b_dragged = False
        self.b_handle = False
        self.b_handle_r = False
        self.b_handle_l = False
        # Designates Active Node
        self.focused = -1

        # Frame time
        self.frametime = 1.0 / np.float(self.parent().i_fps)

    # ------------------------------------------
    # Control Nodes/ Handles
    # ------------------------------------------
    def draw_handles(self, qp):
        _active = []
        # Font colors
        _pen = []
        _pen_q = []
        _textpen = []

        for i, h in enumerate(self.handles):
            # node controls
            _active = self.parent().active_node[i]
            # all node control colors
            if self.parent().light.isChecked():
                # labels
                ThemeSelect.light(self, frame=self.parent().label_frame)
                # boxes
                ThemeSelect.light(self, widget=_active)
                if self.focused == i:
                    ThemeSelect.light(self, active=self.focused, textpen=self.parent().nodes[i])
                else:
                    ThemeSelect.light(self, textpen=self.parent().nodes[i])

            elif self.parent().dark.isChecked():
                # labels
                ThemeSelect.dark(self, frame=self.parent().label_frame)
                # boxes
                ThemeSelect.dark(self, widget=_active)
                if self.focused == i:
                    ThemeSelect.dark(self, active=self.focused, textpen=self.parent().nodes[i])
                else:
                    ThemeSelect.dark(self, textpen=self.parent().nodes[i])

            if h is not None:
                if self.focused == i:
                    # node
                    m = 1
                    # node control box
                    _active = self.parent().active_node[self.focused]
                    _active.setFrameShape(QFrame.Box)
                    # hightlight box
                    if self.parent().light.isChecked():
                        ThemeSelect.light(self, highlight=_active)
                    if self.parent().dark.isChecked():
                        ThemeSelect.dark(self, highlight=_active)

                    _active.setFrameShadow(QFrame.Plain)
                    _active.setLineWidth(0)
                    _active.show()

                else:
                    # node
                    m = 1.4

                # main node
                _pen = QPen(QColor(self.parent().palette.colour[i]))
                _pen.setWidth(2)
                _textpen = QPen(QColor(self.parent().palette.dark_primary))
                if self.parent().light.isChecked():
                    _textpen = QPen(QColor(self.parent().palette.dark_primary))
                    if i == 7:
                        _textpen = QPen(QColor(self.parent().palette.light_primary))
                elif self.parent().dark.isChecked():
                    _textpen = QPen(QColor(self.parent().palette.dark_primary))

                _textpen.setWidth(2)
                # Node Circle
                qp.setPen(_pen)
                qp.setBrush(QBrush(QColor(self.parent().palette.colour[i])))
                qp.drawEllipse(h, 13 / m, 13 / m)
                # node label
                qp.setPen(_textpen)
                if i < 9:
                    qp.drawText(QPoint(h.x() - 4.0, h.y() + 5.0), str(i + 1))
                else:
                    qp.drawText(QPoint(h.x() - 8.5, h.y() + 5.0), str(i + 1))

                # drawing q nodes
                # q node inside
                _pen_q = []
                if self.parent().light.isChecked():
                    _pen_q = QPen(QColor(self.parent().palette.light_ticks))
                elif self.parent().dark.isChecked():
                    _pen_q = QPen(QColor(self.parent().palette.dark_ticks))
                _pen_q.setWidth(2)
                qp.setPen(_pen_q)

                # q node outside
                if self.focused == i:
                    if self.parent().light.isChecked():
                        qp.setBrush(QBrush(QColor(self.parent().palette.colour[i])))
                    if self.parent().dark.isChecked():
                        qp.setBrush(QBrush(QColor(self.parent().palette.colour[i])))
                    qp.drawEllipse(self.handles_qr[i], 4 / m, 4 / m)
                    qp.drawEllipse(self.handles_ql[i], 4 / m, 4 / m)

    # ------------------------------------------
    # Graph Tickmarks
    # ------------------------------------------
    def draw_ticks(self, qp, axis):
        _grid_major_pen = []
        _grid_minor_pen = []
        _tick_pen = []

        if self.parent().light.isChecked():
            ThemeSelect.light(self, plot=self)
            _tick_pen = QPen(QColor(self.parent().palette.light_ticks))
            _grid_major_pen = QPen(QColor(self.parent().palette.light_ticks))
            _grid_minor_pen = QPen(QColor(self.parent().palette.light_ticks))
        elif self.parent().dark.isChecked():
            ThemeSelect.dark(self, plot=self)
            _tick_pen = QPen(QColor(self.parent().palette.dark_ticks))
            _grid_major_pen = QPen(QColor(self.parent().palette.dark_ticks))
            _grid_minor_pen = QPen(QColor(self.parent().palette.dark_ticks))

        qp.setPen(_tick_pen)
        _grid_major_pen.setStyle(Qt.DashLine)
        _grid_major_pen.setWidthF(0.5)
        _grid_minor_pen.setStyle(Qt.DashLine)
        _grid_minor_pen.setWidthF(0.25)
        _majors = []
        _minors = []
        _ticklen = self.parent().i_major_tick
        # vertical offset from bottom
        _boffset = 4
        # r/l offset from major axis
        _roffset = -2
        _xaxis = self.xaxis
        _bgap = self.height() - self.rect.height()

        _ticks = []
        i = 0
        if self.parent().bStartAtMin:
            while self.parent().angle_min + i * self.parent().i_major_tick < self.parent().angle_max +1 :
                _ticks.append( self.parent().angle_min + i * self.parent().i_major_tick )
                i = i+1
        else:
            while i * self.parent().i_major_tick < self.parent().angle_max +1 :
                _ticks.append( i * self.parent().i_major_tick )
                i = i+1

        if axis.type == 'bottom':
            qp.drawText(QPointF(self.width() - self.parent().angle_max, self.height() - _boffset), '[Degree]')

            _majors = _ticks
            for i in range(min(_majors), max(_majors), self.parent().i_minor_tick):
                _minors.append(i)

            # bottom x axis
            qp.drawLine(self.rect.bottomLeft(), self.rect.bottomRight())

            for tick in _majors:
                qp.setPen(_tick_pen)
                qp.drawLine(Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            self.height() - _bgap,
                            Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            self.height() - _bgap - _ticklen)
                if tick != max(_majors):
                    qp.drawText(Tools.to_pixel_coords(self.width(),
                                                      self.height(),
                                                      tick,
                                                      _xaxis) - _bgap - _roffset,
                                self.height() - _boffset,
                                str(tick))

                qp.setPen(_grid_major_pen)
                qp.drawLine(Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick, _xaxis),
                            self.height() - _bgap - _ticklen,
                            Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            0)

            for tick in _minors:
                qp.setPen(_tick_pen)
                qp.drawLine(Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            self.height() - _bgap,
                            Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            self.height() - _bgap - _ticklen * 0.5)

                qp.setPen(_grid_minor_pen)
                qp.drawLine(Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            self.height() - _bgap - _ticklen * 0.5,
                            Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  tick,
                                                  _xaxis),
                            0)

        elif axis.type == 'left':
            _n = 11
            _majors = np.linspace(axis.min, axis.max, _n)
            qp.drawLine(0, 0, 0, self.height() - _bgap)
            qp.drawText(_ticklen, 15, '[Intensity]')
            for tick in _majors:
                qp.setPen(_tick_pen)
                _yp = Tools.to_pixel_coords(self.width(),
                                            self.height(),
                                            0,
                                            _xaxis,
                                            tick,
                                            self.laxis).y()
                qp.drawLine(0, _yp, _ticklen * 0.5, _yp)
                if tick != min(_majors) and tick != max(_majors):
                    qp.drawText(_ticklen, _yp + 4, str(tick)[0:5])

                qp.setPen(_grid_major_pen)
                qp.drawLine(_ticklen * 0.5, _yp, self.width(), _yp)

    # ------------------------------------------
    # Interaction Events
    # ------------------------------------------
    def mouseMoveEvent(self, e):
        #loc
        _x = []
        _y = []
        _pos = []
        _X = []

        # nodes
        _shift = []
        _height = []
        _q = []
        _skew = []

        if self.calltype == 'left':
            if self.b_dragged:
                if self.b_handle:
                    _pos, i = e.pos(), self.focused
                    _shift, _height = Tools.from_pixel_coords(self.width(),
                                                            self.height(),
                                                            _pos,
                                                            self.xaxis,
                                                            self.raxis)
                    self.parent().node_dict[i].shift = _shift
                    self.parent().node_dict[i].height = _height

                # q handles, locked to move in only x axis
                elif self.b_handle_r:
                    _x, _y, i = e.pos().x(), e.pos().y(), self.focused
                    if _x - self.handles[i].x() > 0:
                        _q, _height = Tools.from_pixel_coords(self.width(),
                                                            self.height(),
                                                            QPoint(_x - self.handles[i].x(), _y),
                                                            self.qaxis,
                                                            self.raxis)
                        self.parent().node_dict[i].q = _q

                elif self.b_handle_l:
                    _x, _y, i = e.pos().x(), e.pos().y(), self.focused
                    if self.handles[i].x() - _x > 0:
                        _q, _height = Tools.from_pixel_coords(self.width(),
                                                            self.height(),
                                                            QPoint(self.handles[i].x() - _x, _y),
                                                            self.qaxis,
                                                            self.raxis)
                        self.parent().node_dict[i].q = _q

        elif self.calltype == 'right':
            if self.b_dragged:
                # skewness handles, locked to only y axis value snapping bugs usually related here, event position (
                # ie cursor position) will snap to different location
                if self.b_handle_r:
                    _x, _y, i = e.pos().x(), e.pos().y(), self.focused
                    if _x - self.handles[i].x() > 0:
                        _X, _skew = Tools.from_pixel_coords(self.width(),
                                                          self.height(),
                                                          QPoint(_x, _y),
                                                          self.xaxis,
                                                          self.skewaxis)
                        # artificial axis enforcement
                        if _skew > 5.0:
                            _skew = 5.0
                        elif _skew < -5.0:
                            _skew = -5.0
                        self.parent().node_dict[i].skew = _skew / 10.0

                elif self.b_handle_l:
                    _x, _y, i = e.pos().x(), e.pos().y(), self.focused
                    if self.handles[i].x() - _x > 0:
                        _X, _skew = Tools.from_pixel_coords(self.width(),
                                                          self.height(),
                                                          QPoint(_x, -_y),
                                                          self.xaxis,
                                                          self.skewaxis)
                        # artificial axis enforcement
                        if _skew > 5.0:
                            _skew = 5.0
                        elif _skew < -5.0:
                            _skew = -5.0
                        self.parent().node_dict[i].skew = _skew / 10.0

        # modifies curves
        self.update_handles()
        self.update_q_handles()
        self.update()

    def mousePressEvent(self, e):
        # main node x,y and q node x
        if e.button() == Qt.LeftButton:
            self.calltype = 'left'
        # q node y (skew)
        elif e.button() == Qt.RightButton:
            self.calltype = 'right'

        for i, h in enumerate(self.handles):
            # clicking on main node only
            if h is not None:
                if abs(e.pos().x() - h.x()) <= 10 and abs(e.pos().y() - h.y()) <= 10:
                    self.b_handle = True
                    self.b_dragged = True
                    self.focused = i
                    if not self.parent().showcursor.isChecked():
                        QApplication.setOverrideCursor(Qt.BlankCursor)

            # clicking on q nodes, the 'and ' makes sure you can't click on the invisible q nodes
            if h is not None and self.handles[i] == self.handles[self.focused]:
                # mouse click must be within 10 pixels of center
                if abs(e.pos().x() - self.handles_qr[i].x()) <= 10 and abs(e.pos().y() - self.handles_qr[i].y()) <= 10:
                    self.b_handle_r = True
                    self.b_dragged = True
                    self.focused = i
                    if not self.parent().showcursor.isChecked():
                        QApplication.setOverrideCursor(Qt.BlankCursor)
                # mouse click must be within 10 pixels of center
                elif abs(e.pos().x() - self.handles_ql[i].x()) <= 10 and abs(
                        e.pos().y() - self.handles_ql[i].y()) <= 10:
                    self.b_handle_l = True
                    self.b_dragged = True
                    self.focused = i
                    if not self.parent().showcursor.isChecked():
                        QApplication.setOverrideCursor(Qt.BlankCursor)

    def mousePressEventTab(self, k):
        # clicking on node tab
        for i, h in enumerate(self.handles):
            if h is not None:
                self.b_dragged = False
                self.focused = k
                self.update_handles()
                self.update_q_handles()
                self.update()

    def mouseReleaseEvent(self, e):
        self.b_dragged = False
        QApplication.restoreOverrideCursor()
        if self.b_handle:
            self.cursor().setPos(self.mapToGlobal(self.handles[self.focused]))
            self.b_handle = False
        elif self.b_handle_r:
            self.cursor().setPos(self.mapToGlobal(self.handles_qr[self.focused]))
            self.b_handle_r = False
        elif self.b_handle_l:
            self.cursor().setPos(self.mapToGlobal(self.handles_ql[self.focused]))
            self.b_handle_l = False

    # ------------------------------------------
    # Paint everything in the window
    # ------------------------------------------
    def paintEvent(self, e):
        # simple frame rate limiter
        _start = time()
        try:
            QFrame.paintEvent(self, e)

            self.rect = QRectF(0, 0, self.width(), self.height())
            self.laxis = Axis('left', 0, self.parent().xrd_max)
            self.xaxis = Axis('bottom', self.parent().angle_min, self.parent().angle_max)

            qp = QPainter(self)
            qp.setRenderHint(QPainter.Antialiasing)

            # paint grid
            self.draw_ticks(qp, self.xaxis)
            self.draw_ticks(qp, self.laxis)
            self.draw_ticks(qp, self.raxis)

            # plot xrd curve
            self.plot(qp, self.curve_xrd, self.laxis)

            # paint Bragg
            self.plot_bragg(qp, self.laxis)

            # paint area under chain
            self.update_area()
            self.plot_area(qp, self.area, self.laxis)

            # update crystallinity
            self.update_crystallinity()

            # paint chain response
            self.update_gmm_curves()
            self.plot(qp, self.curve_gmm, self.laxis)
            self.update_gmm_contributors()
            for i in range(len(self.curve_contributors)):
                self.plot(qp, self.curve_contributors[i], self.laxis)

            # paint handles
            self.draw_handles(qp)
            # remove highlight if all empty
            if not self.parent().nodes[self.focused].is_enabled():
                for i, h in enumerate(self.handles):
                    if self.parent().light.isChecked():
                        ThemeSelect.light(self, textpen=self.parent().nodes[i])

                    elif self.parent().dark.isChecked():
                        ThemeSelect.dark(self, textpen=self.parent().nodes[i])

        except AttributeError:
            self.parent().statusBar.showMessage('Paint Error')
            pass

        # normally paint will refresh as fast as it can
        # 0.0133 seconds on 3900x, so 75 fps or so
        # 0.044   seconds with all 8 nodes, plus XRD
        # measure start to end of paint cycle, and sleep until frame time is reached
        # if not, then just go to next frame
        _end = time()
        if (_end-_start) < self.frametime:
            sleep(self.frametime-(_end-_start))

    # ------------------------------------------
    # Plot main curves
    # ------------------------------------------
    def plot(self, qp, curve, yaxis):
        w = self.width()
        h = self.height()
        qp.setPen(curve.pen)
        qp.setBrush(curve.brush)
        poly = QPolygon()
        for x, y in zip(curve.xdata, curve.ydata):
            poly << Tools.to_pixel_coords(w, h, x, self.xaxis, y, yaxis)
        qp.drawPolyline(poly)

    # ------------------------------------------
    # Plot area under active node curve
    # ------------------------------------------
    def plot_area(self, qp, curve, yaxis):
        _w = []
        _h = []
        _areacolor = []
        _colour_line = []

        if self.parent().nodes[self.focused].is_enabled():
            _w = self.width()
            _h = self.height()

            # Area colors
            _areacolor = QColor(QColor(self.parent().palette.colour[self.focused]))
            _areacolor.setAlpha(90)
            qp.setBrush(_areacolor)

            # Line Color
            # this just makes so theres no line
            _colour_line = QColor(0, 0, 0, 0)
            qp.setPen(_colour_line)

            curve.path.moveTo(Tools.to_pixel_coords(_w, _h, 0, self.xaxis, 0, yaxis))
            for _x, _y in zip(curve.xdata, curve.ydata):
                curve.ydata[-1] = 0
                curve.path.lineTo(Tools.to_pixel_coords(_w, _h, _x, self.xaxis, _y, yaxis))

            qp.drawPath(curve.path)
            # Clear does not work in terminal for some reason
            # curve.path.clear()
            curve.path = QPainterPath()

    # ------------------------------------------
    # Plot Bragg Angles
    # ------------------------------------------
    def plot_bragg(self, qp, yaxis):
        _pen_primary = QPen(QColor(255, 0, 0, 150))
        _pen_secondary = QPen(QColor(255, 0, 0, 125))
        _pen_secondary.setStyle(Qt.DashLine)
        qp.setPen(_pen_primary)
        for i in range(0, len(self.bragg.theta1)):
            # prevent overflow error by being outside bounds
            if self.xaxis.min < self.bragg.theta1[i] < self.xaxis.max:
                qp.setPen(_pen_primary)
                qp.drawLine(Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  self.bragg.theta1[i],
                                                  self.xaxis,
                                                  yaxis.min,
                                                  yaxis),
                            Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  self.bragg.theta1[i],
                                                  self.xaxis,
                                                  yaxis.max,
                                                  yaxis))
            if self.xaxis.min < self.bragg.theta2[i] < self.xaxis.max:
                qp.setPen(_pen_secondary)
                qp.drawLine(Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  self.bragg.theta2[i],
                                                  self.xaxis,
                                                  yaxis.min,
                                                  yaxis),
                            Tools.to_pixel_coords(self.width(),
                                                  self.height(),
                                                  self.bragg.theta2[i],
                                                  self.xaxis,
                                                  yaxis.max,
                                                  yaxis))

    # ------------------------------------------
    # Resizing Window
    # ------------------------------------------
    def resizeEvent(self, e):
        QFrame.resizeEvent(self, e)
        # kinda hacky resize but it works
        self.setGeometry(self.x(),
                         self.y(),
                         self.parent().width() - 20,
                         self.parent().height() - 250)
        _gradient = QLinearGradient(QPointF(self.width() / 2, 0),
                                    QPointF(self.width() / 2, self.height()))
        # changes plot color from theme
        if self.parent().light.isChecked():
            ThemeSelect.light(self, gradient=_gradient)
        if self.parent().dark.isChecked():
            ThemeSelect.dark(self, gradient=_gradient)
        _p = self.palette()
        _p.setBrush(QPalette.Window, QBrush(_gradient))
        self.setPalette(_p)
        self.update()

    # ------------------------------------------
    # Crystallinity Calculation
    # ------------------------------------------
    def update_crystallinity(self):
        _cry_area = 0
        _amo_area = 0

        # nodes
        _shift = []
        _height = []
        _q = []
        _skew = []

        # gaussian
        _response = []

        for i in range(0, len(self.parent().nodes)):
            _shift = self.parent().node_dict[i].shift
            _height = Tools.convert_height(self.parent().node_dict[i].height,
                                           self.laxis,
                                           self.raxis)
            _q = self.parent().node_dict[i].q
            _skew = self.parent().node_dict[i].skew

            if self.parent().nodes[i].is_enabled():
                if self.parent().nodes[i].ctrls[1].isChecked():
                    _response = Tools.skew_gauss(x=self.parent().angle,
                                                 amp=_height,
                                                 x0=_shift,
                                                 sigma=_q,
                                                 skew=_skew)
                    _cry_area = _cry_area + np.trapz(self.parent().angle,
                                                     _response)
                else:
                    _response = Tools.skew_gauss(x=self.parent().angle,
                                                 amp=_height,
                                                 x0=_shift,
                                                 sigma=_q,
                                                 skew=_skew)
                    _amo_area = _amo_area + np.trapz(self.parent().angle,
                                                     _response)

        if np.abs(_cry_area) > 0.0:
            _percent_crystal = np.abs(_cry_area / (_cry_area + _amo_area) * 100)
        else:
            _percent_crystal = 0.0
        self.parent().crystal_label.setText(''.join(['Percent Crystallinity: ', str(round(_percent_crystal, 1)), ' %']))

    # ------------------------------------------
    # Update area under curve with movement
    # ------------------------------------------
    def update_area(self):
        _shift = self.parent().node_dict[self.focused].shift
        _height = Tools.convert_height(self.parent().node_dict[self.focused].height,
                                       self.laxis,
                                       self.raxis)
        _q = self.parent().node_dict[self.focused].q
        _skew = self.parent().node_dict[self.focused].skew

        if self.parent().nodes[self.focused].is_enabled():
            _response = Tools.skew_gauss(x=self.parent().angle,
                                         amp=_height,
                                         x0=_shift,
                                         sigma=_q,
                                         skew=_skew)
            self.area.set_data(self.parent().angle, _response)

    # ------------------------------------------
    # Update GMM with node movement
    # ------------------------------------------
    def update_gmm_contributors(self):
        self.curve_contributors = []

        # contributers
        _pen = []
        _contribute = []
        # nodes
        _shift = []
        _height = []
        _q = []
        _skew = []
        # gmm
        _response = []

        for i in range(0, len(self.parent().nodes)):
            if self.parent().nodes[i].is_enabled() and self.parent().contributors.isChecked():
                # main node
                _pen = QPen(QColor(self.parent().palette.colour[i]))
                _pen.setWidth(2)
                _contribute = PlotCurve(_pen)

                _shift = self.parent().node_dict[i].shift
                _height = Tools.convert_height(self.parent().node_dict[i].height,
                                               self.laxis,
                                               self.raxis)
                _q = self.parent().node_dict[i].q
                _skew = self.parent().node_dict[i].skew
                _response = Tools.skew_gauss(x=self.parent().angle,
                                             amp=_height,
                                             x0=_shift,
                                             sigma=_q,
                                             skew=_skew)
                _contribute.set_data(self.parent().angle, _response)
                self.curve_contributors.append(_contribute)

    def update_gmm_curves(self):
        _totalresponse = [0]
        # nodes
        _shift = []
        _height = []
        _q = []
        _skew = []
        # gmm
        _response = []
        _totalresponse

        for i in range(0, len(self.parent().nodes)):
            _shift = self.parent().node_dict[i].shift
            _height = Tools.convert_height(self.parent().node_dict[i].height,
                                           self.laxis,
                                           self.raxis)
            _q = self.parent().node_dict[i].q
            _skew = self.parent().node_dict[i].skew
            if self.parent().nodes[i].is_enabled():
                _response = Tools.skew_gauss(x=self.parent().angle,
                                             amp=_height,
                                             x0=_shift,
                                             sigma=_q,
                                             skew=_skew)
                _totalresponse = _totalresponse + _response
        self.curve_gmm.set_data(self.parent().angle, _totalresponse)

    # ------------------------------------------
    # Update Handles/Nodes with movement
    # ------------------------------------------
    def update_handles(self, new=False):
        _h = []

        for i in range(len(self.parent().nodes)):
            # only do active nodes
            if self.parent().nodes[i].is_enabled() or new:
                _h = Tools.to_pixel_coords(self.width(),
                                           self.height(),
                                           self.parent().node_dict[i].shift,
                                           self.xaxis,
                                           self.parent().node_dict[i].height,
                                           self.raxis)

                self.handles[i] = QPoint(_h.x(), _h.y())

                self.parent().nodes[i].ctrls[2].setText(str(round(self.parent().node_dict[i].shift, 5)))
                self.parent().nodes[i].ctrls[3].setText(
                    str(round(Tools.convert_height(self.parent().node_dict[i].height,
                                                   self.laxis,
                                                   self.raxis), 5)))

            else:
                self.handles[i] = None

    def update_q_handles(self, new=False):
        _q = []
        _qs = []

        for i in range(len(self.parent().nodes)):
            if self.parent().nodes[i].is_enabled() or new:
                # handles q distance (width)
                _q = Tools.to_pixel_coords(self.width(),
                                           self.height(),
                                           self.parent().node_dict[i].q,
                                           self.qaxis,
                                           self.parent().node_dict[i].q,
                                           self.raxis)

                # handles skew distance (height)
                _qs = Tools.to_pixel_coords(self.width(),
                                            self.height(),
                                            self.parent().node_dict[i].q,
                                            self.qaxis,
                                            self.parent().node_dict[i].skew * 10,
                                            self.skewaxis)

                self.handles_ql[i] = QPoint(self.handles[i].x() - _q.x(),
                                            self.handles[i].y() - _qs.y() + round(self.height() / 2))
                self.handles_qr[i] = QPoint(self.handles[i].x() + _q.x(),
                                            self.handles[i].y() + _qs.y() - round(self.height() / 2))

                self.parent().nodes[i].ctrls[4].setText(str(round(self.parent().node_dict[i].q, 5)))
                self.parent().nodes[i].ctrls[5].setText(str(round(self.parent().node_dict[i].skew, 5)))
            else:
                self.handles_ql[i] = None
                self.handles_qr[i] = None

    # ------------------------------------------
    # Update Plot
    # ------------------------------------------
    def update_plot(self, x, y):
        if x.size > 0:
            self.curve_xrd.set_data(x, y)
            self.update()

    # ------------------------------------------
    # Update Plot Axis
    # ------------------------------------------
    def update_axis(self):
        self.laxis = Axis('left', 0, self.parent().xrd_max)
        self.xaxis = Axis('bottom', self.parent().angle_min, self.parent().angle_max)
        self.parent().axisauto.setChecked(True)


# ------------------------------------------
# Node Textbox Highlighter
# ------------------------------------------
class ActiveNode(QFrame):
    def __init__(self, index, *args):
        QFrame.__init__(self, *args)
        self.index = index
        self.focused = -1

    def mousePressEvent(self, event):
        QFrame.mousePressEvent(self, event)

        _gapx = []
        _loc_boxes = []

        for i, h in enumerate(self.parent().active_node):
            # find gap between node tabs. This scales with the gui
            if i == 0:
                _gapx = round((self.parent().active_node[i + 1].x() - self.parent().active_node[i].x()))

            # event global converts local click in box to global coords in pixels
            # needs to be self.parent() or else it changes with button click location
            _loc_boxes = self.parent().mapToGlobal(h.pos()).x()
            if round(_gapx / 2) >= abs(_loc_boxes - event.globalPos().x() + round(_gapx / 2)):
                if h is not None:
                    self.focused = i
                    if self.parent().nodes[self.focused].is_enabled():
                        self.parent().plotwin.mousePressEventTab(i)


# ------------------------------------------
# Plot curve object to assign qualities to
# ------------------------------------------
class PlotCurve(object):
    def __init__(self, pen, brush=QBrush()):
        self.pen = pen
        self.brush = brush
        self.xdata = []
        self.ydata = []

    def set_data(self, x, y):
        self.xdata = x
        self.ydata = y


class PlotArea(object):
    def __init__(self, pen, brush=QBrush(), path=QPainterPath()):
        self.pen = pen
        self.brush = brush
        self.path = path
        self.xdata = []
        self.ydata = []

    def set_data(self, x, y):
        self.xdata = x
        self.ydata = y


class CPlotBragg(object):
    def __init__(self, pen):
        self.pen = pen
        self.theta1 = []
        self.theta2 = []

    def set_data(self, x1, x2):
        self.theta1 = x1
        self.theta2 = x2


# ------------------------------------------
# Handles/Nodes Grid layout and signalling
# ------------------------------------------
class NodeLayout(QGridLayout):
    updated = Signal(int)  # (node index, parameter, new value)
    enabled = Signal(int)  # node index

    def __init__(self, index, mainwin):
        QGridLayout.__init__(self)
        self.index = index
        self.mainwin = mainwin
        # values
        self.ctrls = []
        self.shift = []
        self.height = []
        self.skew = []
        self.q = []

    def add_controls(self, checkbox, crystal, shift, height, q, skew):
        self.ctrls = [checkbox, crystal, shift, height, q, skew]

        self.addWidget(checkbox, 0, 1)
        checkbox.clicked.connect(self.node_state_changed)

        self.addWidget(crystal, 1, 1)

        shift.editingFinished.connect(self.change)
        self.addWidget(shift, 2, 1)

        height.editingFinished.connect(self.change)
        self.addWidget(height, 3, 1)

        q.editingFinished.connect(self.change)
        self.addWidget(q, 4, 1)

        skew.editingFinished.connect(self.change)
        self.addWidget(skew, 5, 1)

    # if is enabled or not, returns boolean
    def is_enabled(self):
        return self.ctrls[0].isChecked()

    # Makes line edits and crystal box uneditable when off
    def set_controls_enabled(self, enabled):
        for i in range(1, len(self.ctrls)):
            self.ctrls[i].setEnabled(enabled)

    def node_state_changed(self):
        # trying to learn signal thing in QT
        self.enabled.emit(self.index)

    def change(self):
        self.shift = float(self.ctrls[2].text())
        self.height = float(self.ctrls[3].text())
        self.q = float(self.ctrls[4].text())
        self.skew = float(self.ctrls[5].text())
        self.updated.emit(self.index)


# ------------------------------------------
# Node values for node_dict, the non dictionary dictionary
# ------------------------------------------
class NodeValues(object):
    def __init__(self):
        self.shift = []
        self.height = []
        self.q = []
        self.skew = []

    def set_values(self, shift, height, q, skew):
        self.shift = shift
        self.height = height
        self.q = q
        self.skew = skew
