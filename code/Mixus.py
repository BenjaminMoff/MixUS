from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QComboBox, QLabel, QMainWindow, QDialog, QStackedWidget, QPushButton, \
    QHBoxLayout, QLayout, QWidget
from DataModel import *
from JsonHandler import JsonHandler
from Enums import *
from UIManager import *
from LimitSwitch import LimitSwitch
from SerialCommunication import SerialSynchroniser
from Popup import Popup
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
    progress = pyqtSignal(int)
    checkpoint_reached = pyqtSignal(str)
    instruction_completed = pyqtSignal()
    drink_completed = pyqtSignal()

    def __init__(self, window_manager, ui_manager, bottle_manager):
        super(MixingMenu, self).__init__()
        uic.loadUi(Paths.MIXING_MENU.value, self)
        self.ui_manager = ui_manager
        self.window_manager = window_manager
        self.bottle_manager = bottle_manager
        self.connect_buttons()
        self.ui_manager.mixing_menu_setup(self)
        self.serial_synchroniser = SerialSynchroniser()
        self.drink = None
        self.cup_switch = LimitSwitch()

    def connect_buttons(self):
        self.pushButton_return.released.connect(self.return_button_action)
        self.progress.connect(self.update_progress_bar)
        self.checkpoint_reached.connect(self.update_ingredients)
        self.drink_completed.connect(self.popup)

    def update_layout(self, instructions, checkpoints, drink):
        """
        Method called when the MixingMenu is loaded
        Updates the ingredients and the progressBar for the current drink
        :param instructions: List of instructions to pass to the serial port
        :param checkpoints: Checkpoints of the instruction list to update ingredients 
        :param drink: Drink that is going to be made
        :return: 
        """""
        self.ui_manager.image_setup(self.label_drinkImage, drink.image_path)
        self.label_Title.setText(drink.name)
        self.drink = drink
        self.progressBar.setValue(0)
        self.ingredient_labels = {}

        for i in range(0, self.verticalLayout_waiting.count()):
            self.verticalLayout_waiting.itemAt(i).widget().deleteLater()
        for i in range(0, self.verticalLayout_done.count()):
            self.verticalLayout_done.itemAt(i).widget().deleteLater()

        for ingredient in drink.liquids:
            label = QLabel()
            label.setText(ingredient.string_name)
            label.setFont(QFont("Times", 12))
            self.ingredient_labels.update({ingredient.string_name: label})
            self.verticalLayout_waiting.addWidget(label)

        if self.serial_synchroniser.can_start_communication():
            self.start_mixing(instructions, checkpoints)
        else:
            connect_and_retry(lambda: self.start_mixing(instructions, checkpoints))

    def start_mixing(self, instructions, checkpoints):
        self.serial_synchroniser.track_progress(self, checkpoints, len(instructions))
        self.serial_synchroniser.begin_communication(instructions)

    def return_button_action(self):
        self.serial_synchroniser.abort_communication()
        if self.serial_synchroniser.can_start_communication():
            self.end_mixing(drink_canceled=True)
        else:
            connect_and_retry(lambda: self.end_mixing(drink_canceled=True))

    def end_mixing(self, drink_canceled=False):
        self.serial_synchroniser.begin_communication(GCodeGenerator.serve_cup())
        self.popup(drink_canceled)

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)

    def update_ingredients(self, liquid_name):
        label = self.ingredient_labels.get(liquid_name)
        self.verticalLayout_waiting.removeWidget(label)
        self.verticalLayout_done.addWidget(label)
        self.bottle_manager.pour(liquid_name, self.drink.ingredients.get(liquid_name))

    def popup(self, drink_canceled=False):
        Popup.drink_completed(self.load_main_menu, drink_canceled=drink_canceled)

    def load_main_menu(self):
        if not self.cup_switch.is_activated(expected=False):
            if self.serial_synchroniser.can_start_communication():
                self.serial_synchroniser.track_progress(self.window_manager.get_window("MainMenu"))
                self.serial_synchroniser.begin_communication(GCodeGenerator.insert_cup())
                self.window_manager.switch_window("MainMenu", in_motion=True)
            else:
                connect_and_retry(self.popup())
        else:
            Popup.drink_completed(self.load_main_menu)


