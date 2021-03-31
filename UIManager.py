from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QComboBox
from Enums import *


class UIManager:
    def __init__(self, window_manager, app):
        self.window_manager = window_manager
        self.res = get_screen_resolution(app)

    def title_setup(self, title):
        """
        Sets the title in the top center and a green background
        :param title: QLabel of the menu
        :return:
        """
        title.setGeometry(-2, 0, self.res.width() + 4, int(round(self.res.height() * 0.15, 0)))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(Style.label_background_color.value)
        title.setFont(QFont("Times", 30, QFont.Bold))

    def bottom_right_button_setup(self, button):
        """
        Sets the given pushButton in the bottom right corner of the screen
        :param button: QPushButton of the menu
        :return:
        """
        button.setGeometry(int(self.res.width() * (1 - 1 / 30 - 1 / 5)), int(self.res.height() * 5.18 / 6),
                           int(self.res.width() / 5), int(self.res.height() / 8))
        self.push_button_setup(button)

    def bottom_left_button_setup(self, button):
        """
        Sets the given pushButton in the bottom left corner of the screen
        :param button: QPushButton of the menu
        :return:
        """
        button.setGeometry(int(self.res.width() / 30), int(self.res.height() * 5.18 / 6), int(self.res.width() / 5),
                           int(self.res.height() / 8))
        self.push_button_setup(button)

    def bottom_background_setup(self, label):
        """
        Sets the background of the bottom of the screen to green
        :param label: QLabel of the menu
        :return:
        """
        label.setGeometry(-2, int(self.res.height() * 0.85), self.res.width() + 4, int(self.res.height() * 0.15))

        label.setStyleSheet(Style.label_background_color.value)

    def image_setup(self, label, path):
        """
        Sets the label in the center right of the screen and puts an image in it
        :param label: QLabel of the menu
        :param path: Path to the image from the main directory (images/image.png)
        :return:
        """
        label.setGeometry(int(self.res.width() * 2 / 3),
                          int(self.res.height() / 2) - Style.drink_button_size.value.height() / 2,
                          Style.drink_button_size.value.width(), Style.drink_button_size.value.height())
        label.setPixmap(QPixmap(path))

    def slider_setup(self, slider):
        """
        Sets the slider for the maintenanceMenu
        :param slider: QSlider of the menu
        :return:
        """
        slider.setGeometry(int(self.res.width() / 20), int(self.res.height() / 2),
                           int(self.res.width() * 0.9), int(self.res.height() / 6))

    def axis_label_setup(self, label):
        """
        Sets the label for the axis slider
        :param label:
        :return:
        """
        label.setGeometry(int(self.res.width() * 0.48), int(self.res.height() * 0.35),
                          int(self.res.width() * 0.9), int(self.res.height() / 6))
        label.setFont(QFont("Times", 15, QFont.Bold))

    def combobox_axis_setup(self, comboBox):
        """
        Sets the comboBox for the maintenanceMenu
        :param comboBox:
        :return:
        """
        comboBox.setGeometry(int(self.res.width() * (1/2 - 1/8)), int(self.res.height() * (5.18/6)),
                             int(self.res.width() / 4), int(self.res.height() / 8))
        comboBox.setStyleSheet(Style.combo_box.value)

    def push_button_setup(self, button):
        """
        Sets the appearance of the given button.
        :param button: QPushButton of the menu
        :return:
        """
        button.setStyleSheet(Style.button_color.value)
        button.pressed.connect(lambda: button.setStyleSheet(Style.button_color_pressed.value))
        button.released.connect(
            lambda: button.setStyleSheet(Style.button_color.value))
        button.setFont(QFont("Times", 15, QFont.Bold))

    def group_box_setup(self, groupbox, layout, pos, is_large=False):
        """
        Sets the groupBox for the DrinkOptionMenu and MixingMenu given the wanted position
        :param groupbox: QGroupBox of the menu
        :param layout: QLayout to put inside the groupBox
        :param pos: Index of the groupBox
        :param is_large: Indicate if the groupBox should be larger
        :return:
        """
        if is_large:
            groupbox.setGeometry(int(self.res.width() * (1 / 15 + 1 / 4 * (pos - 1))),
                                 int(self.res.height() * (1 / 2 - 1 / 4)),
                                 int(self.res.width() / 3),
                                 int(self.res.height() / 2))
        else:
            groupbox.setGeometry(int(self.res.width() * (1 / 15 + 1 / 4 * (pos - 1))),
                                 int(self.res.height() * (1 / 2 - 1 / 4)),
                                 int(self.res.width() / 5),
                                 int(self.res.height() / 2))
        groupbox.setLayout(layout)


    def progress_bar_setup(self, progressbar):
        """
        Sets the position of the progressbar in the bottom right corner of the screen
        :param progressbar: QProgressBar of the menu
        :return:
        """
        progressbar.setGeometry(int(self.res.width() * 0.3),
                                int(self.res.height() * 0.9),
                                int(self.res.width() * 0.65),
                                int(self.res.height() * 0.05))

    def main_layout_setup(self, layout):
        layout.setGeometry(0, int(self.res.height() * 0.15), self.res.width(), int(self.res.height() * 0.7))

    def main_menu_setup(self, main_menu):
        """
        Sets up the MainMenu
        :param main_menu: MainMenu object
        :return:
        """
        self.title_setup(main_menu.label_Title)
        self.bottom_background_setup(main_menu.label_bottom_screen)
        self.bottom_left_button_setup(main_menu.pushButton_maintenance)
        self.bottom_right_button_setup(main_menu.pushButton_exit)
        self.main_layout_setup(main_menu.scrollArea_drinklist)

        main_menu.scrollArea_drinklist.setWidgetResizable(True)
        main_menu.scroll_layout.setSpacing(10)
        main_menu.scroll_layout.setContentsMargins(5, 5, 5, 5)

    def maintenance_menu_setup(self, maintenance_menu):
        """
        Sets up the MaintenanceMenu
        :param maintenance_menu: MaintenanceMenu object
        :return:
        """
        self.title_setup(maintenance_menu.label_Title)
        self.bottom_background_setup(maintenance_menu.label_bottom_screen)
        self.bottom_left_button_setup(maintenance_menu.pushButton_return)
        self.bottom_right_button_setup(maintenance_menu.pushButton_send)
        self.axis_label_setup(maintenance_menu.label_axis)
        self.slider_setup(maintenance_menu.slider)
        self.combobox_axis_setup(maintenance_menu.comboBox_axis)
        maintenance_menu.pushButton_home.setGeometry(int(self.res.width() / 20), int(self.res.height() / 5),
                                                     int(self.res.width() / 4), int(self.res.height() / 6))
        self.push_button_setup(maintenance_menu.pushButton_home)

        maintenance_menu.pushButton_bottle.setGeometry(int(self.res.width() * (1 - 1 / 20 - 1 / 4)),
                                                       int(self.res.height() / 5),
                                                       int(self.res.width() / 4),
                                                       int(self.res.height() / 6))
        self.push_button_setup(maintenance_menu.pushButton_bottle)

    def drink_option_menu_setup(self, drink_option_menu):
        """
        Sets up the DrinkOptionMenu
        :param drink_option_menu: DrinkOptionMenu object
        :return:
        """
        self.title_setup(drink_option_menu.label_Title)
        self.bottom_background_setup(drink_option_menu.label_bottom_screen)
        self.bottom_left_button_setup(drink_option_menu.pushButton_return)
        self.bottom_right_button_setup(drink_option_menu.pushButton_confirm)

        self.group_box_setup(drink_option_menu.groupBox_options,
                             drink_option_menu.verticalLayout_options,
                             1)
        self.group_box_setup(drink_option_menu.groupBox_ingredients,
                             drink_option_menu.verticalLayout_ingredients,
                             2,
                             True)

    def mixing_menu_setup(self, mixing_menu):
        """
        Sets up the MixingMenu
        :param mixing_menu: MixingMenu object
        :return:
        """
        self.title_setup(mixing_menu.label_Title)
        self.bottom_background_setup(mixing_menu.label_bottom_screen)
        self.bottom_left_button_setup(mixing_menu.pushButton_return)
        self.group_box_setup(mixing_menu.groupBox_wating, mixing_menu.verticalLayout_waiting, 1)
        self.group_box_setup(mixing_menu.groupBox_done, mixing_menu.verticalLayout_done, 2)
        self.progress_bar_setup(mixing_menu.progressBar)

    def bottle_menu_setup(self, bottle_menu):
        """
        Sets up the BottleMenu
        :param bottle_menu: BottleMenu object
        :return:
        """
        self.title_setup(bottle_menu.label_Title)
        self.bottom_background_setup(bottle_menu.label_bottom_screen)
        self.bottom_left_button_setup(bottle_menu.pushButton_return)
        self.bottom_right_button_setup(bottle_menu.pushButton_confirm)
        self.main_layout_setup(bottle_menu.scrollArea_bottles)
        bottle_menu.scroll_layout = QVBoxLayout(bottle_menu.scrollAreaWidgetContents)
        bottle_menu.scroll_layout.setSpacing(10)
        bottle_menu.scroll_layout.setObjectName("scroll_layout")
        bottle_menu.scroll_layout.setContentsMargins(5, 5, 5, 5)
        bottle_menu.scroll_layout.setAlignment(Qt.AlignCenter)

    def __init_slot_number(self, bottle_layout):
        bottle_layout.slot_number = QLabel()
        bottle_layout.slot_number.setFont(QFont("Times", 15, QFont.Bold))
        # bottle_layout.slot_number.setAlignment(Qt.AlignLeft)
        bottle_layout.slot_number.setText(str(bottle_layout.bottle.get_slot_number()))
        bottle_layout.add_widget_to_superclass(bottle_layout.slot_number)

    def __init_liquid_type(self, bottle_layout):
        bottle_layout.liquid_type_combo_box = QComboBox()
        bottle_layout.liquid_type_combo_box.setStyleSheet(Style.combo_box.value)
        bottle_layout.liquid_type_combo_box.setFixedSize(Style.combo_box_size.value)
        bottle_layout.liquid_type_combo_box.setFont(QFont("Times", 15, QFont.Bold))
        bottle_layout.liquid_type_combo_box.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        bottle_layout.init_combo_box(bottle_layout.liquid_type_combo_box, bottle_layout.bottle.get_liquid_name(),
                                     Liquid.list())
        bottle_layout.liquid_type_combo_box.activated.connect(bottle_layout.new_liquid_type_selected)
        bottle_layout.add_widget_to_superclass(bottle_layout.liquid_type_combo_box)

    def __init_volume_left(self, bottle_layout):
        bottle_layout.volume_left_combo_box = QComboBox()
        bottle_layout.volume_left_combo_box.setStyleSheet(Style.combo_box.value)
        bottle_layout.volume_left_combo_box.setFixedSize(Style.combo_box_size.value)
        bottle_layout.volume_left_combo_box.setFont(QFont("Times", 15, QFont.Bold))
        bottle_layout.volume_left_combo_box.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        bottle_layout.init_combo_box(bottle_layout.volume_left_combo_box, str(bottle_layout.bottle.get_volume_left()),
                                     BottleSize.list())
        bottle_layout.volume_left_combo_box.activated.connect(bottle_layout.new_volume_selected)
        bottle_layout.add_widget_to_superclass(bottle_layout.volume_left_combo_box)

    def bottle_layout_setup(self, bottle_layout):
        self.__init_slot_number(bottle_layout)
        self.__init_liquid_type(bottle_layout)
        self.__init_volume_left(bottle_layout)


def get_screen_resolution(app):
    """
    Function to get the current screen resolution
    :param app: current app
    :return: QRect(0, 0, sc_res.width(), sc_res.height())
    """
    sc_res = app.desktop().screenGeometry()
    sc_res = QRect(0, 0, 1024, 600)
    return sc_res
