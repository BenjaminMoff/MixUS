from PyQt5.QtWidgets import QMessageBox, QPushButton
from LimitSwitch import LimitSwitch
from PyQt5.QtGui import QFont


class Popup:

    @staticmethod
    def __default_popup():
        msg = QMessageBox()
        msg.setWindowTitle("Mixus")
        msg.setModal(True)
        # TODO : popup stylesheet
        #msg.setStyleSheet("QLabel{min-width: 200px; min-height: 100px;}")
        msg.setFont(QFont("Times", 15, QFont.Bold))
        return msg

    @staticmethod
    def __execute_action_and_close(popup, action):
        popup.done(0)
        action()
        pass

    @staticmethod
    def drink_completed(cup_removed_action):
        # TODO: Replace button with limit switch(close when cup removed)
        msg = Popup.__default_popup()
        msg.setText("Bonne swince!")
        LimitSwitch().execute_when_deactivated(lambda: Popup.__execute_action_and_close(msg, cup_removed_action))
        msg.exec_()

    @staticmethod
    def serial_port_error(retry_action):
        # TODO: Replace button with limit switch(close when cup removed)
        msg = Popup.__default_popup()
        msg.setText("Connection avec le barman perdue")
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Retry)
        #msg.buttonClicked.connect(retry_action)
        msg.buttonClicked.connect(lambda: Popup.__execute_action_and_close(msg, retry_action))
        msg.exec()

    @staticmethod
    def no_cup_error(cup_detected_action):
        msg = Popup.__default_popup()
        msg.setText("Veuillez insérer un verre")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.buttonClicked.connect(LimitSwitch().cancel())
        LimitSwitch().execute_when_activated(cup_detected_action)
        msg.exec_()

    @staticmethod
    def home_before_leaving(home_action):
        msg = Popup.__default_popup()
        msg.setText("Veuillez home avant de quitter ce menu")
        msg.setIcon(QMessageBox.Warning)
        home_button = QPushButton('Home')
        msg.addButton(home_button, QMessageBox.YesRole)
        msg.setStandardButtons(QMessageBox.Cancel)
        home_button.clicked.connect(home_action)
        msg.exec_()