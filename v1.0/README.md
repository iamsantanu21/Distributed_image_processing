# to set up open-cv in Mac
python3 -m venv env
source env/bin/activate
pip3 install opencv-python

# Packaging the executables
# On Windows (for server):
    Install PyInstaller:
        pip install pyinstaller
    Build server EXE:
        pyinstaller --onefile --noconsole server.py
    The executable will be in dist/server.exe
## On Mac (for client):
# Build client app:
    pyinstaller --onefile --windowed client.py
# The .app bundle will appear in dist/client.app
