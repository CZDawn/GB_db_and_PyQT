from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, \
                            qApp, QApplication


class StartUserNameEnteringWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_button_pressed = False

        self.setWindowTitle('Welcome!')
        self.setFixedSize(175, 93)

        self.label = QLabel('Enter username:', self)
        self.label.move(10, 10)
        self.label.setFixedSize(154, 10)

        self.client_name = QLineEdit(self)
        self.client_name.move(10, 30)
        self.client_name.setFixedSize(154, 20)

        self.ok_button = QPushButton('Start', self)
        self.ok_button.move(10, 60)
        self.ok_button.clicked.connect(self.click)

        self.cancel_button = QPushButton('Exit', self)
        self.cancel_button.move(90, 60)
        self.cancel_button.clicked.connect(qApp.exit)

        self.show()

    def click(self):
        if self.client_name.text():
            self.ok_button_pressed = True
            qApp.exit()


if __name__ == '__main__':
    APP = QApplication([])
    start_window_obj = StartUserNameEnteringWindow()
    APP.exec_()

