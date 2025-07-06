#!/usr/bin/env python3
"""
Digital Clock Kiosk Application

A PyQt5-based full-screen clock display with countdown timer, IP address display,
and dynamic message updates from a text file.
"""

import sys
import time
import socket
import fcntl
import struct
import subprocess
import platform
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont


class Config:
    """Configuration constants for the application."""
    
    # Platform detection
    @staticmethod
    def is_raspberry_pi() -> bool:
        """Detect if running on Raspberry Pi using multiple methods."""
        # Method 1: Check /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo or 'BCM2708' in cpuinfo or 'BCM2709' in cpuinfo or 'BCM2835' in cpuinfo:
                    return True
        except FileNotFoundError:
            pass
        
        # Method 2: Check for /proc/device-tree/model
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip()
                if 'Raspberry Pi' in model:
                    return True
        except FileNotFoundError:
            pass
        
        # Method 3: Check for /sys/firmware/devicetree/base/model
        try:
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model = f.read().strip()
                if 'Raspberry Pi' in model:
                    return True
        except FileNotFoundError:
            pass
        
        return False
    
    @staticmethod
    def is_macos() -> bool:
        """Detect if running on macOS."""
        return platform.system() == 'Darwin'
    
    @property
    def IS_RASPBERRY_PI(self) -> bool:
        """Property to check if running on Raspberry Pi."""
        return self.is_raspberry_pi()
    
    @property
    def IS_MACOS(self) -> bool:
        """Property to check if running on macOS."""
        return self.is_macos()
    
    def get_platform_info(self) -> str:
        """Get detailed platform information for debugging."""
        info = []
        info.append(f"System: {platform.system()}")
        info.append(f"Release: {platform.release()}")
        info.append(f"Machine: {platform.machine()}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Is Raspberry Pi: {self.IS_RASPBERRY_PI}")
        info.append(f"Is macOS: {self.IS_MACOS}")
        return " | ".join(info)
    
    # Font sizes - dynamically determined based on platform
    @property
    def CLOCK_FONT_SIZE(self) -> int:
        """Clock font size based on platform."""
        return 100 if self.IS_RASPBERRY_PI else 300
    
    @property
    def FOOTER_FONT_SIZE(self) -> int:
        """Footer font size based on platform."""
        return 10 if self.IS_RASPBERRY_PI else 50
    
    # Colors
    BACKGROUND_COLOR = "black"
    CLOCK_COLOR = "white"
    HEADER_COLOR = "lightblue"
    IP_COLOR = "pink"
    COUNTDOWN_COLOR = "green"
    
    # Timer intervals (milliseconds)
    CLOCK_UPDATE_INTERVAL = 1000
    MESSAGE_CHECK_INTERVAL = 5000  # Check for new messages every 5 seconds
    
    # File paths
    MESSAGE_FILE = "message.txt"
    
    # Countdown target date (year, month, day, hour, minute)
    COUNTDOWN_TARGET = (2023, 9, 15, 9, 0)
    
    # Network interface names
    PI_INTERFACE = 'wlan0'
    MACOS_INTERFACE = 'en0'


