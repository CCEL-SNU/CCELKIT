import os, yaml
from argparse import ArgumentParser
import numpy as np
from tqdm import tqdm
from ase.cell import Cell
from ase.io import read, write
from ._packmol_utils import *
from ._packmol_class import *

def init_dir(root_dir=os.getcwd())->None:
    root_dir = os.path.abspath(root_dir)
    os.makedirs(root_dir, exist_ok=True)
    src_dir = os.path.join(root_dir, 'src')
    solid_dir = os.path.join(src_dir, 'solid')
    liquid_dir = os.path.join(src_dir, 'liquid')
    gas_dir = os.path.join(src_dir, 'gas')
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(solid_dir, exist_ok=True)
    os.makedirs(liquid_dir, exist_ok=True)
    os.makedirs(gas_dir, exist_ok=True)

    cell_path = os.path.join(src_dir, 'cell_POSCAR')
    if not os.path.exists(cell_path):
        cell_atoms = Atoms(cell=Cell([[50,0,0],[0,50,0],[0,0,50]]), pbc=True, symbols=['H'], positions=[[0,0,0]])
        write(cell_path, cell_atoms)

    return root_dir, src_dir, solid_dir, liquid_dir, gas_dir, cell_path

def init_config(root_dir:str = os.getcwd())->None:
    root_dir = os.path.abspath(root_dir)
    src_dir = os.path.join(root_dir, 'src')
    out_dir = os.path.join(root_dir, 'out')

    cell_path = os.path.join(src_dir, 'cell_POSCAR')
    solid_dir = os.path.join(src_dir, 'solid')
    solid_filenames = [get_filename(os.path.join(solid_dir, file)) for file in os.listdir(solid_dir) if not file.startswith('pinp_')]
    solid_dict = {filename: None for filename in solid_filenames}
    liquid_dir = os.path.join(src_dir, 'liquid')
    liquid_filenames = [get_filename(os.path.join(liquid_dir, file)) for file in os.listdir(liquid_dir) if not file.startswith('pinp_')]
    liquid_dict = {filename: {"density": None} for filename in liquid_filenames}
    gas_dir = os.path.join(src_dir, 'gas')
    gas_filenames = [get_filename(os.path.join(gas_dir, file)) for file in os.listdir(gas_dir) if not file.startswith('pinp_')]
    gas_dict = {filename: {"density": None} for filename in gas_filenames}

    config = {
        "root_dir": root_dir,
        "src_dir": src_dir,
        "out_dir": out_dir,
        "cell_path": cell_path,
        "solid_dir": solid_dir,
        "solid" : solid_dict,
        "liquid_dir": liquid_dir,
        "liquid": liquid_dict,
        "gas_dir": gas_dir,
        "gas": gas_dict,
        "tolerance": 2.0,
        "seed": 42,
        "population": 5
    }
    with open(os.path.join(root_dir, 'config_init.yml'), 'w') as f:
        yaml.dump(config, f, indent=4)
    return None


def make_system(config_path:str)->None:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    src_dir = config.get("src_dir", os.path.join(os.getcwd(), 'src'))
    out_dir = config.get("out_dir", os.path.join(os.getcwd(), 'out'))

    os.makedirs(out_dir, exist_ok=True)

    tolerance = config.get("tolerance", 2.0)
    seed = config.get("seed", 42)

    pobjs = read_src(src_dir)
    pcell = pobjs["cell"]
    pliquids = pobjs["liquid"]
    pgases = pobjs["gas"]
    psolids = pobjs["solid"] # not used

    cell = pcell.info['system']['cell']
    cell_array = cell.array
    cell_volume = cell_array[0][0] * cell_array[1][1] * cell_array[2][2]

    x_min, y_min, z_min = 0, 0, 0
    x_max, y_max, z_max = x_min + cell_array[0][0] - tolerance, y_min + cell_array[1][1] - tolerance, z_min + cell_array[2][2] - tolerance # for pbc condition

    box_info = {
        "x_min": x_min,
        "y_min": y_min,
        "z_min": z_min,
        "x_max": x_max,
        "y_max": y_max,
        "z_max": z_max
    }
    
    for system_idx in tqdm(range(config['population']), desc='시스템 생성 중'):
        c = 0
        for pobj in pliquids + pgases:
            pobj.set_system_info(box_info)
            density = config[pobj.type][pobj.name]['density']
            num_atoms = density_to_number(density, pobj.info['system']['molar_mass'], pobj.info['system']['molar_length'], cell_volume)
            mol_indices = []
            for i in range(num_atoms):
                mol_indices.append(list(range(c, c+pobj.info['system']['molar_length'])))
                c += pobj.info['system']['molar_length']
            pobj.set_system_info({"num_molecules": num_atoms, "mol_indices": mol_indices})

        # make liquid and gas packmol input
        liquid_gas_packmol_inp = os.path.join(out_dir, 'liquid_gas_packmol.inp')
        liquid_gas_packmol_xyz = os.path.join(out_dir, 'liquid_gas_packmol.xyz')
        with open(liquid_gas_packmol_inp, 'w') as f:
            f.write(write_packmol_header(tolerance, seed + system_idx))
            f.write(f"output {liquid_gas_packmol_xyz}\n\n")
            f.write(write_liquid_gas_packmol_inp(pliquids, pgases))

        try:
            result = subprocess.run(f"packmol < {liquid_gas_packmol_inp}", shell=True, timeout=30)
        except subprocess.TimeoutExpired:
            raise RuntimeError("Packmol execution timed out (timeout = 30 sec). Please check the input file and the system resources.")

        solid_POSCAR = Atoms(cell=cell, pbc=True)
        for psolid in psolids:
            solid_atoms = psolid.atoms
            solid_POSCAR += solid_atoms

        solid_POSCAR.write(os.path.join(out_dir, 'solid.xyz'), format='xyz')

        liquid_gas_xyz = read(liquid_gas_packmol_xyz, format='xyz')
        solid_xyz = read(os.path.join(out_dir, 'solid.xyz'), format='xyz')
        solid_length = len(solid_xyz)


        system_atoms = solid_xyz.copy()
        system_atoms.cell = cell
        system_atoms.pbc = True

        c = len(system_atoms)
        for pobj in pliquids + pgases:
            num_mol = len(pobj.info['system']['mol_indices'])
            a = 0
            new_mol_indices = []
            for i in range(num_mol):
                mol_indices = pobj.info['system']['mol_indices'][i]
                mol_atoms = liquid_gas_xyz[mol_indices]

                system_atoms += mol_atoms

                is_valid = True
                for t in range(len(mol_atoms)):
                    d_array = system_atoms.get_distances(a=solid_length+t,indices=list(range(solid_length)), mic=True)
                    if d_array.min() < 2.0:
                        is_valid = False
                        break

                if is_valid:
                    new_mol_indices.append(list(range(c, c+len(mol_atoms))))
                    system_atoms += mol_atoms
                    c += len(mol_atoms)
                    a += 1

            pobj.set_system_info({"num_atoms": a, "mol_indices": new_mol_indices})

        system_POSCAR_path = os.path.join(out_dir, f'system_{system_idx:02d}_POSCAR')
        write(system_POSCAR_path, system_atoms)