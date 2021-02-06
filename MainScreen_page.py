# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'designeroViTaJ.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *


class MainMenu(object):
    def setupUi(self, MainMenu):
        if MainMenu.objectName():
            MainMenu.setObjectName('MainMenu')
        MainMenu.resize(1336, 1069)
        self.centralwidget = QWidget(MainMenu)
        self.centralwidget.setObjectName(u"centralwidget")
        self.label_MainTitle = QLabel(self.centralwidget)
        self.label_MainTitle.setObjectName(u"label_MainTitle")
        self.label_MainTitle.setGeometry(QRect(300, 30, 761, 121))
        self.label_MainTitle.setAlignment(Qt.AlignCenter)
        self.scrollArea_drinklist = QScrollArea(self.centralwidget)
        self.scrollArea_drinklist.setObjectName(u"scrollArea_drinklist")
        self.scrollArea_drinklist.setGeometry(QRect(100, 210, 1141, 491))
        self.scrollArea_drinklist.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_drinklist.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea_drinklist.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1139, 472))
        self.scrollArea_drinklist.setWidget(self.scrollAreaWidgetContents)
        self.pushButton_exit = QPushButton(self.centralwidget)
        self.pushButton_exit.setObjectName(u"pushButton_exit")
        self.pushButton_exit.setGeometry(QRect(1140, 950, 151, 51))
        self.pushButton_maintenance = QPushButton(self.centralwidget)
        self.pushButton_maintenance.setObjectName(u"pushButton_maintenance")
        self.pushButton_maintenance.setGeometry(QRect(100, 960, 151, 51))
        MainMenu.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainMenu)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1336, 21))
        MainMenu.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainMenu)
        self.statusbar.setObjectName(u"statusbar")
        MainMenu.setStatusBar(self.statusbar)

        self.retranslateUi(MainMenu)

        QMetaObject.connectSlotsByName(MainMenu)
    # setupUi

    def retranslateUi(self, MainMenu):
        MainMenu.setWindowTitle(QCoreApplication.translate("MainMenu", u"MainMenu", None))
        self.label_MainTitle.setText(QCoreApplication.translate("MainMenu", u"Mixus", None))
        self.pushButton_exit.setText(QCoreApplication.translate("MainMenu", u"Exit", None))
        self.pushButton_maintenance.setText(QCoreApplication.translate("MainMenu", u"Maintenance", None))
    # retranslateUi


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainMenu()
    main.show()
    sys.exit(app.exec_())

