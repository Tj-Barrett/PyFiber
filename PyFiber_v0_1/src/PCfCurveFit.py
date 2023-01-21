from scipy.ndimage import gaussian_filter as gf
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.signal import argrelextrema

from src.PCTools import *

# ------------------------------------------
# Curve Fit
# ------------------------------------------
def baseline_als(y, lam, p, niter=10):
    # Asymmetric least squares method- find baseline of data to remove
    # https://www.researchgate.net/publication/228961729_Baseline_Correction_with_Asymmetric_Least_Squares_Smoothing
    # https: // stackoverflow.com / questions / 29156532 / python - baseline - correction - library / 29185844
    _L = len(y)
    _D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(_L, _L - 2))
    _D = lam * _D.dot(_D.transpose())  # Precompute this term since it does not depend on `w`
    _w = np.ones(_L)
    _W = sparse.spdiags(_w, 0, _L, _L)
    _z = []
    for i in range(niter):
        _W.setdiag(_w)  # Do not create a new matrix, just update diagonal values
        _Z = _W + _D
        _z = spsolve(_Z, _w * y)
        _w = p * (y > _z) + (1 - p) * (y < _z)
    return _z


def pdf(data, mean, variance):
    s1 = 1 / (np.sqrt(2 * np.pi * variance))
    s2 = np.exp(-(np.square(data - mean) / (2 * variance)))
    return s1 * s2


