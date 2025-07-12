#!/usr/bin/env python3
"""
Character Display Kiosk Application

A PyQt5-based kiosk application that displays Chinese characters with
support for Discord message integration and network status display.
"""

import sys
import os
import json
import random
import threading
import time
import socket
import fcntl
import struct
import subprocess
from typing import List, Tuple, Dict

from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout


# Configuration
RUN_ON_PI = False

if RUN_ON_PI:
    CLOCK_FONT_SIZE = 130
    FOOTER_FONT_SIZE = 35
else:
    CLOCK_FONT_SIZE = 300
    FOOTER_FONT_SIZE = 50

# Constants
FLASHCARDS_FILE = "flashcards.json"
MESSAGE_FILE = "message.txt"
CHARACTER_UPDATE_INTERVAL = 10000  # 10 seconds
COUNTDOWN_INTERVAL = 1000  # 1 second for countdown updates
DEFAULT_HEADER_TEXT = "" #There are no bad pictures - thats just how your face looks sometimes"


def get_wlan_ipaddress() -> str:
    """Get the IP address of the wlan0 interface (Raspberry Pi)."""
    ifname = 'wlan0'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf-8'))
    )[20:24])
    return ip_address


def get_en0_ipaddress() -> str:
    """Get the IP address of the en0 interface (macOS)."""
    ip_address = subprocess.check_output(['ipconfig', 'getifaddr', 'en0']).decode().strip()
    return ip_address


def get_ip_address() -> str:
    """Get the current IP address based on platform."""
    try:
        if RUN_ON_PI:
            return get_wlan_ipaddress()
        else:
            return get_en0_ipaddress()
    except Exception:
        return "127.0.0.1"  # fallback to localhost


class CharacterDisplay(QWidget):
    """Main application window for displaying Chinese characters."""
    
    def __init__(self):
        super().__init__()
        self.callback_done = threading.Event()
        self.flashcards: List[Dict[str, str]] = []
        self.current_index: int = 0
        self.countdown_seconds: int = CHARACTER_UPDATE_INTERVAL // 1000
        
        self._load_flashcards()
        self._init_ui()
        self._setup_timers()
        self._update_character()

    def _init_ui(self):
        """Initialize the user interface."""
        self._create_header_label()
        self._create_character_label()
        self._create_countdown_label()
        self._create_ip_address_label()
        self._create_frame_label()
        self._setup_layout()
        self._setup_window_properties()

    def _setup_layout(self):
        """Setup the main layout of the application."""
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.header_label)

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.frame_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.countdown_label)
        footer_layout.addWidget(self.ip_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.character_label, 1)
        main_layout.addLayout(footer_layout)
        
        self.setLayout(main_layout)

    def _setup_window_properties(self):
        """Configure window properties for fullscreen kiosk mode."""
        # Center the widget on the screen
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        self.setCursor(Qt.BlankCursor)

    def _setup_timers(self):
        """Setup timers for character updates and countdown."""
        # Single timer for both character updates and countdown
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_countdown)
        self.timer.start(COUNTDOWN_INTERVAL)
        
        # Initialize countdown
        self.countdown_seconds = CHARACTER_UPDATE_INTERVAL // 1000

    def _load_flashcards(self):
        """Load flashcards from JSON file."""
        dirname = os.path.dirname(__file__) or '.'
        json_path = os.path.join(dirname, FLASHCARDS_FILE)
        
        try:
            with open(json_path, "r", encoding='utf-8') as f:
                self.flashcards = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {FLASHCARDS_FILE} not found")
        except Exception as e:
            print(f"Error loading flashcards: {e}")

    def _create_header_label(self):
        """Create and configure the header label."""
        self.header_label = QLabel(self)
        self.header_label.setText(DEFAULT_HEADER_TEXT)
        self.header_label.setStyleSheet('color: lightblue')
        self.header_label.setWordWrap(True)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.resize(100, 20)

        font = self.header_label.font()
        font.setPointSize(FOOTER_FONT_SIZE)
        self.header_label.setFont(font)

    def _create_character_label(self):
        """Create and configure the main character display label."""
        self.character_label = QLabel('', self)
        self.character_label.setAlignment(Qt.AlignCenter)
        font = self.character_label.font()
        font.setPointSize(CLOCK_FONT_SIZE)
        self.character_label.setFont(font)
        self.character_label.setStyleSheet('color: white')

    def _create_countdown_label(self):
        """Create and configure the countdown label."""
        self.countdown_label = QLabel(self)
        self.countdown_label.setText(f"{self.countdown_seconds}s")
        self.countdown_label.setStyleSheet('color: yellow')
        font = self.countdown_label.font()
        font.setPointSize(FOOTER_FONT_SIZE)
        self.countdown_label.setFont(font)

    def _create_ip_address_label(self):
        """Create and configure the IP address label."""
        self.ip_label = QLabel(self)
        self.ip_label.setText(get_ip_address())
        self.ip_label.setStyleSheet('color: pink')
        font = self.ip_label.font()
        font.setPointSize(FOOTER_FONT_SIZE)
        self.ip_label.setFont(font)

    def _create_frame_label(self):
        """Create and configure the frame label."""
        self.frame_label = QLabel("...", self)
        self.frame_label.setStyleSheet('color: green')
        font = self.frame_label.font()
        font.setPointSize(FOOTER_FONT_SIZE)
        self.frame_label.setFont(font)
        self.end_time = QDateTime(2024, 9, 15, 9, 0)

    def _update_countdown(self):
        """Update the countdown display."""
        self.countdown_seconds -= 1
        self.countdown_label.setText(f"{self.countdown_seconds}s")
        
        # When countdown reaches 0, update character and reset countdown
        if self.countdown_seconds <= 0:
            self._update_character()
            self.countdown_seconds = CHARACTER_UPDATE_INTERVAL // 1000

    def _update_character(self):
        """Update the displayed character and check for new messages."""
        self._check_for_message()
        self._display_random_character()

    def _check_for_message(self):
        """Check for and display new messages from Discord."""
        dirname = os.path.dirname(__file__) or '.'
        message_path = os.path.join(dirname, MESSAGE_FILE)
        
        try:
            with open(message_path, "r", encoding='utf-8') as f:
                message = f.readline().strip()
                if message:
                    self.header_label.setText(message)
        except FileNotFoundError:
            # Keep default message if file doesn't exist
            pass
        except Exception as e:
            print(f"Error reading message file: {e}")

    def _display_random_character(self):
        """Display a random character from the loaded flashcards."""
        if not self.flashcards:
            return
            
        self.current_index = random.randrange(len(self.flashcards))
        current_flashcard = self.flashcards[self.current_index]
        
        # Display the hanzi character
        self.character_label.setText(current_flashcard.get("Hanzi", ""))
        # Display the pinyin in the frame label
        self.frame_label.setText(current_flashcard.get("Pinyin", ""))


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = CharacterDisplay()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

