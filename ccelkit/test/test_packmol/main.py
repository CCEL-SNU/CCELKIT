import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from packmol import *
import argparse
import numpy as np
import inspect
from typing import get_type_hints

def test_init_dir():
    init_dir()

def test_init_config():
    init_config(preset=True)

def test_make_system(config_path:str):
    make_system(config_path)

def main():
    test_init_dir()
    # test_init_config()
    config_path = os.path.join(os.getcwd(), 'config_init.yml')
    test_make_system(config_path)
if __name__ == "__main__":
    main()

