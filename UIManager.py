from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QComboBox, QLabel, QMainWindow, QDialog, QStackedWidget, QPushButton, \
    QHBoxLayout, QVBoxLayout, QGroupBox
from Enums import *


class UIManager:
    def __init__(self, window_manager, app):
        self.window_manager = window_manager
        self.res = get_screen_resolution(app)

    def title_setup(self, title):
        title.setGeometry(-2, 0, self.res.width() + 4, int(round(self.res.height() * 0.15, 0)))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(GUI.label_background_color.value)
        title.setFont(QFont("Times", 30, QFont.Bold))

    def bottom_right_button_setup(self, button):
        button.setGeometry(int(self.res.width() * (1 - 1 / 30 - 1 / 5)), int(self.res.height() * 5.18 / 6),
                           int(self.res.width() / 5), int(self.res.height() / 8))
        self.push_button_setup(button)

    def bottom_left_button_setup(self, button):
        button.setGeometry(int(self.res.width() / 30), int(self.res.height() * 5.18 / 6), int(self.res.width() / 5),
                           int(self.res.height() / 8))
        self.push_button_setup(button)

    def bottom_background_setup(self, label):
        label.setGeometry(-2, int(self.res.height() * 0.85), self.res.width() + 4, int(self.res.height() * 0.15))

        label.setStyleSheet(GUI.label_background_color.value)

    def image_setup(self, label, path):
        label.setGeometry(int(self.res.width() * 2 / 3),
                          int(self.res.height() / 2) - GUI.drink_image_size.value.height() / 2,
                          GUI.drink_image_size.value.width(), GUI.drink_image_size.value.height())
        label.setPixmap(QPixmap(path))

    def sliders_setup(self, slider, pos):
        slider.setGeometry(int(self.res.width() / 20), int(self.res.height() * (5 + 1.5 * (pos - 1)) / 12),
                           int(self.res.width() * 0.9), int(self.res.height() / 12))

    def push_button_setup(self, button):
        button.setStyleSheet(GUI.button_color.value)
        button.pressed.connect(lambda: button.setStyleSheet(GUI.button_color_pressed.value))
        button.released.connect(
            lambda: button.setStyleSheet(GUI.button_color.value))
        button.setFont(QFont("Times", 15, QFont.Bold))

    def group_box_setup(self, groupbox, layout, pos):
        groupbox.setGeometry(int(self.res.width() * (1 / 15 + 1 / 4 * (pos - 1))),
                             int(self.res.height() * (1 / 2 - 1 / 4)), int(self.res.width() / 5),
                             int(self.res.height() / 2))
        groupbox.setLayout(layout)

    def progress_bar_setup(self, progressbar):
        progressbar.setGeometry(int(self.res.width() * 0.3), int(self.res.height() * 0.9), int(self.res.width() * 0.65),
                                int(self.res.height() * 0.05))

    def main_menu_setup(self, main_menu):
        self.title_setup(main_menu.label_Title)
        self.bottom_background_setup(main_menu.label_bottom_screen)
        self.bottom_left_button_setup(main_menu.pushButton_maintenance)
        self.bottom_right_button_setup(main_menu.pushButton_exit)
        main_menu.scrollArea_drinklist.setGeometry(0, int(self.res.height() * 0.15), self.res.width(),
                                                   int(self.res.height() * 0.7))
        main_menu.scrollArea_drinklist.setWidgetResizable(True)
        main_menu.scroll_layout.setSpacing(10)
        main_menu.scroll_layout.setContentsMargins(5, 5, 5, 5)

    def maintenance_menu_setup(self, maintenance_menu):
        self.title_setup(maintenance_menu.label_Title)
        self.bottom_background_setup(maintenance_menu.label_bottom_screen)
        self.bottom_left_button_setup(maintenance_menu.pushButton_return)
        self.bottom_right_button_setup(maintenance_menu.pushButton_send)
        self.sliders_setup(maintenance_menu.Slider_x, 1)
        self.sliders_setup(maintenance_menu.Slider_y, 2)
        self.sliders_setup(maintenance_menu.Slider_z, 3)

        maintenance_menu.pushButton_home.setGeometry(int(self.res.width() / 20), int(self.res.height() / 5),
                                                     int(self.res.width() / 4), int(self.res.height() / 6))
        self.push_button_setup(maintenance_menu.pushButton_home)

        maintenance_menu.pushButton_bottle.setGeometry(int(self.res.width() * (1 - 1 / 20 - 1 / 4)),
                                                       int(self.res.height() / 5),
                                                       int(self.res.width() / 4),
                                                       int(self.res.height() / 6))
        self.push_button_setup(maintenance_menu.pushButton_bottle)

    def drink_option_menu_setup(self, drink_option_menu):
        self.title_setup(drink_option_menu.label_Title)
        self.bottom_background_setup(drink_option_menu.label_bottom_screen)
        self.bottom_left_button_setup(drink_option_menu.pushButton_return)
        self.bottom_right_button_setup(drink_option_menu.pushButton_confirm)
        self.group_box_setup(drink_option_menu.groupBox_options, drink_option_menu.verticalLayout_options, 1)
        self.group_box_setup(drink_option_menu.groupBox_ingredients, drink_option_menu.verticalLayout_ingredients, 2)

    def mixing_menu_setup(self, mixing_menu):
        self.title_setup(mixing_menu.label_Title)
        self.bottom_background_setup(mixing_menu.label_bottom_screen)
        self.bottom_left_button_setup(mixing_menu.pushButton_return)
        self.group_box_setup(mixing_menu.groupBox_wating, mixing_menu.verticalLayout_waiting, 1)
        self.group_box_setup(mixing_menu.groupBox_done, mixing_menu.verticalLayout_done, 2)
        self.progress_bar_setup(mixing_menu.progressBar)


def get_screen_resolution(app):
    sc_res = app.desktop().screenGeometry()
    sc_res = QRect(0, 0, 1024, 600)
    return sc_res
