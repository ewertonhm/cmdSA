import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
    "packages": ["os"],
    "excludes": ["tkinter"],
    "includes": ["Bemtevi", "conf", "Netbox", "SA"]
}

# base="Win32GUI" should be used only for Windows GUI app
base = None
'''if sys.platform == "win32":
    base = "Win32GUI"
    '''

setup(
    name = "Status",
    version = "3.0",
    description = "Verifica status dos circuitos!",
    options = {"build_exe": build_exe_options},
    executables = [Executable("main.py", base=base)]
)