from queue import Queue

from PyQt5.QtCore import QObject
from serial import Serial


class DeviceController(QObject):
    def __init__(self):
        super().__init__()
        self.port = ""
        self.baudrate = 9600
        self.channel_data = Queue()
        self.is_running = False

    def stop(self):
        self.is_running = False

    def run(self) -> None:
        self.is_running = True
        serial = Serial(self.port, baudrate=self.baudrate)
        serial.reset_input_buffer()
        while self.is_running:
            packet = serial.readline()
            self.channel_data.put(packet)
        serial.close()
        self.channel_data = Queue()
