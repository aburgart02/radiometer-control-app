import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton

from app.threads.device_controller import DeviceController
from app.threads.timer import Timer
from app.widgets.graph_widget import GraphWidget


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_port = ''
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        self.port_buttons = [QPushButton(f'COM{i}', self) for i in range(1, 17)]
        self.plot = None
        self.start_device_button = None
        self.stop_button = None
        self.update_port_button = None
        self.data = []

        self.device_thread = QThread()
        self.device_controller = DeviceController()
        self.device_controller.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_controller.load_data)

        self.init_plot()

        self.timer_thread = QThread()
        self.timer = Timer(self.plot)
        self.timer.moveToThread(self.timer_thread)
        self.timer_thread.started.connect(self.timer.start)

        self.init_control_buttons()
        self.configure_port_buttons()

    def init_plot(self) -> None:
        self.plot = GraphWidget(self, device_controller=self.device_controller)
        self.plot.move(0, 0)

    def start_device(self) -> None:
        self.device_thread.start()
        self.timer_thread.start()
        if self.device_controller.port_error:
            print('Could not open port')
            self.device_thread.quit()
            self.timer_thread.quit()

    def write_data(self):
        with open('../data', 'wb') as f:
            [f.write(s) for s in self.data]

    def stop(self):
        self.timer.stop()
        self.write_data()

    def init_control_buttons(self) -> None:
        self.start_device_button = QPushButton('Start device', self)
        self.start_device_button.move(100, 1000)
        self.start_device_button.resize(140, 60)
        self.start_device_button.clicked.connect(self.start_device)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.move(300, 1000)
        self.stop_button.resize(140, 100)
        self.stop_button.clicked.connect(self.stop)

        self.update_port_button = QPushButton('Update ports list', self)
        self.update_port_button.move(500, 1000)
        self.update_port_button.resize(140, 100)
        self.update_port_button.clicked.connect(self.update_ports)

    def update_ports(self) -> None:
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        self.configure_port_buttons()

    def select_port(self, port: str) -> None:
        self.selected_port = port
        self.device_controller.port = self.selected_port
        self.configure_port_buttons()

    def configure_port_buttons(self) -> None:
        offset = 1000
        for i in range(len(self.port_buttons)):
            if self.port_buttons[i].text() in self.active_ports:
                self.port_buttons[i].move(700, offset)
                self.port_buttons[i].resize(100, 40)
                self.port_buttons[i].disconnect()
                self.port_buttons[i].clicked.connect(lambda x, i=i: self.select_port(self.port_buttons[i].text()))
                self.port_buttons[i].setStyleSheet(f'QPushButton {{background-color: '
                                                   f'{ "#008000" if self.port_buttons[i].text() == self.selected_port else "#FFFFFF"} }}')
                offset += 60
                self.port_buttons[i].show()
            else:
                self.port_buttons[i].hide()
