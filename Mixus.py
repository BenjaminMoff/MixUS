from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QMenu, QApplication, QLabel, QMainWindow, QDialog, QStackedWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout
from Enums import *
from DataModel import *
from JsonHandler import *
import sys


class BottleLayout:
    slot_number = None
    liquid_type = None
    volume_left = None

    def __init__(self, temp_bottle):
        self.bottle = temp_bottle
        self.__init_slot_number(temp_bottle.get_slot_number())
        self.__init_liquid_type(temp_bottle.get_liquid_type())
        self.__init_volume_left(temp_bottle.get_volume_left())

    def __init_slot_number(self, number):
        self.slot_number = QLabel()
        self.slot_number.setText(str(number))

    def __init_liquid_type(self, liquid_type):
        self.liquid_type = QComboBox()
        self.liquid_type.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.liquid_type.currentIndexChanged.connect(self.update_liquid_type)
        self.update_liquid_type(liquid_type)

    def __init_volume_left(self, volume):
        self.volume_left = QComboBox()
        self.volume_left.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.volume_left.currentIndexChanged.connect(self.update_volume_left)
        self.update_volume_left(volume)

    def update_liquid_type(self, new_liquid_type):
        self.bottle.set_liquid_type(new_liquid_type)
        self.liquid_type.Clear()

        # First item added is the current liquid type
        self.liquid_type.addItem(new_liquid_type)

        # Add other liquid type options
        for liquid in Liquid.list():
            if liquid is not new_liquid_type:
                self.liquid_type.addItem(liquid)

    def update_volume_left(self, new_volume):
        self.bottle.set_volume_left(new_volume)
        self.volume_left.Clear()

        # First item added is the current volume
        self.liquid_type.addItem(new_volume)

        # Add other volume options
        for size in BottleSize.list():
            if size is not new_volume:
                self.liquid_type.addItem(size)


class BottleMenu(QDialog):
    name = "BottleMenu"
    bottles = []
    temp_bottles = []
    bottle_layouts = []
    manager = None

    def __init__(self, manager, bottles):
        super(BottleMenu, self).__init__()
        uic.loadUi('BottleMenu.ui', self)
        self.manager = manager

        self.scroll_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setObjectName("scroll_layout")
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        self.bottles = bottles
        for bottle in bottles:
            temp_bottle = Bottle(bottle.get_slot_number(),
                                 bottle.get_liquid_type(),
                                 bottle.get_volume_left)
            self.temp_bottles.append(temp_bottle)
            bottle_layout = BottleLayout(temp_bottle)
            self.bottle_layouts.append(bottle_layout)
            self.scroll_layout.addLayout(bottle_layout)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MaintenanceMenu"))
        self.pushButton_confirm.released.connect(self.confirm_button_released())
        # TODO ecriture dans persistance

    def confirm_button_released(self):
        # save changes done in the menu to the bottle list accessible by other menus
        self.bottles.clear()
        self.bottles.extend(self.temp_bottles)
        self.manager.switch_window("MainMenu")


class MixingMenu(QDialog):
    name = "MixingMenu"

    def __init__(self, manager):
        super(MixingMenu, self).__init__()
        uic.loadUi('MixingMenu.ui', self)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MainMenu"))
        # TODO Transfert de commandes gcodes(ici ou DrinkOptionMenu) + update status et afficher dans widgets


class DrinkOptionMenu(QDialog):
    name = "DrinkOptionMenu"

    def __init__(self, manager):
        super(DrinkOptionMenu, self).__init__()
        uic.loadUi('DrinkOptionMenu.ui', self)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MainMenu"))
        self.pushButton_confirm.released.connect(lambda: manager.switch_window("MixingMenu"))
        # TODO lancer algorithme de generation de gcode + lancement commandes?

    def setup_drink(self, drink):
        self.label_title.setText(drink)
        # TODO setup image + ingredients


class MaintenanceMenu(QDialog):
    name = "MaintenanceMenu"

    def __init__(self, manager):
        super(MaintenanceMenu, self).__init__()
        uic.loadUi('MaintenanceMenu.ui', self)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MainMenu"))
        self.pushButton_bottle.released.connect(lambda: manager.switch_window("BottleMenu"))
        # TODO update les combobox de bottle menu lors de louverture


class MainMenu(QMainWindow):
    name = "MainMenu"

    def __init__(self, manager):
        super(MainMenu, self).__init__()
        uic.loadUi('MainMenu.ui', self)

        self.pushButton_exit.released.connect(lambda: sys.exit(app.exec_()))
        # TODO Updater les fichiers de persistance a la fermeture
        self.pushButton_maintenance.released.connect(lambda: manager.switch_window("MaintenanceMenu"))

        self.scrollArea_drinklist.setWidgetResizable(True)
        self.scroll_layout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setObjectName(u"scroll_layout")
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        for x in range(0, 10):
            P = QPushButton(self.scrollAreaWidgetContents)
            P.setText(str(x + 1))
            P.setFixedSize(300, 600)
            self.scroll_layout.addWidget(P)
            P.released.connect(lambda drink=P: manager.switch_window("DrinkOptionMenu", drink))
            # TODO passer un drink plutot que le bouton (drink devrait etre un attribut dun drinkButton)


class WindowManager:
    windows = {}
    stack = None

    def create_windows_dict(self, stack):
        self.stack = stack
        for x in range(0, stack.count()):
            self.windows.update({stack.widget(x).string_name: x})

    def switch_window(self, window_name, drink=None):
        if window_name == "DrinkOptionMenu":
            self.stack.widget(self.windows.get(window_name)).setup_drink(drink.text())
        self.stack.setCurrentIndex(self.windows.get(window_name))


def init_app_ui():
    stack = QStackedWidget()
    manager = WindowManager()
    json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)

    bottles = json_handler.load_bottles()
    drinks = json_handler.load_drinks()

    stack.addWidget(MainMenu(manager))
    stack.addWidget(MaintenanceMenu(manager))
    stack.addWidget(DrinkOptionMenu(manager))
    stack.addWidget(MixingMenu(manager))
    stack.addWidget(BottleMenu(manager, bottles))

    manager.create_windows_dict(stack)
    stack.resize(1920, 1080)
    stack.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    init_app_ui()

    sys.exit(app.exec_())
