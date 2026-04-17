# MikroTik Manager

A professional desktop application using Python and PySide6 that allows MikroTik hotspot users to manage their profiles and enable auto-login functionality.

## Project Layout

```text
mikrotik_manager/
├── main.py                 # Application entry point
├── ui/
│   ├── login_window.py     # Login UI
│   ├── dashboard_window.py # Main dashboard UI
│   ├── password_dialog.py  # Password change dialog
│   └── styles.py           # QSS stylesheets
├── core/
│   ├── ssh_manager.py      # SSH communication with router
│   ├── hotspot_manager.py  # Hotspot login/logout automation
│   ├── quota_manager.py    # Quota calculation
│   └── config_manager.py   # App configuration
└── utils/
    ├── single_instance.py  # Single instance check
    ├── startup_manager.py  # Windows startup integration
    └── validators.py       # Input validation
```

## Adding Custom Icons

The app is configured to use `ui/assets/mikrotik-light.png` as its window and taskbar icon. To bundle this icon into the `.exe` file:

```bash
# Using the PNG as the executable icon (PyInstaller will attempt conversion)
pyinstaller --noconfirm --onedir --windowed --icon="ui/assets/mikrotik-light.png" main.py
```

## Development Requirements
- Python 3.9+
- `pip install -r requirements.txt`
