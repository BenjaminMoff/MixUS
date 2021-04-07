from PyQt5.QtWidgets import QMessageBox, QPushButton
from LimitSwitch import LimitSwitch
from PyQt5.QtGui import QFont


class Popup:

    @staticmethod
    def __default_popup():
        """
        :return: QMessageBox with default popup aesthetics
        """
        msg = QMessageBox()
        msg.setWindowTitle("Mixus")
        msg.setModal(True)
        msg.setFont(QFont("Times", 15, QFont.Bold))
        return msg

    @staticmethod
    def __execute_action_and_close(popup, action):
        """
        :param popup: (QMessageBox) popup to be closed
        :param action: (runnable) function to run before closing popup
        :return:
        """
        popup.done(0)
        action()
        pass

    @staticmethod
    def drink_completed(cup_removed_action, drink_canceled=False):
        """
        :param home_action: (runnable) function to run when home button clicked
        :param drink_canceled: (runnable) function to run when home button clicked
        :return: dsiplay a popup window asking user to home the machine
        """
        msg = Popup.__default_popup()
        msg.setIcon(QMessageBox.Information)
        if drink_canceled:
            msg.setText("Annulation de la commande")
        else:
            msg.setText("Bonne swince!")
        msg.setInformativeText("Veuillez récupérer votre verre")
        msg.exec_()
        LimitSwitch().execute_when_deactivated(lambda: Popup.__execute_action_and_close(msg, cup_removed_action))

    @staticmethod
    def serial_port_error(retry_action):
        """
        :param retry_action: (runnable) function to run when retry button is clicked
        :return: dsiplay a popup window indicating that the serial communication is not available
        """
        msg = Popup.__default_popup()
        msg.setText("Connection avec le barman perdue")
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Retry)
        msg.buttonClicked.connect(lambda: Popup.__execute_action_and_close(msg, retry_action))
        msg.exec()

    @staticmethod
    def no_cup_error(retry_action):
        """
        :param retry_action: (runnable) function to run when retry button is clicked
        :return: dsiplay a popup window asking user to insert a cup in the machine
        """
        msg = Popup.__default_popup()
        msg.setText("Veuillez insérer votre verre")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Retry)
        msg.buttonClicked.connect(retry_action)
        msg.exec_()

    @staticmethod
    def home_before_leaving(home_action):
        """
        :param home_action: (runnable) function to run when home button is clicked
        :return: dsiplay a popup window asking user to home the machine
        """
        msg = Popup.__default_popup()
        msg.setText("Veuillez home avant de quitter ce menu")
        msg.setIcon(QMessageBox.Warning)
        home_button = QPushButton('Home')
        msg.addButton(home_button, QMessageBox.YesRole)
        msg.setStandardButtons(QMessageBox.Cancel)
        home_button.clicked.connect(home_action)
        msg.exec_()