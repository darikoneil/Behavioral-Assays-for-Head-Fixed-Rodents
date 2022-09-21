from os import chdir, path
from PyQt6 import uic

currentPath = path.dirname(path.realpath(__file__))
chdir(currentPath)
uic.compileUiDir(currentPath)

if __name__ == "__main__":
    print("Compiling...")
    currentPath = path.dirname(path.realpath(__file__))
    chdir(currentPath)
    uic.compileUiDir(currentPath)
    print("Compiled.")
