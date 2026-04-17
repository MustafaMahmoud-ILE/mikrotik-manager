# MikroTik Hotspot Manager

A professional, modern, and frameless desktop application for managing MikroTik hotspot users. Built with Python and PySide6, featuring a skeuomorphic dark-themed UI and robust backend integration.

## ✨ Latest Features

- **System Tray Support**: The app now stays active in the background when minimized, providing seamless quota monitoring.
- **Smart Installation**: Automatically installs itself to `%APPDATA%` and creates shortcuts on the **Desktop** and **Start Menu**.
- **Auto-Login & Quota Tracking**: Real-time quota monitoring with a 30-second auto-reauthentication cycle.
- **Profile Management**: Switch between profiles (Gaming, Balanced, etc.) with automated hotspot session management.
- **Modern UI**: Custom frameless windows, smooth animations, and a polished dark theme with accent lightning.

## 🚀 Installation & Deployment

### For Developers
1. Clone the repository:
   ```bash
   git clone https://github.com/MustafaMahmoud-ILE/mikrotik-manager.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### For Production (EXE)
The project is configured for `PyInstaller`. To build the executable:
```bash
pyinstaller --noconfirm --onedir --windowed --name "mikrotik-manager" --icon="ui/assets/mikrotik-light.png" --add-data "ui/assets;ui/assets" main.py
```

## 📂 Project Structure

- `core/`: Backend logic (SSH, Hotspot, Config, and Quota management).
- `ui/`: PySide6 windows, custom styles, and assets.
- `utils/`: System utilities (Tray management, Shortcut creation, Startup logic).
- `dist/`: Ready-to-use production builds.

## 🛠️ Requirements
- Python 3.10+
- PySide6
- Paramiko (for SSH management)
- Requests (for Hotspot API)

---
*Developed for Banna's Home Network.*