class NetworkUtils:
    """Utility class for network operations."""
    
    @staticmethod
    def get_wlan_ipaddress() -> str:
        """Get IP address for wlan0 interface (Raspberry Pi)."""
        try:
            ifname = Config.PI_INTERFACE
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_address = socket.inet_ntoa(fcntl.ioctl(
                sock.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            return ip_address
        except (OSError, IOError) as e:
            return f"Error: {e}"
    
    @staticmethod
    def get_en0_ipaddress() -> str:
        """Get IP address for en0 interface (macOS)."""
        try:
            ip_address = subprocess.check_output(
                ['ipconfig', 'getifaddr', Config.MACOS_INTERFACE]
            ).decode().strip()
            return ip_address
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return f"Error: {e}"
    
    @staticmethod
    def get_ip_address() -> str:
        """Get IP address based on platform."""
        config = Config()
        if config.IS_RASPBERRY_PI:
            return NetworkUtils.get_wlan_ipaddress()
        else:
            return NetworkUtils.get_en0_ipaddress()


class MessageReader:
    """Handles reading messages from file."""
    
    def __init__(self, file_path: str = Config.MESSAGE_FILE):
        self.file_path = Path(file_path)
        self._last_modified = 0
        self._cached_message = ""
    
    def read_message(self) -> str:
        """Read message from file with caching to avoid unnecessary I/O."""
        try:
            if not self.file_path.exists():
                return "Message file not found"
            
            # Check if file has been modified
            current_mtime = self.file_path.stat().st_mtime
            if current_mtime > self._last_modified:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._cached_message = f.readline().strip()
                self._last_modified = current_mtime
            
            return self._cached_message or "No message available"
            
        except (IOError, OSError) as e:
            return f"Error reading message: {e}"


class CountdownTimer:
    """Handles countdown timer logic."""
    
    def __init__(self, target_date: tuple = Config.COUNTDOWN_TARGET):
        self.end_time = QDateTime(*target_date)
    
    def get_time_remaining(self) -> str:
        """Get formatted string of time remaining."""
        current_date_time = QDateTime.currentDateTime()
        time_left = current_date_time.secsTo(self.end_time)
        
        if time_left <= 0:
            return "Countdown over!"
        
        days_left = time_left // (24 * 60 * 60)
        time_left -= days_left * 24 * 60 * 60
        time = QTime(0, 0, 0).addSecs(time_left)
        
        return (f"{days_left} days, {time.toString('hh')} hrs, "
                f"{time.toString('mm')} mins, {time.toString('ss')} secs")


class StyledLabel(QLabel):
    """Custom QLabel with consistent styling."""
    
    def __init__(self, text: str = "", color: str = "white", 
                 font_size: Optional[int] = None, 
                 word_wrap: bool = False):
        super().__init__(text)
        self.setStyleSheet(f'color: {color}')
        self.setAlignment(Qt.AlignCenter)
        
        if word_wrap:
            self.setWordWrap(True)
        
        font = self.font()
        if font_size is None:
            config = Config()
            font_size = config.FOOTER_FONT_SIZE
        font.setPointSize(font_size)
        self.setFont(font)


class MainWindow(QWidget):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.message_reader = MessageReader()
        self.countdown_timer = CountdownTimer()
        self.init_ui()
        self.setup_timers()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.create_widgets()
        self.setup_layout()
        self.setup_window_properties()
    
    def create_widgets(self):
        """Create all UI widgets."""
        config = Config()
        
        # Header label for messages
        self.header_label = StyledLabel(
            "There are no bad pictures - that's just how your face looks sometimes",
            Config.HEADER_COLOR,
            config.FOOTER_FONT_SIZE,
            word_wrap=True
        )
        
        # Clock label
        self.clock_label = StyledLabel(
            "",
            Config.CLOCK_COLOR,
            config.CLOCK_FONT_SIZE
        )
        
        # IP address label
        self.ip_label = StyledLabel(
            NetworkUtils.get_ip_address(),
            Config.IP_COLOR,
            config.FOOTER_FONT_SIZE
        )
        
        # Countdown label
        self.countdown_label = StyledLabel(
            "...",
            Config.COUNTDOWN_COLOR,
            config.FOOTER_FONT_SIZE
        )
    
    def setup_layout(self):
        """Setup the layout structure."""
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.header_label)
        
        # Footer layout
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.countdown_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.ip_label)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.clock_label, 1)  # Give clock label more space
        main_layout.addLayout(footer_layout)
        
        self.setLayout(main_layout)
    
    def setup_window_properties(self):
        """Setup window properties and positioning."""
        # Center the window on screen
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
        
        # Full screen and styling
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {Config.BACKGROUND_COLOR};")
        self.setCursor(Qt.BlankCursor)
    
    def setup_timers(self):
        """Setup timers for clock updates and message checking."""
        # Clock update timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(Config.CLOCK_UPDATE_INTERVAL)
        
        # Message check timer
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.update_message)
        self.message_timer.start(Config.MESSAGE_CHECK_INTERVAL)
    
    def update_clock(self):
        """Update clock display and countdown."""
        # Update clock
        current_time = QTime.currentTime()
        self.clock_label.setText(current_time.toString("hh:mm:ss"))
        
        # Update countdown
        self.countdown_label.setText(self.countdown_timer.get_time_remaining())
    
    def update_message(self):
        """Update message from file."""
        message = self.message_reader.read_message()
        self.header_label.setText(message)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Print platform detection info for debugging
    config = Config()
    print(f"Platform Detection: {config.get_platform_info()}")
    
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

