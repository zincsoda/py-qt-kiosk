import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt

class RotatedTextWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Rotated Text")
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background with black
        painter.fillRect(self.rect(), Qt.black)
        
        # Set font and size
        font = QFont("Arial", 150)
        painter.setFont(font)
        
        # Set text color to white
        painter.setPen(Qt.white)
        
        # Get text metrics for proper centering
        text = "盟"
        text_rect = painter.fontMetrics().boundingRect(text)
        
        # Calculate center position
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Rotate text by 90 degrees around the center
        painter.translate(center_x, center_y)  # Translate to center of the widget
        painter.rotate(90)                     # Rotate 90 degrees clockwise
        
        # Draw the text centered (accounting for text dimensions)
        painter.drawText(-text_rect.width() / 2, text_rect.height() / 2, text)
        
        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RotatedTextWidget()
    window.show()
    sys.exit(app.exec_())
