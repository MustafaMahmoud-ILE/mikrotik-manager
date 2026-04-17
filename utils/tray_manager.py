from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QObject, Signal

class TrayManager(QObject):
    show_requested = Signal()
    exit_requested = Signal()

    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), parent)
        self.tray_icon.setToolTip("MikroTik Manager")
        
        # Context Menu
        self.menu = QMenu()
        
        self.show_action = QAction("Show Manager")
        self.show_action.triggered.connect(self.show_requested.emit)
        
        self.exit_action = QAction("Exit")
        self.exit_action.triggered.connect(self.exit_requested.emit)
        
        self.menu.addAction(self.show_action)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)
        
        self.tray_icon.setContextMenu(self.menu)
        
        # Activation (Double click or single click on some platforms)
        self.tray_icon.activated.connect(self._on_activated)
        
    def show(self):
        self.tray_icon.show()
        
    def hide(self):
        self.tray_icon.hide()

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_requested.emit()

    def show_message(self, title, message, icon=QSystemTrayIcon.Information, timeout=3000):
        self.tray_icon.showMessage(title, message, icon, timeout)
