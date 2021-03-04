from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QLabel, QMainWindow, QDialog, QStackedWidget, QPushButton, \
    QHBoxLayout
from DataModel import *
from JsonHandler import JsonHandler
from Enums import *
from UIManager import *
from SerialCommunication import SerialSynchroniser
import sys


class BottleLayout(QHBoxLayout):
    """
    Layout to allow modification of liquid type and volume of bottles on the machine
    ComboBoxes are used to get user input
    """
    slot_number = None
    liquid_type_combo_box = None
    volume_left_combo_box = None

    def __init__(self, temp_bottle, ui_manager):
        super().__init__()
        self.bottle = temp_bottle
        self.ui_manager = ui_manager

        self.ui_manager.bottle_layout_setup(self)

    def add_widget_to_superclass(self, widget):
        super().addWidget(widget)

    def init_combo_box(self, combo_box, selected_item, items):
        # First item added is selected
        combo_box.addItem(selected_item)

        for item in items:
            if item != selected_item:
                combo_box.addItem(item)

    def new_liquid_type_selected(self):
        self.bottle.set_liquid(Liquid.get_liquid_from_string_name(self.liquid_type_combo_box.currentText()))

    def new_volume_selected(self):
        self.bottle.set_volume_left(int(self.volume_left_combo_box.currentText()))

    def update_layout(self, new_bottle):
        """
        Update the layout to display status of new_bottle
        :param new_bottle: bottle used to update combo boxes
        :return:
        """
        self.bottle = new_bottle
        self.liquid_type_combo_box.clear()
        self.volume_left_combo_box.clear()

        self.init_combo_box(self.liquid_type_combo_box, self.bottle.get_liquid_name(), Liquid.list())
        self.init_combo_box(self.volume_left_combo_box, str(self.bottle.get_volume_left()), BottleSize.list())


class BottleMenu(QDialog):
    """
    Menu to update the software when bottles are changed on the machine
    """
    name = "BottleMenu"
    bottle_manager = []
    temp_bottles = []
    bottle_layouts = {}
    window_manager = None

    def __init__(self, window_manager, ui_manager, bottle_manager):
        super(BottleMenu, self).__init__()
        uic.loadUi(Paths.BOTTLE_MENU.value, self)
        self.window_manager = window_manager
        self.bottle_manager = bottle_manager
        self.ui_manager = ui_manager
        self.ui_manager.bottle_menu_setup(self)
        self.connect_buttons()
        self.bottles_setup()

    def bottles_setup(self):
        for bottle in self.bottle_manager.get_bottles():
            temp_bottle = bottle.copy()
            self.temp_bottles.append(temp_bottle)
            bottle_layout = BottleLayout(temp_bottle, self.ui_manager)
            self.bottle_layouts.update({temp_bottle.get_slot_number(): bottle_layout})
            self.scroll_layout.addLayout(bottle_layout)

    def connect_buttons(self):
        self.pushButton_return.released.connect(lambda: self.window_manager.switch_window("MaintenanceMenu"))
        self.pushButton_confirm.released.connect(self.confirm_button_released)

    # TODO ecriture dans persistance

    def confirm_button_released(self):
        # save changes done in the menu to the bottle list accessible by other menus
        self.bottle_manager.update(self.temp_bottles)
        self.window_manager.switch_window("MainMenu")

    def update_layout(self):

        """
        Method called when the bottle menu is loaded
        Updates each bottle layout with the current content of bottle manager
        :return:
        """
        self.temp_bottles.clear()
        for bottle in self.bottle_manager.get_bottles():
            temp_bottle = bottle.copy()
            self.temp_bottles.append(temp_bottle)
            self.bottle_layouts.get(temp_bottle.get_slot_number()).update_layout(temp_bottle)


