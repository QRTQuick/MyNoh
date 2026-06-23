"""Best-effort startup registration helper. Run after installation."""
from __future__ import annotations
import os, platform, sys
from pathlib import Path

APP = "Mynoh"

def main() -> None:
    exe = Path(sys.executable).resolve()
    system = platform.system()
    if system == "Windows":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP, 0, winreg.REG_SZ, str(exe)); winreg.CloseKey(key)
    elif system == "Darwin":
        plist = Path.home()/"Library/LaunchAgents/com.mynoh.app.plist"
        plist.write_text(f"""<?xml version='1.0' encoding='UTF-8'?><!DOCTYPE plist PUBLIC '-//Apple//DTD PLIST 1.0//EN' 'http://www.apple.com/DTDs/PropertyList-1.0.dtd'><plist version='1.0'><dict><key>Label</key><string>com.mynoh.app</string><key>ProgramArguments</key><array><string>{exe}</string></array><key>RunAtLoad</key><true/></dict></plist>""")
    else:
        autostart = Path.home()/".config/autostart"; autostart.mkdir(parents=True, exist_ok=True)
        (autostart/"mynoh.desktop").write_text(f"[Desktop Entry]\nType=Application\nName=Mynoh\nExec={exe}\nX-GNOME-Autostart-enabled=true\n")
    print(f"Registered {APP} startup for {system}")

if __name__ == "__main__": main()
