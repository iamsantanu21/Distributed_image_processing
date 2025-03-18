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
# On Mac (for client):
    Build client app:
        pyinstaller --onefile --windowed client.py
