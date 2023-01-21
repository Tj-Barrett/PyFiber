import os

# Dependencies List
PCdep = []
# Openpyxl
PCdep.append('openpyxl')
# Pyside2 is a QT5 package, and is the basis for the GUI
PCdep.append('pyside6')
# Pandas deals with importing/modifying data
PCdep.append('pandas')
# Scipy and Nupy deal with data processing
PCdep.append('scipy')
PCdep.append('numpy')

for i in PCdep:
    os.system('pip install '+i)
