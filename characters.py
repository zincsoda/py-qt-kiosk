import sys, time
from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
import threading, time

import socket
import fcntl
import struct
import subprocess
import csv
import random
import os

RUN_ON_PI = True

if RUN_ON_PI:
    CLOCK_FONT_SIZE = 130
    FOOTER_FONT_SIZE = 35
else:
    CLOCK_FONT_SIZE = 300
    FOOTER_FONT_SIZE = 50

def get_wlan_ipaddress():
    # Get the network interface associated with WiFi
    ifname = 'wlan0'  # This assumes your WiFi interface is named 'wlan0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf-8'))
    )[20:24])
    return ip_address

# macOS
def get_en0_ipaddress():
    ip_address = subprocess.check_output(['ipconfig', 'getifaddr', 'en0']).decode().strip()
    return ip_address

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.callback_done = threading.Event()
        self.characters = []
        self.read_csv_chars()
        self.initUI()
        self.update_character()


    def initUI(self):

        self.createHeaderLabel()
        self.createcharacter_label()
        self.createIPAddressLabel()
        self.createFrameLabel()

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.header_label)

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.frame_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.ip_label)

        layout = QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.character_label, 1)
        layout.addLayout(footer_layout)  
        self.setLayout(layout)

        # center the widget on the screen
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        self.setCursor(Qt.BlankCursor)

    def read_csv_chars(self):
        dirname = os.path.dirname(__file__) or '.'
        f = open(dirname + "/" +  "input.csv", "r")
        csv_reader = csv.reader(f)
        for row in csv_reader:
            tup = (row[0], row[1])
            self.characters.append(tup)
        f.close()

    def createcharacter_label(self):
        self.character_label = QLabel('', self)
        self.character_label.setAlignment(Qt.AlignCenter)
        font = self.character_label.font()
        font.setPointSize(CLOCK_FONT_SIZE)
        self.character_label.setFont(font)
        self.character_label.setStyleSheet('color: white')

        # Create a timer that updates the clock every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_character)
        self.timer.start(10000)


    def createHeaderLabel(self):
        self.header_label = QLabel(self)
        self.header_label.setText("There are no bad pictures - thats just how your face looks sometimes")
        self.header_label.setStyleSheet('color: lightblue')
        self.header_label.setWordWrap(True)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.resize(100, 20)

        font = self.header_label.font() # get the current font
        font.setPointSize(FOOTER_FONT_SIZE)
        self.header_label.setFont(font)

    def createIPAddressLabel(self):
        self.ip_label = QLabel(self)
        if RUN_ON_PI:
            ip_address = get_wlan_ipaddress()
        else:
            ip_address = get_en0_ipaddress()
        self.ip_label.setText(ip_address)
        self.ip_label.setStyleSheet('color: pink')
        font = self.ip_label.font() # get the current font
        font.setPointSize(FOOTER_FONT_SIZE)
        self.ip_label.setFont(font)

    def createFrameLabel(self):
        self.frame_label = QLabel("...",self)
        self.frame_label.setStyleSheet('color: green')
        font = self.frame_label.font() # get the current font
        font.setPointSize(FOOTER_FONT_SIZE)
        self.frame_label.setFont(font)
        self.end_time = QDateTime(2024, 9, 15, 9, 0)  # May 11th 2023, 7pm

    def update_character(self):

        # Check for discord message
        self.checkForMessage()

        # Choose next character
        self.index = random.randrange(len(self.characters))
        current_character = self.characters[self.index][1]
        current_frame = self.characters[self.index][0]
        self.character_label.setText(current_character)
        self.frame_label.setText(current_frame)

    def checkForMessage(self):
        f = open(os.path.dirname(__file__) + "/" +  "message.txt", "r")
        message = f.readline()
        self.header_label.setText(message)
        f.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

