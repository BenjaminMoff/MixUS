from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QMenu, QApplication, QLabel, QMainWindow, QDialog, QStackedWidget, QPushButton, \
    QHBoxLayout, QVBoxLayout
from Enums import *
from DataModel import *
from JsonHandler import *
import sys


class BottleLayout(QHBoxLayout):
    slot_number = None
    liquid_type = None
    volume_left = None

    def __init__(self, temp_bottle):
        super().__init__()
        self.bottle = temp_bottle
        self.__init_slot_number(temp_bottle.get_slot_number())
        self.__init_liquid_type(temp_bottle.get_liquid_name())
        self.__init_volume_left(temp_bottle.get_volume_left())

    def __init_slot_number(self, number):
        self.slot_number = QLabel()
        self.slot_number.setText(str(number))
        super().addWidget(self.slot_number)

    def __init_liquid_type(self, liquid_type_name):
        self.liquid_type = QComboBox()
        self.liquid_type.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.__init_combo_box(self.liquid_type, liquid_type_name, Liquid.list())
        self.liquid_type.activated.connect(self.new_liquid_type_selected)
        super().addWidget(self.liquid_type)

    def __init_volume_left(self, volume):
        self.volume_left = QComboBox()
        self.volume_left.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.__init_combo_box(self.volume_left, str(volume), BottleSize.list())
        self.volume_left.activated.connect(self.new_volume_selected)
        super().addWidget(self.volume_left)

    def __init_combo_box(self, combo_box, selected_item, items):
        # First item added is selected
        combo_box.addItem(selected_item)

        for item in items:
            if item != selected_item:
                combo_box.addItem(item)

    def new_liquid_type_selected(self):
        self.bottle.set_liquid(Liquid.get_liquid_from_string_name(self.liquid_type.currentText()))

    def new_volume_selected(self):
        self.bottle.set_volume_left(int(self.volume_left.currentText()))

    def update_layout(self, new_bottle):
        self.bottle = new_bottle
        self.liquid_type.clear()
        self.volume_left.clear()

        self.__init_combo_box(self.liquid_type, self.bottle.get_liquid_name(), Liquid.list())
        self.__init_combo_box(self.volume_left, str(self.bottle.get_volume_left()), BottleSize.list())


class BottleMenu(QDialog):
    name = "BottleMenu"
    bottle_manager = []
    temp_bottles = []
    bottle_layouts = {}
    manager = None

    def __init__(self, window_manager, bottle_manger):
        super(BottleMenu, self).__init__()
        uic.loadUi('BottleMenu.ui', self)
        self.manager = window_manager

        self.scroll_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setObjectName("scroll_layout")
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        self.bottle_manager = bottle_manger
        for bottle in bottle_manger.get_bottles():
            temp_bottle = bottle.copy()
            self.temp_bottles.append(temp_bottle)
            bottle_layout = BottleLayout(temp_bottle)
            self.bottle_layouts.update({temp_bottle.get_slot_number(): bottle_layout})
            self.scroll_layout.addLayout(bottle_layout)

        self.pushButton_return.released.connect(lambda: window_manager.switch_window("MaintenanceMenu"))
        self.pushButton_confirm.released.connect(self.confirm_button_released)
        # TODO ecriture dans persistance

    def confirm_button_released(self):
        # save changes done in the menu to the bottle list accessible by other menus
        self.bottle_manager.update(self.temp_bottles)
        self.manager.switch_window("MainMenu")

    # TODO use bottle manager instead
    def update_layout(self):
        self.temp_bottles.clear()
        for bottle in self.bottle_manager.get_bottles():
            temp_bottle = bottle.copy()
            self.temp_bottles.append(temp_bottle)
            self.bottle_layouts.get(temp_bottle.get_slot_number).update_layout(temp_bottle)


