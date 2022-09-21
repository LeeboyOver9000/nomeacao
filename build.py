import PyInstaller.__main__

PyInstaller.__main__.run([
    'app/gui.py',
    '--paths=app',
    '--onefile',
    '--windowed',
    '--name=buscanome'
])