class DrinkOptionMenu(QDialog):
    name = "DrinkOptionMenu"
    progress = pyqtSignal(int)
    checkpoint_reached = pyqtSignal(str)
    instruction_completed = pyqtSignal()
    in_motion = False
    drink = None

    def __init__(self, window_manager, ui_manager, drink_manager):
        super(DrinkOptionMenu, self).__init__()
        uic.loadUi(Paths.DRINK_OPTION_MENU.value, self)
        self.window_manager = window_manager
        self.drink_manager = drink_manager
        self.ui_manager = ui_manager
        self.serial_synchroniser = SerialSynchroniser()
        self.cup_switch = LimitSwitch()

        ui_manager.drink_option_menu_setup(self)

        self.radioButton_normal.toggled.connect(self.update_ingredients)
        self.radioButton_double.toggled.connect(self.update_ingredients)
        self.radioButton_virgin.toggled.connect(self.update_ingredients)

        self.pushButton_return.released.connect(self.return_button_action)
        self.pushButton_confirm.released.connect(self.load_mixing_menu)
        self.instruction_completed.connect(self.__on_instruction_completed)

    def update_layout(self, drink):
        self.drink = drink
        self.label_Title.setText(self.drink.name.replace("_", " "))
        self.radioButton_normal.setChecked(True)
        self.ui_manager.image_setup(self.label_drinkImage, self.drink.image_path)
        self.request_cup()
        self.update_ingredients()

    def return_button_action(self):
        if self.serial_synchroniser.can_start_communication():
            self.load_main_menu()
        else:
            connect_and_retry(self.load_main_menu)

    def request_cup(self):
        if self.serial_synchroniser.can_start_communication():
            self.__send_command(GCodeGenerator.wait_for_cup())
        else:
            connect_and_retry(lambda: self.__send_command(GCodeGenerator.wait_for_cup()))

    def __send_command(self, instructions):
        self.pushButton_return.setEnabled(False)
        self.pushButton_confirm.setEnabled(False)
        self.in_motion = True
        self.serial_synchroniser.track_progress(self)
        self.serial_synchroniser.begin_communication(instructions)

    def __on_instruction_completed(self):
        self.pushButton_return.setEnabled(True)
        self.pushButton_confirm.setEnabled(True)
        self.in_motion = False
        self.update_ingredients()

    def update_ingredients(self):
        self.is_current_setting_valid()

        for i in range(0, self.verticalLayout_ingredients.count()):
            self.verticalLayout_ingredients.itemAt(i).widget().deleteLater()

        flag = 0
        for liquid in list(self.drink.liquids):
            l = LiquidLabel(liquid, self.drink.ingredients.get(liquid.string_name))
            vol = self.drink.ingredients.get(l.liquid.string_name)
            if self.radioButton_normal.isChecked():
                l.update_volume(vol)
            elif self.radioButton_double.isChecked():
                if l.liquid.is_alcoholized:
                    l.update_volume(vol * 2)
                elif l.liquid.is_filler:
                    volume_to_remove = self.drink.alcohol_volume()
                    l.update_volume(
                        vol - volume_to_remove)
                else:
                    l.update_volume(vol)
            elif self.radioButton_virgin.isChecked():
                if l.liquid.is_alcoholized:
                    flag = 1
                elif l.liquid.is_filler:
                    volume_to_add = self.drink.alcohol_volume()
                    l.update_volume(vol + volume_to_add)
                else:
                    l.update_volume(vol)

            if flag == 0:
                self.verticalLayout_ingredients.addWidget(l)
            else:
                flag = 0

    # Disable confirm button if the drink cant be made with current settings
    def is_current_setting_valid(self):
        is_valid = not self.in_motion and \
                   ((self.radioButton_double.isChecked() and self.is_double_available()) or
                    (self.radioButton_virgin.isChecked() and self.is_virgin_available()) or
                    self.radioButton_normal.isChecked())
        self.pushButton_confirm.setEnabled(is_valid)

    def is_double_available(self):
        return self.drink_manager.is_double_available(self.drink)

    def is_virgin_available(self):
        return self.drink_manager.is_virgin_available(self.drink)

    def load_mixing_menu(self):
        if self.cup_switch.is_activated():
            instructions, liquid_checkpoints = self.drink_manager.get_instructions(self.drink,
                                                                                   self.radioButton_double.isChecked(),
                                                                                   self.radioButton_virgin.isChecked())

            self.window_manager.switch_window("MixingMenu",
                                              drink=self.drink,
                                              instructions=instructions,
                                              checkpoints=liquid_checkpoints)
        else:
            Popup.no_cup_error(self.load_mixing_menu)

    def load_main_menu(self):
        self.serial_synchroniser.track_progress(self.window_manager.get_window("MainMenu"))
        self.serial_synchroniser.begin_communication(GCodeGenerator.insert_cup())
        self.window_manager.switch_window("MainMenu", in_motion=True)


