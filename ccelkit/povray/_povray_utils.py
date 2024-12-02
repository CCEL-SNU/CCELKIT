from ase.io import read, write
from ase import Atoms
from typing import List, Union, Dict
import os
import numpy as np
from ase.data.colors import jmol_colors

from scipy.spatial.transform import Rotation as R


import click
import os
import yaml

@click.command()
@click.option('--output', '-o', default='config.yml', help='설정 파일 저장 경로')
def create_config(output):
    default_config = {
        "target": None,
        "input_filepath": "./src/perovskite_POSCAR",
        "output_filepath": "./outputs/config_perovskite_POSCAR.png",
        "repeatation": [1, 1, 1],
        "orientation": "0.945420 -0.016442 -0.325439 0.293091 0.479364, 0.827229 0.142402 -0.877462 0.458019",
        "cell_on": True,
        "transmittances": None,
        "heatmaps": None,
        "canvas_width": 800,
        "color_species": {
            "Re": [0.580, 0, 0.827],
            "H": [0.529, 0.808, 0.980],
            "O": [0.0, 0.0, 1.0],
            "Ru": [0.827, 0.827, 0.827]
        },
        "color_index": {
            0: [0.580, 0, 0.827],
            1: [0.529, 0.808, 0.980],
            2: [1.000, 0.051, 0.051],
            3: [0.0, 0.0, 1.0]
        }
    }
    
    # YAML 파일로 저장
    with open(output, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)
    
    click.echo(f"설정 파일이 생성되었습니다: {output}")

def parse_orientation(orientation: str) -> List[float]:
    orientation_preset = {
        "top": "+1.000000 +0.000000 +0.000000 +0.000000 +1.000000 +0.000000 +0.000000 +0.000000 +1.000000",
        "side_x": "+0.000000  +1.000000  +0.000000 +0.000000  +0.000000  +1.000000 +1.000000  +0.000000  +0.000000",
        "side_y": " +0.000000  -0.000000  +1.000000 +1.000000  -0.000000  -0.000000 +0.000000  +1.000000  +0.000000",
        "perspective": " -0.316228  +0.948683  -0.000000 -0.155963  -0.051988  +0.986394 +0.935775  +0.311925  +0.164399"
    }
    if orientation in orientation_preset.keys():
        orientation = orientation_preset[orientation]
    orientation = orientation.split()
    orientation = [float(o) for o in orientation]
    return orientation

def set_repeatation(atoms: Atoms, repeatation: list) -> Atoms:
    atoms = atoms.repeat(repeatation)
    return atoms

def set_cell_on(atoms: Atoms, cell_on: bool) -> Atoms:
    atoms_copied = atoms.copy()
    if not cell_on:
        atoms_copied.cell = None
    return atoms_copied

def set_canvas_width(povray_settings: dict, canvas_width: int) -> None:
    new_instance = {'canvas_width': canvas_width}
    povray_settings.update(new_instance)
    return None

def set_transmittances(povray_settings: dict, transmittances: Union[List[float],None]) -> None:
    if transmittances:
        povray_settings.update({'transmittances': transmittances})
    return None

def set_heatmaps(povray_settings: dict, heatmaps: Union[List[float],None]) -> None:
    if heatmaps:
        mapped_colors = [(c, 0.0, 1.0 - c) for c in heatmaps]
        povray_settings.update({'colors': mapped_colors})
    return None

def set_camera_orientation(povray_settings: dict, orientation: List[float]) -> str:
    rotation = [orientation[:3], orientation[3:6], orientation[6:]]
    rotation = R.from_matrix(rotation).as_euler("xyz", degrees=True)
    rotation = f"{rotation[0]}x, {rotation[1]}y, {rotation[2]}z"
    return rotation

def set_custom_colors(atoms: Atoms, povray_settings: dict
                      , color_species_dict: Union[Dict[str,List[float]],None]
                      , color_index_dict: Union[Dict[int,List[float]],None]) -> None:
    colors = povray_settings.get('colors', [0.0 for _ in range(len(atoms))])
    if not color_species_dict:
        color_species_dict = {}
    if not color_index_dict:
        color_index_dict = {}

    for i, atom in enumerate(atoms):
        default_color = color_species_dict.get(atom.symbol,jmol_colors[atom.number])
        colors[i] = color_index_dict.get(i,default_color)
    povray_settings.update({'colors': colors})
    return None