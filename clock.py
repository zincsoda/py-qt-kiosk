import sys, time
from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
import threading, time

import socket
import fcntl
import struct
import subprocess

RUN_ON_PI = False

if RUN_ON_PI:
    CLOCK_FONT_SIZE = 100
    FOOTER_FONT_SIZE = 10
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
        self.initUI()

    def initUI(self):

        self.createHeaderLabel()
        self.createClockLabel()
        self.createIPAddressLabel()
        self.createCountDownLabel()

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.header_label)

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.countdown_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.ip_label)

        layout = QVBoxLayout()
        layout.addLayout(header_layout)
        layout.addWidget(self.clockLabel, 1)
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

    def createClockLabel(self):
        self.clockLabel = QLabel('', self)
        self.clockLabel.setAlignment(Qt.AlignCenter)
        font = self.clockLabel.font()
        font.setPointSize(CLOCK_FONT_SIZE)
        self.clockLabel.setFont(font)
        self.clockLabel.setStyleSheet('color: white')

        # Create a timer that updates the clock every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)


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

    def createCountDownLabel(self):
        self.countdown_label = QLabel("...",self)
        self.countdown_label.setStyleSheet('color: green')
        font = self.countdown_label.font() # get the current font
        font.setPointSize(FOOTER_FONT_SIZE)
        self.countdown_label.setFont(font)
        self.end_time = QDateTime(2023, 9, 15, 9, 0)  # May 11th 2023, 7pm

    def update_clock(self):
        # Get the current time and display it on the label
        current_clock_time = QTime.currentTime()
        current_time_text = current_clock_time.toString("hh:mm:ss")
        self.clockLabel.setText(current_time_text)

        # Check for discord message
        self.checkForMessage()

        # Update countdown timere
        current_date_time = QDateTime.currentDateTime()
        time_left = current_date_time.secsTo(self.end_time)

        if time_left <= 0:
            self.countdown_label.setText("Countdown over!")
        else:
            days_left = time_left // (24 * 60 * 60)
            time_left -= days_left * 24 * 60 * 60
            time = QTime(0, 0, 0).addSecs(time_left)

            self.countdown_label.setText("{} days,  {} hrs,  {} mins,  {} secs".format(
                days_left, time.toString('hh'), time.toString('mm'), time.toString('ss')))

    def checkForMessage(self):
        f = open("message.txt", "r")
        message = f.readline()
        self.header_label.setText(message)
        f.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