class MaintenanceMenu(QDialog):
    name = "MaintenanceMenu"
    progress = pyqtSignal(int)
    checkpoint_reached = pyqtSignal(str)
    instruction_completed = pyqtSignal()
    is_home = True

    def __init__(self, window_manager, ui_manager):
        super(MaintenanceMenu, self).__init__()
        uic.loadUi(Paths.MAINTENANCE_MENU.value, self)
        self.window_manager = window_manager
        self.serial_synchroniser = SerialSynchroniser()
        self.instruction_completed.connect(self.on_instruction_completed)
        self.pushButton_return.clicked.connect(lambda: self.change_window("MainMenu"))
        self.pushButton_bottle.clicked.connect(lambda: self.change_window("BottleMenu"))
        self.pushButton_send.clicked.connect(self.send_button_action)
        self.pushButton_home.clicked.connect(self.home_button_action)
        self.slider.valueChanged.connect(self.label_axis_update)
        self.comboBox_axis.currentIndexChanged.connect(lambda: self.slider_update(self.comboBox_axis.currentText()))
        self.combobox_axis_setup()

        ui_manager.maintenance_menu_setup(self)

    def combobox_axis_setup(self):
        self.comboBox_axis.addItem('X')
        self.comboBox_axis.addItem('Y')
        self.comboBox_axis.addItem('Z')
        self.label_axis.setText('0')

    def slider_update(self, axis):
        if axis == 'X':
            self.slider.setMaximum(GCodeGenerator.max_x)
        elif axis == 'Y':
            self.slider.setMaximum(GCodeGenerator.max_y)
        elif axis == 'Z':
            self.slider.setMaximum(GCodeGenerator.max_z)
        else:
            raise ValueError("Axis given was not X, Y or Z")
        self.slider.setValue(0)

    def label_axis_update(self):
        self.label_axis.setText(str(self.slider.value()))

    def send_button_action(self):
        self.is_home = False
        instructions = GCodeGenerator.move_axis(int(self.label_axis.text()), self.comboBox_axis.currentText())
        if self.serial_synchroniser.can_start_communication():
            self.__send_command(instructions)
        else:
            connect_and_retry(lambda: self.__send_command(instructions))

    def on_instruction_completed(self):
        self.pushButton_send.setEnabled(True)
        self.pushButton_home.setEnabled(True)
        self.pushButton_return.setEnabled(True)
        self.pushButton_bottle.setEnabled(True)

    def home_button_action(self):
        self.is_home = True
        instructions = GCodeGenerator.home()
        if self.serial_synchroniser.can_start_communication():
            self.__send_command(instructions)
        else:
            connect_and_retry(lambda: self.__send_command(instructions))

    def change_window(self, window_name):
        if not self.is_home:
            Popup.home_before_leaving(self.home_button_action)
        else:
            self.window_manager.switch_window(window_name)

    def __send_command(self, instructions):
        self.pushButton_send.setEnabled(False)
        self.pushButton_home.setEnabled(False)
        self.pushButton_return.setEnabled(False)
        self.pushButton_bottle.setEnabled(False)
        self.serial_synchroniser.track_progress(self)
        self.serial_synchroniser.begin_communication(instructions)


