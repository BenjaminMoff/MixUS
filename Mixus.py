from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QDialog, QStackedWidget, QPushButton, QHBoxLayout, \
    QVBoxLayout
import sys


class BottleLayoutBuilder:
    slot_number = None
    beverage_name = None
    remaining_volume = None
    edit_button = None

    def with_slot_number(self, number):
        self.slot_number = QLabel()
        self.slot_number.setText(str(number))
        return self

    def with_beverage_name(self, name):
        self.beverage_name = QLabel()
        self.beverage_name.setText(name)
        return self

    def with_remaining_volume(self, volume_oz):
        self.remaining_volume = QLabel()
        self.remaining_volume.setText(str(volume_oz))
        return self

    def with_edit_button_runnable(self, runnable):
        self.edit_button = QPushButton()
        self.edit_button.setFixedSize(100, 150)
        self.edit_button.setText('Modifier')
        #self.edit_button.released.connect(runnable)
        return self

    def build(self):
        layout = QHBoxLayout()

        layout.addWidget(self.slot_number)
        layout.addWidget(self.beverage_name)
        layout.addWidget(self.remaining_volume)
        layout.addWidget(self.edit_button)

        return layout


class BottleMenu(QDialog):
    name = "BottleMenu"

    def __init__(self, manager):
        super(BottleMenu, self).__init__()
        uic.loadUi('BottleMenu.ui', self)

        self.scroll_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setObjectName("scroll_layout")
        self.scroll_layout.setContentsMargins(5, 5, 5, 5)

        for x in range(1, 12):
            bottle_layout = BottleLayoutBuilder() \
                .with_slot_number(x) \
                .with_beverage_name('Alcohol ' + str(x)) \
                .with_remaining_volume(str(2 * x)) \
                .with_edit_button_runnable(None) \
                .build()
            # TODO Ajouter logique pour modifier objets bouteille (runnable du edit button qui ouvre un context menu)

            self.scroll_layout.addLayout(bottle_layout)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MaintenanceMenu"))
        self.pushButton_confirm.released.connect(lambda: manager.switch_window("MainMenu"))



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
            self.windows.update({stack.widget(x).name: x})

    def switch_window(self, window_name, drink=None):
        if window_name == "DrinkOptionMenu":
            self.stack.widget(self.windows.get(window_name)).setup_drink(drink.text())
        self.stack.setCurrentIndex(self.windows.get(window_name))


def init_app():
    stack = QStackedWidget()
    manager = WindowManager()

    stack.addWidget(MainMenu(manager))
    stack.addWidget(MaintenanceMenu(manager))
    stack.addWidget(DrinkOptionMenu(manager))
    stack.addWidget(MixingMenu(manager))
    stack.addWidget(BottleMenu(manager))

    manager.create_windows_dict(stack)
    stack.resize(1920, 1080)
    stack.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)



    init_app()

    sys.exit(app.exec_())