class MixingMenu(QDialog):
    name = "MixingMenu"

    def __init__(self, window_manager, ui_manager):
        super(MixingMenu, self).__init__()
        uic.loadUi(Paths.MIXING_MENU.value, self)
        self.ui_manager = ui_manager
        self.pushButton_return.released.connect(lambda: window_manager.switch_window("MainMenu"))
        self.ui_manager.mixing_menu_setup(self)

    def update_layout(self, instructions, drink):
        """
        Method called when the MixingMenu is loaded
        Updates the ingredients and the progressBar for the current drink
        :param instructions: List of instructions to pass to the serial port
        :param drink: Drink that is going to be made
        :return: 
        """""
        self.ui_manager.image_setup(self.label_drinkImage, drink.image_path)
        self.label_Title.setText(drink.name)
        for i in range(0, self.verticalLayout_waiting.count()):
            self.verticalLayout_waiting.itemAt(i).widget().deleteLater()
        ingredient_labels = []

        for ingredient in drink.liquids:
            L = QLabel()
            L.setText(ingredient.string_name)
            L.setFont(QFont("Times", 12))
            ingredient_labels.append(QLabel)
            self.verticalLayout_waiting.addWidget(L)
        self.setup_progress_bar(instructions)

    def setup_progress_bar(self, instructions):
        self.progressBar.setMaximum(len(instructions))

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)


class DrinkOptionMenu(QDialog):
    name = "DrinkOptionMenu"
    drink = None

    def __init__(self, window_manager, ui_manager, drink_manager):
        super(DrinkOptionMenu, self).__init__()
        uic.loadUi(Paths.DRINK_OPTION_MENU.value, self)
        self.window_manager = window_manager
        self.drink_manager = drink_manager
        self.ui_manager = ui_manager

        ui_manager.drink_option_menu_setup(self)

        self.radioButton_normal.toggled.connect(self.is_current_setting_valid)
        self.radioButton_double.toggled.connect(self.is_current_setting_valid)
        self.radioButton_virgin.toggled.connect(self.is_current_setting_valid)

        self.pushButton_return.clicked.connect(lambda: self.window_manager.switch_window("MainMenu"))
        self.pushButton_confirm.released.connect(lambda: self.get_instructions_and_run())

        # TODO lancer algorithme de generation de gcode + lancement commandes?

    def update_layout(self, drink):
        """

        :param drink: selected drink
        :return:
        """
        self.drink = drink
        self.label_Title.setText(self.drink.name)
        self.radioButton_normal.setChecked(True)

        self.ui_manager.image_setup(self.label_drinkImage, self.drink.image_path)

        for i in range(0, self.verticalLayout_ingredients.count()):
            self.verticalLayout_ingredients.itemAt(i).widget().deleteLater()

        for liquid in self.drink.liquids:
            L = QLabel()
            L.setText(str(self.drink.ingredients.get(liquid.string_name)) + " onces de " + liquid.string_name)
            L.setFont(QFont("Times", 12))
            self.verticalLayout_ingredients.addWidget(L)

    # Disable confirm button if the drink cant be made with current settings
    def is_current_setting_valid(self):
        is_valid = (self.radioButton_double.isChecked() and self.is_double_available()) or \
                   (self.radioButton_virgin.isChecked() and self.is_virgin_available()) or \
                   self.radioButton_normal.isChecked()
        self.pushButton_confirm.setEnabled(is_valid)

    def is_double_available(self):
        return self.drink_manager.is_double_available(self.drink)

    def is_virgin_available(self):
        return self.drink_manager.is_virgin_available(self.drink)

    def get_instructions_and_run(self):
        instructions = self.drink_manager.get_instructions(self.drink, self.radioButton_double.isChecked(),
                                                           self.radioButton_virgin.isChecked())
        self.window_manager.switch_window("MixingMenu", self.drink, instructions)


class MaintenanceMenu(QDialog):
    name = "MaintenanceMenu"

    def __init__(self, window_manager, ui_manager):
        super(MaintenanceMenu, self).__init__()
        uic.loadUi(Paths.MAINTENANCE_MENU.value, self)
        self.window_manager = window_manager
        self.pushButton_return.clicked.connect(lambda: self.window_manager.switch_window("MainMenu"))
        self.pushButton_bottle.clicked.connect(lambda: self.window_manager.switch_window("BottleMenu"))

        ui_manager.maintenance_menu_setup(self)
        # TODO faire lenvoi des positions des sliders avec un connect lambda