class MainMenu(QMainWindow):
    name = "MainMenu"
    progress = pyqtSignal(int)
    checkpoint_reached = pyqtSignal(str)
    instruction_completed = pyqtSignal()

    def __init__(self, window_manager, ui_manager, drink_manager):
        super(MainMenu, self).__init__()
        uic.loadUi(Paths.MAIN_MENU.value, self)
        self.window_manager = window_manager
        self.drink_manager = drink_manager
        self.scroll_layout = QHBoxLayout(self.scrollAreaWidgetContents)

        self.connect_buttons()
        self.instruction_completed.connect(self.__on_instruction_completed)
        ui_manager.main_menu_setup(self)

        self.update_layout()

    def update_layout(self, in_motion=False):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().deleteLater()
        for drink in self.drink_manager.get_available_drinks():
            drink_button = DrinkButton(self.scrollAreaWidgetContents, drink)
            self.scroll_layout.addWidget(drink_button)
            drink_button.button.released.connect(
                lambda button_drink=drink_button.drink: self.window_manager.switch_window("DrinkOptionMenu",
                                                                                          drink=button_drink))
        if in_motion:
            self.enable_buttons(False)

    def connect_buttons(self):
        self.pushButton_maintenance.clicked.connect(lambda: self.window_manager.switch_window("MaintenanceMenu"))
        self.pushButton_exit.clicked.connect(lambda: sys.exit(app.exec_()))

    def enable_buttons(self, enable=True):
        self.pushButton_maintenance.setEnabled(enable)
        self.pushButton_exit.setEnabled(enable)

        drink_buttons = (self.scroll_layout.itemAt(i) for i in range(self.scroll_layout.count()))
        for drink_button in drink_buttons:
            drink_button.widget().setEnabled(enable)

    def __on_instruction_completed(self):
        self.enable_buttons()


class DrinkButton(QWidget):
    def __init__(self, scroll_area_widget_contents, drink):
        super(DrinkButton, self).__init__(scroll_area_widget_contents)
        self.drink = drink
        self.button = QPushButton()
        self.label = QLabel(drink.name.replace("_", " "))

        self.button.setStyleSheet("QPushButton{ background-image: url(" + self.drink.image_path + "); }")
        self.button.setFixedSize(Style.drink_button_image_size.value)

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Times", 9, QFont.Bold))

        self.setFixedSize(Style.drink_button_size.value)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


class LiquidLabel(QLabel):
    def __init__(self, liquid, volume):
        super(LiquidLabel, self).__init__()
        self.liquid = liquid
        self.volume = volume
        self.setText(str(volume) + " onces de " + str.lower(self.liquid.string_name))
        self.setFont(QFont("Times", 12))

    def update_volume(self, volume):
        self.volume = volume
        self.setText(str(volume) + " onces de " + str.lower(self.liquid.string_name))


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

    def get_window(self, window_name):
        return self.stack.widget(self.windows.get(window_name))

    def switch_window(self, window_name, drink=None, instructions=None, checkpoints=None, in_motion=False):
        """
        Switch the window to the given window_name
        :param window_name: Name of the window to switch
        :param drink: Drink object if needed
        :param instructions: Instruction list if needed
        :param checkpoints: Checkpoints of instruction list if needed
        :param in_motion: Indicate if the machine is in motion
        :return:
        """
        if window_name == "DrinkOptionMenu":
            self.get_window(window_name).update_layout(drink)
        elif window_name == "MainMenu":
            self.get_window(window_name).update_layout(in_motion)
        elif window_name == "BottleMenu":
            self.get_window(window_name).update_layout()
        elif window_name == "MixingMenu":
            self.get_window(window_name).update_layout(instructions, checkpoints, drink)
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
    window_manager.append_window(MixingMenu(window_manager, ui_manager, bottle_manager))
    window_manager.append_window(BottleMenu(window_manager, ui_manager, bottle_manager))

    stack.resize(ui_manager.res.width(), ui_manager.res.height())

    init_hardware(window_manager.get_window("MainMenu"))
    window_manager.switch_window("MainMenu", in_motion=True)

    stack.show()  # FullScreen()


def init_hardware(first_menu):
    serial_synchroniser = SerialSynchroniser()
    if serial_synchroniser.can_start_communication():
        initial_machine_homing(first_menu)
    else:
        Popup.serial_port_error(lambda: connect_and_retry(lambda: initial_machine_homing(first_menu)))


def initial_machine_homing(first_menu):
    serial_synchroniser = SerialSynchroniser()
    serial_synchroniser.begin_communication(GCodeGenerator.home())
    serial_synchroniser.track_progress(first_menu)


def connect_and_retry(runnable):
    serial_synchroniser = SerialSynchroniser()
    serial_synchroniser.set_serial_port()
    if serial_synchroniser.can_start_communication():
        runnable()
    else:
        Popup.serial_port_error(lambda: connect_and_retry(runnable))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    init_app_ui(app)
    sys.exit(app.exec_())