class CurveFit(object):
    def fcurvefit(self, x, y):
        # http://www.astroml.org/book_figures/chapter4/fig_GMM_1D.html
        #
        _x = np.array(x)
        _y = np.array(y)
        for i in range(0, len(_y)):
            if _y[i] < 0:
                _y[i] = 0
        del x, y

        # baseline reduction for peak guessing
        _baseline = baseline_als(y=_y, lam=self.i_als_lambda, p=self.f_als_p, niter=self.i_als_iter)
        _adjy = _y - _baseline

        for i in range(0, len(_adjy)):
            if _adjy[i] < 0:
                _adjy[i] = 0

        # sample data, pretty much just a 1D array with x instances cooresponding to height
        _peak_sample = []
        for i in range(len(_adjy)):
            # make an integer greater than 1
            _count = np.round(_adjy[i] * 10 ** 4)
            for j in range(int(_count)):
                _peak_sample.append(_x[i])

        _base_sample = []
        for i in range(len(_baseline)):
            # make an integer greater than 1
            _count = np.round(_baseline[i] * 10 ** 4)
            for j in range(int(_count)):
                _base_sample.append(_x[i])

        _filt_adjy = gf(_adjy, sigma=self.i_smooth)

        # initial peak guesses
        _peak_indicies = argrelextrema(_filt_adjy, comparator=np.greater, order=5)[0]
        _base_indicies = argrelextrema(_baseline, comparator=np.greater, order=5)[0]

        # initialize for expectation maximization / gmm
        _peak_k = []
        _peak_weights = []
        _peak_means = []
        _peak_vars = []

        _base_k = []
        _base_weights = []
        _base_means = []
        _base_vars = []

        # might not technically be a tolerance
        _eps = self.f_gmm_tol

        # sort by descending height
        _useless, _peak_indicies = zip(*sorted(zip(_y[_peak_indicies], _peak_indicies), reverse=True))
        del _useless
        _peak_indicies = np.array(_peak_indicies)

        _useless, _base_indicies = zip(*sorted(zip(_y[_base_indicies], _base_indicies), reverse=True))
        del _useless
        _base_indicies = np.array(_base_indicies)

        # Peaks
        #
        # either number of nodes specified by ini file, or max number of peaks, whichever is fewer
        if len(_peak_indicies) > self.i_gmm_peak_nodes:
            _peak_weights = _y[_peak_indicies[range(self.i_gmm_peak_nodes)]]
            _peak_means = _x[_peak_indicies[range(self.i_gmm_peak_nodes)]]
            _peak_k = self.i_gmm_peak_nodes
        else:
            _peak_weights = _y[_peak_indicies]
            _peak_means = _x[_peak_indicies]
            _peak_k = len(_peak_indicies)

        _peak_vars = np.random.random_sample(size=_peak_k)

        # Base
        if len(_base_indicies) > self.i_gmm_base_nodes:
            _base_weights = _y[_peak_indicies[range(self.i_gmm_base_nodes)]]
            _base_means = _x[_peak_indicies[range(self.i_gmm_base_nodes)]]
            _base_k = self.i_gmm_base_nodes
        else:
            _base_weights = _y[_base_indicies]
            _base_means = _x[_base_indicies]
            _base_k = len(_base_indicies)

        _base_vars = np.random.random_sample(size=_base_k)

        for _step in range(self.i_gmm_max_iter):
            # inspection
            # variance will go to zero if curve is not needed, returns NaN error so remove it
            _peak_out = [(k, l, m) for (k, l, m) in zip(_peak_means, _peak_weights, _peak_vars) if m > 1E-9]
            _peak_means, _peak_weights, _peak_vars = zip(*_peak_out)
            _peak_means = np.array(_peak_means)
            _peak_weights = np.array(_peak_weights)
            _peak_vars = np.array(_peak_vars)
            _peak_k = len(_peak_vars)

            _base_out = [(k, l, m) for (k, l, m) in zip(_base_means, _base_weights, _base_vars) if m > 1E-9]
            _base_means, _base_weights, _base_vars = zip(*_base_out)
            _base_means = np.array(_base_means)
            _base_weights = np.array(_base_weights)
            _base_vars = np.array(_base_vars)
            _base_k = len(_base_vars)

            # expectation step for peaks and base
            _peak_like = []
            for j in range(_peak_k):
                _peak_like.append(pdf(_peak_sample, _peak_means[j], np.sqrt(_peak_vars[j])))
            _peak_like = np.array(_peak_like)

            _base_like = []
            for j in range(_base_k):
                _base_like.append(pdf(_base_sample, _base_means[j], np.sqrt(_base_vars[j])))
            _base_like = np.array(_base_like)

            # maximization peak
            _peak_b = []
            for j in range(_peak_k):
                _peak_b.append(
                    (_peak_like[j] * _peak_weights[j]) / (np.sum([_peak_like[i] * _peak_weights[i] for i in range(_peak_k)], axis=0) + _eps))

                # update means and variance
                _peak_means[j] = np.sum(_peak_b[j] * _peak_sample) / (np.sum(_peak_b[j] + _eps))

                _peak_vars[j] = np.sum(_peak_b[j] * np.square(_peak_sample - _peak_means[j])) / (np.sum(_peak_b[j] + _eps))
                # update weights
                _peak_weights[j] = np.mean(_peak_b[j])

            # maximization base
            _base_b = []
            for j in range(_base_k):
                _base_b.append(
                    (_base_like[j] * _base_weights[j]) / (np.sum([_base_like[i] * _base_weights[i] for i in range(_base_k)], axis=0) + _eps))

                # update means and variance
                _base_means[j] = np.sum(_base_b[j] * _base_sample) / (np.sum(_base_b[j] + _eps))

                _base_vars[j] = np.sum(_base_b[j] * np.square(_base_sample - _base_means[j])) / (np.sum(_base_b[j] + _eps))
                # update weights
                _base_weights[j] = np.mean(_base_b[j])


        _peak_max_weight = np.max(_peak_weights)
        _peak_max_y = np.max(_adjy)
        _peak_corr_weights = _peak_weights / _peak_max_weight * _peak_max_y

        _base_max_weight = np.max(_base_weights)
        _base_max_y = np.max(_baseline)
        _base_corr_weights = _base_weights / _base_max_weight * _base_max_y

        # Combine peaks and bases
        _means = []
        # ugly but i dont feel like fighting the data type right now
        for i in _base_means:
            _means.append(i)
        for i in _peak_means:
            _means.append(i)

        _corr_weights = []
        for i in _base_corr_weights:
            _corr_weights.append(i)
        for i in _peak_corr_weights:
            _corr_weights.append(i)

        _vars = []
        for i in _base_vars:
            _vars.append(i)
        for i in _peak_vars:
            _vars.append(i)

        for i in range(len(_means)):
            # shift
            self.node_dict[i].shift = _means[i]
            # height
            self.node_dict[i].height = Tools.convert_height(_corr_weights[i], self.plotwin.raxis, self.plotwin.laxis)
            # Q
            self.node_dict[i].q = np.sqrt(_vars[i])
            # controls
            self.nodes[i].ctrls[0].setChecked(True)
            self.nodes[i].ctrls[1].setEnabled(True)
            self.nodes[i].ctrls[2].setEnabled(True)
            self.nodes[i].ctrls[3].setEnabled(True)
            self.nodes[i].ctrls[4].setEnabled(True)
            self.nodes[i].ctrls[5].setEnabled(True)

        self.plotwin.update_handles()
        self.plotwin.update_q_handles()
        self.plotwin.update()
        self.plotwin.update_crystallinity()
