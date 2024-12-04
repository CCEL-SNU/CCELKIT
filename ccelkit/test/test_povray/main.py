import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from povray import visual
import argparse
import numpy as np
import inspect
from typing import get_type_hints

def get_default_args(func) -> dict:
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

def test_default_settings():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/default_settings_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_repeatation():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/repeatation_perovskite_POSCAR.png",
                        "repeatation": [5,5,3],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_orientation():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/default_settings_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": ' -0.839916  -0.275574  -0.467548 -0.525955  +0.200854  +0.826456 -0.133841  +0.940062  -0.313639',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_cell_off():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/cell_off_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": True,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_transmittances():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/transmittances_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": [0.1, 0.2, 0.2, 0.9, 0.9],
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_heatmaps():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/heatmaps_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": [0.1, 0.2, 0.2, 0.9, 0.9],
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_canvas_width():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/canvas_width_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 1920,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_custom_colors():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/perovskite_POSCAR",
                        "output_filepath": "./outputs/custom_colors_perovskite_POSCAR.png",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": {
                                            "Re": [0.580, 0, 0.827],
                                            'H' : [0.0, 0.0, 1.0],
                                            "O": [0.0, 1.0, 0.0],
                                            "Ru": [0.827, 0.827, 0.827],
                                         },
                        "color_index": {
                                            4 : [0.0, 0.0, 1.0],
                                         },
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_target():
    default_settings = {
                        "config": None,
                        "target": "POSCAR",
                        "input_filepath": None,
                        "output_filepath": None,
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 960,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def test_gif():
    default_settings = {
                        "config": None,
                        "target": None,
                        "input_filepath": "./src/test.traj",
                        "output_filepath": "./outputs/test.gif",
                        "repeatation": [1,1,1],
                        "orientation": 'perspective',
                        "cell_off": False,
                        "transmittances": None,
                        "heatmaps": None,
                        "canvas_width": 800,
                        "color_species": None,
                        "color_index": None,
                        "frame_per_second": 24
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)


def test_config():
    default_settings = {
                        "config": "./src/config.yml",
                        }
    args = argparse.Namespace(**default_settings)
    visual(args)

def main():
    # test_default_settings()
    # test_repeatation()
    # test_cell_off()
    # test_transmittances()
    # test_heatmaps()
    # test_canvas_width()
    # test_custom_colors()
    # test_config()
    # test_orientation()
    # test_target()
    test_gif()
if __name__ == "__main__":
    main()