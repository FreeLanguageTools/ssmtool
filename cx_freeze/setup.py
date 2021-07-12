import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["PyQt5", "wiktionaryparser"],
                     "excludes": ["tkinter"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "ssmtool",
    version = "0.1.7",
    description = "Simple Sentence Mining",
    options = {"build_exe": build_exe_options},
    executables = [Executable("app.py",
                              base=base,
                              icon="icon.ico",
                              shortcut_name="Simple Sentence Mining",
                              shortcut_dir="DesktopFolder")]
)