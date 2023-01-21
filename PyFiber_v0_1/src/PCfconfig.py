import configparser

def getinitconfig(self,configfile,geom):
    # ini file
    _config = configparser.ConfigParser()
    _config.read(configfile)
    try:
        _i_xpos = _config.getint('Global', 'ixpos')
        # default to 20 if location is too large
        if _i_xpos > geom.width():
            _i_xpos = 20
    except ValueError:
        # catch anything that is not an int for location
        _i_xpos = 20

    try:
        _i_ypos = _config.getint('Global', 'iypos')
        # default to 20 if location is too large
        if _i_ypos > geom.height():
            _i_ypos = 20
    except ValueError:
        # catch anything that is not an int for location
        _i_ypos = 20

    try:
        _i_width = _config.getint('Global', 'iwidth')
        # default to 800 if window is too large or below zero. Minimum is enforced automatically
        if _i_width > geom.width() or _i_width < 0:
            _i_width = 1000
    except ValueError:
        # catch anything that is not an int
        _i_width = 1000

    try:
        _i_height = _config.getint('Global', 'iheight')
        # default to 600 if window is too large or below zero. Minimum is enforced automatically
        if _i_height > geom.height() or _i_height < 0:
            _i_height = 750
    except ValueError:
        # catch anything that is not an int for location
        _i_height = 750

    return _i_xpos, _i_ypos,  _i_width, _i_height

def getconfig(self,configfile,geom):
    # ini file
    _config = configparser.ConfigParser()
    _config.read(configfile)
    try:
        self.i_xpos = _config.getint('Global', 'ixpos')
        # default to 20 if location is too large
        if self.i_xpos > geom.width():
            self.i_xpos = 20
    except ValueError:
        # catch anything that is not an int for location
        self.i_xpos = 20

    try:
        self.i_ypos = _config.getint('Global', 'iypos')
        # default to 20 if location is too large
        if self.i_ypos > geom.height():
            self.i_ypos = 20
    except ValueError:
        # catch anything that is not an int for location
        self.i_ypos = 20

    try:
        self.i_width = _config.getint('Global', 'iwidth')
        # default to 800 if window is too large or below zero. Minimum is enforced automatically
        if self.i_width > geom.width() or self.i_width < 0:
            self.i_width = 1000
    except ValueError:
        # catch anything that is not an int
        self.i_width = 1000

    try:
        self.i_height = _config.getint('Global', 'iheight')
        # default to 600 if window is too large or below zero. Minimum is enforced automatically
        if self.i_height > geom.height() or self.i_height < 0:
            self.i_height = 750
    except ValueError:
        # catch anything that is not an int for location
        self.i_height = 750

    try:
        self.i_fps = _config.getint('Global', 'ifps')
        # default to 20 if location is too large
        if self.i_fps < 0:
            self.i_fps = 30
    except ValueError:
        # catch anything that is not an int
        self.i_fps = 30

    # gaussian
    try:
        self.i_smooth = _config.getint('FitType', 'ismooth')
        if self.i_smooth < 0:
            self.i_smooth = 5
    except ValueError:
        # catch anything that is not an int
        self.i_smooth = 5

    # Asymmetric Least Squares
    try:
        self.i_als_iter = _config.getint('FitType', 'iALSiter')
        if self.i_als_iter < 0:
            self.i_als_iter = 10
    except ValueError:
        # catch anything that is below zero
        self.i_als_iter = 10

    try:
        self.i_als_lambda = _config.getint('FitType', 'iALSlambda')
        if self.i_als_lambda < 0:
            self.i_als_lambda = 2500
    except ValueError:
        # catch anything that is not an int
        self.i_als_lambda = 2500

    try:
        self.f_als_p = _config.getfloat('FitType', 'fALSp')
        if self.f_als_p < 0.0:
            self.f_als_p = 0.001
    except ValueError:
        # catch anything that is below zero
        self.f_als_p = 0.001

    # GMM
    try:
        self.i_total_nodes = _config.getint('FitType', 'iNodes')
        if self.i_total_nodes < 1 or self.i_total_nodes > 12:
            self.i_total_nodes = 8
    except ValueError:
        # catch anything that is not an int
        self.i_total_nodes = 8

    try:
        self.i_gmm_peak_nodes = _config.getint('FitType', 'iPeakNodes')
        if self.i_gmm_peak_nodes < 1 or self.i_gmm_peak_nodes > (self.i_total_nodes - 1):
            self.i_gmm_peak_nodes = 5
    except ValueError:
        # catch anything that is not an int
        self.i_gmm_peak_nodes = 5

    self.i_gmm_base_nodes = self.i_total_nodes-self.i_gmm_peak_nodes

    try:
        self.i_gmm_max_iter = _config.getint('FitType', 'iMaxIter')
        if self.i_gmm_max_iter < 0:
            self.i_gmm_max_iter = 100
    except ValueError:
        # catch anything that is not an int
        self.i_gmm_max_iter = 100

    try:
        self.f_gmm_tol = _config.getfloat('FitType', 'fTolerance')
        if self.f_gmm_tol < 0:
            self.f_gmm_tol = 1E-8
    except ValueError:
        # catch anything that is not an int
        self.f_gmm_tol = 1E-8

    # Angles
    try:
        self.bStartAtMin = _config.getboolean('Angles', 'bStartAtMin')
    except ValueError:
        # catch anything that is not a boolean
        self.bStartAtMin = False

    try:
        self.angle_max = _config.getint('Angles', 'iMaxAngle')
        if self.angle_max < 0:
            self.angle_max = 60
    except ValueError:
        # catch anything that is not an int
        self.angle_max = 60

    try:
        self.angle_min = _config.getint('Angles', 'iMinAngle')
        if self.angle_min < 0 or self.angle_min > self.angle_max:
            self.angle_min = 5
    except ValueError:
        # catch anything that is not an int
        self.angle_min = 5

    try:
        self.i_major_tick = _config.getint('Angles', 'iMajorTick')
        if self.i_major_tick < 0:
            self.i_major_tick = 15
    except ValueError:
        # catch anything that is not an int
        self.i_major_tick = 15

    try:
        self.i_minor_tick = _config.getint('Angles', 'iMinorTick')
        if self.i_minor_tick < 0 or self.i_minor_tick > self.i_major_tick:
            self.i_minor_tick = 5
    except ValueError:
        # catch anything that is not an int
        self.i_minor_tick = 5


    # Theme Settings
    try:
        self.bTheme = _config.getboolean('Theme', 'bTheme')
    except ValueError:
        # catch anything that is not a boolean
        self.bTheme = False

    try:
        self.b_contributors = _config.getboolean('Theme', 'bContributors')
    except ValueError:
        # catch anything that is not a bool
        self.b_contributors = True

    try:
        self.b_cursor = _config.getboolean('Theme', 'bCursor')
    except ValueError:
        # catch anything that is not a bool
        self.b_Cursor = False

    # LAMMPS reference file
    self.reference = _config.get('LAMMPSref', "sLAMMPSref")
