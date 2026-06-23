import subprocess, sys

cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--windowed", "--name", "Mynoh", "--add-data", "assets:assets", "main.py"]
raise SystemExit(subprocess.call(cmd))
