from PySide6.QtGui import QColor


# ------------------------------------------
# Selecting Themes, all in one place
# ------------------------------------------
class ThemeSelect(object):
    def __init__(self, *args):
        self.colour = []
        self.widget = []
        self.frame = []
        # statics
        self.dark_primary = '#2E3440'
        self.dark_secondary = '#3B4252'
        self.dark_text = '#ECEFF4'
        self.dark_ticks = '#D8DEE9'
        # light
        self.light_primary = '#ECEFF4'
        self.light_secondary = '#D8DEE9'
        self.light_text = '#2E3440'
        self.light_ticks = '#3B4252'

    def light(self,
              active=None,
              widget=None,
              frame=None,
              plot=None,
              highlight=None,
              crystal=None,
              menu=None,
              gradient=None,
              textpen=None):
        # Primary Background Color
        if widget is not None:
            widget.setStyleSheet('QWidget {color:#2E3440; background-color: #ECEFF4}')
        if frame is not None:
            frame.setStyleSheet('QFrame {color:#2E3440; background-color: #ECEFF4}')
        if plot is not None:
            plot.setStyleSheet('QFrame {background-color: transparent; border-color: #ECEFF4 }')
        if highlight is not None:
            highlight.setStyleSheet("QFrame {background-color: #D8DEE9; border-radius: 10px;}")
        if crystal is not None:
            crystal.setStyleSheet('QLabel {color:#2E3440; background-color: transparent}')
        if menu is not None:
            menu.setStyleSheet('QMenuBar {color:#2E3440; background-color: #ECEFF4}')
        if gradient is not None:
            gradient.setColorAt(0, QColor('#D8DEE9'))
            gradient.setColorAt(1, QColor('#E5E9F0'))
        if textpen is not None:
            if active is not None:
                textpen.ctrls[0].setStyleSheet('QCheckBox {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[1].setStyleSheet('QCheckBox {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[2].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[3].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[4].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[5].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
            else:
                textpen.ctrls[0].setStyleSheet('QCheckBox {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[1].setStyleSheet('QCheckBox {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[2].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[3].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[4].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[5].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')

        # Nodes
        self.colour = ['#BF616A',  # Red
                       '#D08770',  # Orange
                       '#EBCB8B',  # Yellow
                       '#A3BE8C',  # Green
                       '#88C0D0',  # Frost 1
                       '#5E81AC',  # Frost 2
                       '#B48EAD',  # Purple
                       '#2E3440',  # Grey
                       '#81A1C1',  # Frost 3
                       '#D8DEE9',  # Snowstorm 1
                       '#5E81AC',  # Frost 4
                       '#F5E1F9',  # Snowstorm 3 edit
                       ]

    def dark(self,
             active=None,
             widget=None,
             frame=None,
             plot=None,
             highlight=None,
             crystal=None,
             menu=None,
             gradient=None,
             textpen=None):
        # Primary Background Color
        if widget is not None:
            widget.setStyleSheet('QWidget {color:#E5E9F0; background-color: #2E3440}')
        if frame is not None:
            frame.setStyleSheet('QFrame {color:#E5E9F0; background-color: #2E3440}')
        if plot is not None:
            plot.setStyleSheet('QFrame { background-color: transparent; border-color:#2E3440}')
        if highlight is not None:
            highlight.setStyleSheet("QFrame {background-color: #3B4252; border-radius: 10px;}")
        if crystal is not None:
            crystal.setStyleSheet('QLabel {color:#E5E9F0; background-color: transparent}')
        if menu is not None:
            menu.setStyleSheet('QMenuBar {color:#E5E9F0; background-color: #2E3440}')
        if gradient is not None:
            gradient.setColorAt(0, QColor('#3B4252'))
            gradient.setColorAt(1, QColor('#3B4252'))
        if textpen is not None:
            if active is not None:
                textpen.ctrls[0].setStyleSheet('QCheckBox {color:#E5E9F0; background-color:#3B4252}')
                textpen.ctrls[1].setStyleSheet('QCheckBox {color:#E5E9F0; background-color:#3B4252}')
                textpen.ctrls[2].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#3B4252}')
                textpen.ctrls[3].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#3B4252}')
                textpen.ctrls[4].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#3B4252}')
                textpen.ctrls[5].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#3B4252}')
            else:
                textpen.ctrls[0].setStyleSheet('QCheckBox {color:#E5E9F0; background-color:#2E3440}')
                textpen.ctrls[1].setStyleSheet('QCheckBox {color:#E5E9F0; background-color:#2E3440}')
                textpen.ctrls[2].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#2E3440}')
                textpen.ctrls[3].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#2E3440}')
                textpen.ctrls[4].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#2E3440}')
                textpen.ctrls[5].setStyleSheet('QLineEdit {color:#E5E9F0; background-color:#2E3440}')

        # Nodes
        self.colour = ['#BF616A',  # Red
                       '#D08770',  # Orange
                       '#EBCB8B',  # Yellow
                       '#A3BE8C',  # Green
                       '#88C0D0',  # Frost 1
                       '#5E81AC',  # Frost 2
                       '#B48EAD',  # Purple
                       '#D8DEE9',  # Grey
                       '#81A1C1',  # Frost 3
                       '#D8DEE9',  # Snowstorm 1
                       '#5E81AC',  # Frost 4
                       '#F5E1F9',  # Snowstorm 3 edit
                       ]

    def printlight(self,
              active=None,
              widget=None,
              frame=None,
              plot=None,
              highlight=None,
              crystal=None,
              menu=None,
              gradient=None,
              textpen=None):
        # Primary Background Color
        if widget is not None:
            widget.setStyleSheet('QWidget {color:#2E3440; background-color: #FFFFFF}')
        if frame is not None:
            frame.setStyleSheet('QFrame {color:#2E3440; background-color: #FFFFFF}')
        if plot is not None:
            plot.setStyleSheet('QFrame {background-color: transparent; border-color: #FFFFFF }')
        if highlight is not None:
            highlight.setStyleSheet("QFrame {background-color: #D8DEE9; border-radius: 10px;}")
        if crystal is not None:
            crystal.setStyleSheet('QLabel {color:#2E3440; background-color: transparent}')
        if menu is not None:
            menu.setStyleSheet('QMenuBar {color:#2E3440; background-color: #FFFFFF}')
        if gradient is not None:
            gradient.setColorAt(0, QColor('#D8DEE9'))
            gradient.setColorAt(1, QColor('#E5E9F0'))
        if textpen is not None:
            if active is not None:
                textpen.ctrls[0].setStyleSheet('QCheckBox {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[1].setStyleSheet('QCheckBox {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[2].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[3].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[4].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
                textpen.ctrls[5].setStyleSheet('QLineEdit {color:#2E3440; background-color:#D8DEE9}')
            else:
                textpen.ctrls[0].setStyleSheet('QCheckBox {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[1].setStyleSheet('QCheckBox {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[2].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[3].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[4].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')
                textpen.ctrls[5].setStyleSheet('QLineEdit {color:#2E3440; background-color:#ECEFF4}')


        # Nodes
        self.colour = ['#BF616A',  # Red
                       '#D08770',  # Orange
                       '#EBCB8B',  # Yellow
                       '#A3BE8C',  # Green
                       '#88C0D0',  # Frost 1
                       '#5E81AC',  # Frost 2
                       '#B48EAD',  # Purple
                       '#2E3440',  # Grey
                       '#81A1C1',  # Frost 3
                       '#D8DEE9',  # Snowstorm 1
                       '#5E81AC',  # Frost 4
                       '#F5E1F9',  # Snowstorm 3 edit
                       ]
