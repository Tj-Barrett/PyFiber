# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QPoint
import numpy as np


# ------------------------------------------
# Pixel Conversion Tools
# ------------------------------------------
class Tools(object):
    def convert_height(y, to_axis, from_axis):
        return (y - from_axis.min) / (from_axis.max - from_axis.min) * (to_axis.max - to_axis.min)

    # Define simple gaussian
    def gauss_function(x, amp, x0, sigma):
        return amp * np.exp(-(x - x0) ** 2. / (2. * sigma ** 2.))

    # Skewed gaussian
    def skew_gauss(x, amp, x0, sigma, skew):
        _gauss = amp * np.exp(-(x - x0) ** 2. / (2. * sigma ** 2.))
        return _gauss + skew * (x0 - x) / sigma * _gauss * np.sqrt(2 * np.pi)

    # transfer to pixel coordinates
    def to_pixel_coords(width, height, x, xaxis, y=0, yaxis=None):
        _xp = (x - xaxis.min) / (xaxis.max - xaxis.min) * width
        if yaxis is not None:
            _yp = (y - yaxis.max) / (yaxis.min - yaxis.max) * height
            return QPoint(_xp, _yp)
        else:
            return _xp

    # transfer from pixel coorinates
    def from_pixel_coords(width, height, point, xaxis, yaxis):
        _x = point.x() * (xaxis.max - xaxis.min) / width + xaxis.min
        _y = point.y() * (yaxis.min - yaxis.max) / height + yaxis.max

        # applying boundaries so node cant go outside plot
        if xaxis.max > _x > xaxis.min and yaxis.max > _y > yaxis.min:
            return _x, _y
        elif _x > xaxis.min and yaxis.max > _y > yaxis.min:  # the four walls
            return xaxis.max, _y
        elif _x < xaxis.max and yaxis.max > _y > yaxis.min:
            return xaxis.min, _y
        elif xaxis.max > _x > xaxis.min and _y < yaxis.max:
            return _x, yaxis.min
        elif xaxis.max > _x > xaxis.min and _y > yaxis.min:
            return _x, yaxis.max
        elif _x > xaxis.min and _y > yaxis.min:  # corners
            return xaxis.max, yaxis.max
        elif _x < xaxis.max and _y < yaxis.max:
            return xaxis.min, yaxis.min
        elif _x > xaxis.min and _y < yaxis.max:
            return xaxis.max, yaxis.min
        elif _x < xaxis.max and _y > yaxis.min:
            return xaxis.min, yaxis.max
