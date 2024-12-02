from ase.io import read, write
from ase import Atoms
from typing import List, Union, Dict
import os
import numpy as np
from ase.data.colors import jmol_colors

from scipy.spatial.transform import Rotation as R

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