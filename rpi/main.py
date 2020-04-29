import struct
import threading
from abc import ABC, abstractmethod
from enum import Enum
from threading import Thread
from time import sleep
from typing import Callable

import mido
import pyudev
import serial
from mido.backends.rtmidi import Input
from pyudev import Device
from serial import SerialException, Serial

SERIAL_PORT = '/dev/ttyACM0'
MIDI_PORT = 'CASIO USB-MIDI:CASIO USB-MIDI MIDI 1 20:0'
ARDUINO_ATTR = dict(idVendor="2341", idProduct="0043", port='/dev/ttyACM0')
PIANO_ATTR = dict(idVendor="07cf", idProduct="6803", port='/dev/snd/midiC1D0')


class DataPacket(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def pack(self):
        pass


class Note(DataPacket):
    def __init__(self, is_on: bool, note: int, velocity: int):
        super().__init__()
        self.is_on = is_on
        self.note = note
        self.velocity = velocity

    def pack(self):
        return struct.pack('>?BB', self.is_on, self.note - 21, self.velocity)


class Meta(DataPacket):
    def __init__(self, piano_is_on: bool):
        super().__init__()
        self.piano_is_on = piano_is_on

    def pack(self):
        return struct.pack('>?', self.piano_is_on)


class PacketType(Enum):
    meta = 1
    data = 2


class Packet:
    def __init__(self, packet_type: PacketType, data_packet: DataPacket):
        self.packet_type = packet_type
        self.data_packet = data_packet

    def pack(self):
        return struct.pack('>B', self.packet_type.value) + self.data_packet.pack()


Callback = Callable[[Note], None]


class USBDevice:
    def __init__(self, action: str, name: str):
        self.action = action
        self.name = name

    def __repr__(self):
        return f'{self.__class__.__name__}: {repr(self.__dict__)}'


def is_arduino(device: Device):
    return device.properties.get('ID_VENDOR_ID') == ARDUINO_ATTR['idVendor'] and \
           device.properties.get('ID_MODEL_ID') == ARDUINO_ATTR['idProduct'] and \
           device.properties.get('DEVNAME') == ARDUINO_ATTR['port']


def is_midi(device: Device):
    return device.properties.get('DEVNAME') == PIANO_ATTR['port']


class USBObserver:
    def __init__(self, fn: Callable[[USBDevice], None]):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.__observer = None
        self.__callback = fn

    def __repr__(self):
        return f'{self.__class__.__name__}: {repr(self.__dict__)}'

    def run(self, **kwargs):
        if 'filter_by' in kwargs:
            self.monitor.filter_by(kwargs['filter_by'])
        self.__observer = pyudev.MonitorObserver(self.monitor, callback=self.observer)
        self.__observer.start()

    def stop(self):
        if self.__observer is None:
            return
        self.__observer.stop()

    def observer(self, device: Device):
        if is_arduino(device):
            name = 'arduino'
        elif is_midi(device):
            name = 'piano'
        else:
            return
        self.__callback(USBDevice(device.action, name))


class Connector(ABC):
    def __init__(self, port: str):
        self.is_connected = False
        self.port = port

    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass


class MidiConnector(Connector):
    def __init__(self, port: str):
        super().__init__(port)
        self.__midi_connection: Input = None
        self.__thread: Thread = None

    def connect(self):
        try:
            self.__midi_connection = mido.open_input(self.port)
            self.is_connected = True
            print(f'{self.port} connected')
        except IOError as e:
            print(f'Could not connect to MIDI {self.port}. Error: {e}')

    def disconnect(self):
        self.__midi_connection.close()
        self.is_connected = False
        print(f'{self.port} disconnected')

    def listen_for_midi(self, fn: Callback):
        if not self.is_connected:
            self.connect()
        self.__thread = threading.Thread(target=self.__start_thread, args=(fn,))
        self.__thread.start()

    def __start_thread(self, fn: Callback):
        print('Listening for MIDI input..')
        while self.is_connected:
            msg = self.__midi_connection.receive()
            data = msg.dict()
            type = data['type']
            if type not in ['note_on', 'note_off']:
                continue
            is_on = True if type == 'note_on' else False
            note = data['note']
            velocity = data['velocity']

            fn(Note(is_on, note, velocity))

    def __del__(self):
        self.disconnect()


class ArduinoConnector(Connector):
    def __init__(self, port: str):
        super().__init__(port)
        self.__serial_connection: Serial = None

    def connect(self):
        try:
            if self.is_connected:
                return
            self.__serial_connection = serial.Serial(self.port)
            self.is_connected = True
            print(f'{self.port} connected')
        except SerialException as e:
            print(f'Could not connect to serial port: {self.port}. Error: {e}')

    def disconnect(self):
        if not self.is_connected:
            return
        self.__serial_connection.close()
        self.is_connected = False
        print(f'{self.port} disconnected')

    def send_data(self, data: bytes):
        if not self.is_connected:
            return
        print(f'Sending data: {data.hex()}')
        try:
            self.__serial_connection.write(data)
        except Exception as e:
            print(f'Error sending data: {e}')


class Main(Thread):
    def __init__(self, midi_port: str, serial_port: str):
        super().__init__(daemon=True)
        self.usb_observer = USBObserver(self.usb_listener)
        self.usb_observer.run()
        self.piano = MidiConnector(midi_port)
        self.piano.listen_for_midi(self.note_listener)
        self.arduino = ArduinoConnector(serial_port)
        self.notes_on = [False] * 88

    def note_listener(self, note: Note):
        shifted_note = note.note - 21
        self.notes_on[shifted_note] = note.is_on
        if self.notes_on[0] and self.notes_on[87]:
            self.arduino.connect()
        else:
            packet = Packet(PacketType.data, note)
            self.arduino.send_data(packet.pack())

    def usb_listener(self, device: USBDevice):
        if device.name == 'piano':
            if device.action == 'add':
                self.piano.listen_for_midi(self.note_listener)
                self.arduino.send_data(Packet(PacketType.meta, Meta(True)).pack())
            elif device.action == 'remove':
                packet = Packet(PacketType.meta, Meta(False))
                self.arduino.send_data(packet.pack())
                self.piano.disconnect()

        if device.name == 'arduino':
            if device.action == 'add':
                self.arduino.connect()
            elif device.action == 'remove':
                self.arduino.disconnect()


if __name__ == '__main__':
    main_thread = Main(MIDI_PORT, SERIAL_PORT)
    main_thread.start()