class MixingMenu(QDialog):
    name = "MixingMenu"

    def __init__(self, window_manager):
        super(MixingMenu, self).__init__()
        uic.loadUi('MixingMenu.ui', self)

        self.pushButton_return.released.connect(lambda: window_manager.switch_window("MainMenu"))
        # TODO Transfert de commandes gcodes(ici ou DrinkOptionMenu) + update status et afficher dans widgets


class DrinkOptionMenu(QDialog):
    name = "DrinkOptionMenu"

    def __init__(self, window_manager):
        super(DrinkOptionMenu, self).__init__()
        uic.loadUi('DrinkOptionMenu.ui', self)

        self.pushButton_return.released.connect(lambda: window_manager.switch_window("MainMenu"))
        self.pushButton_confirm.released.connect(lambda: window_manager.switch_window("MixingMenu"))
        # TODO lancer algorithme de generation de gcode + lancement commandes?

    def setup_drink(self, drink):
        self.label_title.setText(drink)
        # TODO setup image + ingredients


class MaintenanceMenu(QDialog):
    name = "MaintenanceMenu"

    def __init__(self, window_manager):
        super(MaintenanceMenu, self).__init__()
        uic.loadUi('MaintenanceMenu.ui', self)

        self.pushButton_return.released.connect(lambda: window_manager.switch_window("MainMenu"))
        self.pushButton_bottle.released.connect(lambda: window_manager.switch_window("BottleMenu"))
        # TODO update les combobox de bottle menu lors de louverture


class MainMenu(QMainWindow):
    name = "MainMenu"

    def __init__(self, window_manager, drink_manager):
        super(MainMenu, self).__init__()
        uic.loadUi('MainMenu.ui', self)
        self.window_manager = window_manager
        self.drink_manager = drink_manager

        self.pushButton_exit.released.connect(lambda: sys.exit(app.exec_()))
        # TODO Updater les fichiers de persistance a la fermeture
        self.pushButton_maintenance.released.connect(lambda: window_manager.switch_window("MaintenanceMenu"))

        self.scrollArea_drinklist.setWidgetResizable(True)
        self.scroll_layout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setObjectName("scroll_layout")
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.update_layout()

    def update_layout(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)
        for drink in self.drink_manager.get_available_drinks():
            P = DrinkButton(self.scrollAreaWidgetContents, drink)
            P.setFixedSize(300, 600)
            self.scroll_layout.addWidget(P)
            P.released.connect(lambda drink=P: self.window_manager.switch_window("DrinkOptionMenu", drink))
            # TODO passer un drink plutot que le bouton (drink devrait etre un attribut dun drinkButton)


class DrinkButton(QPushButton):
    def __init__(self, scrollAreaWidgetContents, drink):
        super(DrinkButton, self).__init__(scrollAreaWidgetContents)
        self.drink = drink
        self.setText(self.drink.name)


class WindowManager:
    windows = {}
    stack = None

    def __init__(self, stack):
        self.stack = stack

    def append_window(self, window):
        self.stack.addWidget(window)
        window_index = self.stack.count() - 1
        self.windows.update({self.stack.widget(window_index).name: window_index})

    def switch_window(self, window_name, drink=None):
        if window_name == "DrinkOptionMenu":
            self.stack.widget(self.windows.get(window_name)).setup_drink(drink.text())
        elif window_name == "MainMenu":
            self.stack.widget(self.windows.get(window_name)).update_layout()
        self.stack.setCurrentIndex(self.windows.get(window_name))


def init_app_ui():
    stack = QStackedWidget()
    window_manager = WindowManager(stack)
    json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)

    bottle_manager = BottleManager(json_handler)
    drink_manager = DrinkManager(json_handler, bottle_manager)

    window_manager.append_window(MainMenu(window_manager, drink_manager))
    window_manager.append_window(MaintenanceMenu(window_manager))
    window_manager.append_window(DrinkOptionMenu(window_manager))
    window_manager.append_window(MixingMenu(window_manager))
    window_manager.append_window(BottleMenu(window_manager, bottle_manager))

    stack.resize(1920, 1080)
    stack.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    init_app_ui()

    sys.exit(app.exec_())