class MainMenu(QMainWindow):
    name = "MainMenu"

    def __init__(self, window_manager, ui_manager, drink_manager):
        super(MainMenu, self).__init__()
        uic.loadUi(Paths.MAIN_MENU.value, self)
        self.window_manager = window_manager
        self.drink_manager = drink_manager
        self.scroll_layout = QHBoxLayout(self.scrollAreaWidgetContents)

        self.connect_buttons()
        ui_manager.main_menu_setup(self)

        self.update_layout()
        # TODO Updater les fichiers de persistance a la fermeture

    def update_layout(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)
        for drink in self.drink_manager.get_available_drinks():
            button = DrinkButton(self.scrollAreaWidgetContents, drink)
            self.scroll_layout.addWidget(button)
            button.released.connect(
                lambda button_drink=button.drink: self.window_manager.switch_window("DrinkOptionMenu", button_drink))

    def connect_buttons(self):
        self.pushButton_maintenance.clicked.connect(lambda: self.window_manager.switch_window("MaintenanceMenu"))
        self.pushButton_exit.clicked.connect(lambda: sys.exit(app.exec_()))


class DrinkButton(QPushButton):
    def __init__(self, scroll_area_widget_contents, drink):
        super(DrinkButton, self).__init__(scroll_area_widget_contents)
        self.drink = drink
        self.setStyleSheet(GUI.drink_button.value)
        self.setFixedSize(GUI.drink_image_size.value)
        self.setStyleSheet("QPushButton{ background-image: url(" + self.drink.image_path + "); }")


class WindowManager:
    """
    Class responsible to switch between menus and update layouts
    """
    windows = {}
    stack = None

    def __init__(self, stack):
        self.stack = stack

    def append_window(self, window):
        """
        Add the window to the stack
        :param window:
        :return:
        """
        self.stack.addWidget(window)
        window_index = self.stack.count() - 1
        self.windows.update({self.stack.widget(window_index).name: window_index})

    def switch_window(self, window_name, drink=None, instructions=None):
        """
        Switch the window to the given window_name
        :param window_name: Name of the window to switch
        :param drink: Drink object if needed
        :param instructions: Instruction list if needed
        :return:
        """
        if window_name == "DrinkOptionMenu":
            self.stack.widget(self.windows.get(window_name)).update_layout(drink)
        elif window_name == "MainMenu":
            self.stack.widget(self.windows.get(window_name)).update_layout()
        elif window_name == "BottleMenu":
            self.stack.widget(self.windows.get(window_name)).update_layout()
        elif window_name == "MixingMenu":
            self.stack.widget(self.windows.get(window_name)).update_layout(instructions, drink)
        self.stack.setCurrentIndex(self.windows.get(window_name))


def init_app_ui(app):
    """
    Functions that initiates the app
    :param app: current app
    :return:
    """
    stack = QStackedWidget()
    window_manager = WindowManager(stack)
    json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)

    bottle_manager = BottleManager(json_handler)
    drink_manager = DrinkManager(json_handler, bottle_manager)
    ui_manager = UIManager(window_manager, app)

    window_manager.append_window(MainMenu(window_manager, ui_manager, drink_manager))
    window_manager.append_window(MaintenanceMenu(window_manager, ui_manager))
    window_manager.append_window(DrinkOptionMenu(window_manager, ui_manager, drink_manager))
    window_manager.append_window(MixingMenu(window_manager, ui_manager))
    window_manager.append_window(BottleMenu(window_manager, ui_manager, bottle_manager))

    stack.resize(ui_manager.res.width(), ui_manager.res.height())

    stack.show()  # TODO : put in full screen


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    init_app_ui(app)
    sys.exit(app.exec_())
