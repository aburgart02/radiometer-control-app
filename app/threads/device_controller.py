import asyncio
from asyncio import new_event_loop
from queue import Queue

from PyQt5.QtCore import QObject
from serial import SerialException, Serial
from serial_asyncio import open_serial_connection


class DeviceController(QObject):
    def __init__(self):
        super().__init__()
        self.port = ""
        self.baudrate = 9600
        self.channel_data = Queue()
        self.port_error = False

    def load_data(self) -> None:
        loop = new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())

    async def run(self) -> None:
        try:
            serial = Serial(self.port)
            serial.reset_input_buffer()
            serial.close()
            reader, writer = await open_serial_connection(url=self.port, baudrate=self.baudrate)
            while True:
                packet = await reader.readline()
                self.channel_data.put(packet)
        except SerialException:
            self.port_error = True
