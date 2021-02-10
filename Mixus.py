from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QStackedWidget, QPushButton, QHBoxLayout, QWidget
import sys


class BottleMenu(QDialog):
    name = "BottleMenu"

    def __init__(self, manager):
        super(BottleMenu, self).__init__()
        uic.loadUi('BottleMenu.ui', self)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MaintenanceMenu"))
        self.pushButton_confirm.released.connect(lambda: manager.switch_window("MainMenu"))
        #TODO Ajouter logique pour modifier objets bouteille (reecrire dans fichier persistance lors de la fermeture)


class MixingMenu(QDialog):
    name = "MixingMenu"

    def __init__(self, manager):
        super(MixingMenu, self).__init__()
        uic.loadUi('MixingMenu.ui', self)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MainMenu"))
        #TODO Transfert de commandes gcodes(ici ou DrinkOptionMenu) + update status et afficher dans widgets


class DrinkOptionMenu(QDialog):
    name = "DrinkOptionMenu"

    def __init__(self, manager):
        super(DrinkOptionMenu, self).__init__()
        uic.loadUi('DrinkOptionMenu.ui', self)

        self.pushButton_return.released.connect(lambda: manager.switch_window("MainMenu"))
        self.pushButton_confirm.released.connect(lambda: manager.switch_window("MixingMenu"))
        #TODO lancer algorithme de generation de gcode + lancement commandes?

    def setup_drink(self, drink):
        self.label_title.setText(drink)
        #TODO setup image + ingredients


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
        #TODO Updater les fichiers de persistance a la fermeture
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
            #TODO passer un drink plutot que le bouton (drink devrait etre un attribut dun drinkButton)


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
