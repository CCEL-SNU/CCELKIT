from ase.io import read, write
from ase import Atoms
from typing import List, Union, Dict
import os
import numpy as np
from ase.data.colors import jmol_colors

from scipy.spatial.transform import Rotation as R
import os
import yaml

def create_config():
    default_config = {
        "target": "POSCAR", # String what target files include
        "input_filepath": None, # if target is specified, input_filepath must be None value
        "output_filepath": None, # if target is specified, output_filepath must be None value
        "repeatation": [1, 1, 1], # 3x1 array
        "orientation": "perspective", # "top", "side_x", "side_y", "perspective" or vesta orientation 3x3 array
        "cell_on": True, # true or false
        "transmittances": None, # array of float, 1 : 100% transmittance, 0 : 0% transmittance
        "heatmaps": None, # array of float, 1 : 100% red, 0 : 100% blue
        "canvas_width": 800, # pixel number of canvas width
        "color_species": {
            # "Re": [0.580, 0, 0.827],
            # "H": [0.529, 0.808, 0.980],
            # "O": [0.0, 0.0, 1.0],
            # "Ru": [0.827, 0.827, 0.827]
        },
        "color_index": {
            # 0: [0.580, 0, 0.827],
            # 1: [0.529, 0.808, 0.980],
            # 2: [1.000, 0.051, 0.051],
            # 3: [0.0, 0.0, 1.0]
        }
    }
    
    # YAML 파일로 저장
    with open("./config.yml", 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, allow_unicode=True, default_flow_style=False)

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

def set_position_smoothing(atoms: Atoms) -> Atoms:
    atoms_copied = atoms.copy()
    cell = atoms_copied .get_cell()
    a, b, c = cell[0], cell[1], cell[2]

    positions = atoms_copied.get_positions()

    limit_a = 0.99 * np.linalg.norm(a)
    limit_b = 0.99 * np.linalg.norm(b)
    limit_c = 0.99 * np.linalg.norm(c)

    for i, pos in enumerate(positions):
        if pos[0] > limit_a:
            positions[i] -= a
        if pos[1] > limit_b:
            positions[i] -= b
        if pos[2] > limit_c:
            positions[i] -= c

    atoms_copied.set_positions(positions)
    return atoms_copied