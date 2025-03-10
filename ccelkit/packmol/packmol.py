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
    fluid_dir = os.path.join(src_dir, 'fluid')
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(solid_dir, exist_ok=True)
    os.makedirs(fluid_dir, exist_ok=True)

    cell_path = os.path.join(src_dir, 'cell_POSCAR')
    if not os.path.exists(cell_path):
        cell_atoms = Atoms(cell=Cell([[50,0,0],[0,50,0],[0,0,50]]), pbc=True, symbols=['H'], positions=[[0,0,0]])
        write(cell_path, cell_atoms)

    return root_dir, src_dir, solid_dir, fluid_dir, cell_path

def init_config(root_dir:str = os.getcwd(), preset:str = False)->None:
    root_dir = os.path.abspath(root_dir)
    src_dir = os.path.join(root_dir, 'src')
    out_dir = os.path.join(root_dir, 'out')
    
    if preset:
        set_preset(src_dir)

    cell_path = os.path.join(src_dir, 'cell_POSCAR')
    solid_dir = os.path.join(src_dir, 'solid')
    solid_filenames = [get_filename(os.path.join(solid_dir, file)) for file in os.listdir(solid_dir) if not file.startswith('pinp_')]
    solid_dict = {filename: None for filename in solid_filenames}
    fluid_dir = os.path.join(src_dir, 'fluid')
    fluid_filenames = [get_filename(os.path.join(fluid_dir, file)) for file in os.listdir(fluid_dir) if not file.startswith('pinp_')]
    fluid_dict = {filename: {"density": None} for filename in fluid_filenames}

    config = {
        "root_dir": root_dir,
        "src_dir": src_dir,
        "out_dir": out_dir,
        "cell_path": cell_path,
        "solid_dir": solid_dir,
        "solid" : solid_dict,
        "fluid_dir": fluid_dir,
        "fluid": fluid_dict,
        "tolerance": 2.0,
        "seed": 42,
        "population": 5,
        "solid_fluid_tolerance": 3.0
    }
    with open(os.path.join(root_dir, 'config_init.yml'), 'w') as f:
        yaml.dump(config, f, indent=4)
    return None


def make_system(config_path:str)->None:
    packmol_path = os.environ.get('PACKMOL')
    if packmol_path is None:
        raise EnvironmentError("PACKMOL 환경 변수가 설정되어 있지 않습니다.")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    src_dir = config.get("src_dir", os.path.join(os.getcwd(), 'src'))
    out_dir = config.get("out_dir", os.path.join(os.getcwd(), 'out'))

    os.makedirs(out_dir, exist_ok=True)

    tolerance = config.get("tolerance", 2.0)
    seed = config.get("seed", 42)

    pobjs = read_src(src_dir)
    pcell = pobjs["cell"]
    pfluids = pobjs["fluid"]
    psolids = pobjs["solid"] # not used

    cell = pcell.info['system']['cell']
    cell_array = cell.array
    cell_volume = cell_array[0][0] * cell_array[1][1] * cell_array[2][2]

    x_min, y_min, z_min = 0, 0, 0
    x_max, y_max, z_max = x_min + cell_array[0][0], y_min + cell_array[1][1], z_min + cell_array[2][2]

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
        for pobj in pfluids:
            pobj.set_system_info({"tolerance": tolerance})
            pobj.set_system_info(box_info)
            density = config[pobj.type][pobj.name]['density']
            num_atoms = density_to_number(density, pobj.info['system']['molar_mass'], pobj.info['system']['molar_length'], cell_volume)
            mol_indices = []
            for i in range(num_atoms):
                mol_indices.append(list(range(c, c+pobj.info['system']['molar_length'])))
                c += pobj.info['system']['molar_length']
            pobj.set_system_info({"num_molecules": num_atoms, "mol_indices": mol_indices})

        # make fluid packmol input
        fluid_packmol_inp = os.path.join(out_dir, f'fluid_packmol_{system_idx:02d}.inp')
        fluid_packmol_xyz = os.path.join(out_dir, f'fluid_packmol_{system_idx:02d}.xyz')
        with open(fluid_packmol_inp, 'w') as f:
            f.write(write_packmol_header(tolerance, seed + system_idx))
            f.write(f"output {fluid_packmol_xyz}\n\n")
            f.write(write_fluid_packmol_inp(pfluids))

        print(f"Packmol 실행 중: {fluid_packmol_inp}")
        result = subprocess.run(f"{packmol_path} < {fluid_packmol_inp}", shell=True, timeout=30)

        fluid_xyz = read(fluid_packmol_xyz, format='xyz')
        fluid_xyz.cell = cell
        fluid_xyz.pbc = True
        fluid_non_duplicate = None
        new_mol_indices = []
        c = 0
        for pobj in pfluids:
            a = 0
            num_mol = len(pobj.info['system']['mol_indices'])
            new_mol_indices = []
            for i in range(num_mol):
                mol_indices = pobj.info['system']['mol_indices'][i]
                mol_atoms = fluid_xyz[mol_indices]
                if fluid_non_duplicate is None:
                    fluid_non_duplicate = mol_atoms
                    fluid_non_duplicate.cell = cell
                    fluid_non_duplicate.pbc = True
                else:
                    is_valid = True
                    temp_atoms = fluid_non_duplicate.copy() + mol_atoms.copy()
                    for t in range(len(mol_atoms)):
                        d_array = temp_atoms.get_distances(a=len(fluid_non_duplicate)+t,indices=list(range(len(fluid_non_duplicate))), mic=True)
                        if (d_array.min() < config['tolerance']):
                            is_valid = False
                            break
                    if is_valid:
                        fluid_non_duplicate = temp_atoms
                        new_mol_indices.append(list(range(c, c+len(mol_atoms))))
                        c += len(mol_atoms)
                        a += 1
            pobj.set_system_info({"num_atoms": a, "mol_indices": new_mol_indices})
        
        fluid_non_duplicate_POSCAR_path = os.path.join(out_dir, f'fluid_non_duplicate_{system_idx:02d}_POSCAR')
        fluid_non_duplicate.write(fluid_non_duplicate_POSCAR_path)

        solid_POSCAR = Atoms(cell=cell, pbc=True)
        for psolid in psolids:
            solid_atoms = psolid.atoms
            solid_POSCAR += solid_atoms

        solid_POSCAR.write(os.path.join(out_dir, 'solid.xyz'), format='xyz')

        fluid_non_duplicate = read(fluid_non_duplicate_POSCAR_path)
        solid_xyz = read(os.path.join(out_dir, 'solid.xyz'), format='xyz')
        solid_length = len(solid_xyz)


        system_atoms = solid_xyz.copy()
        system_atoms.cell = cell
        system_atoms.pbc = True
        system_atoms.wrap()
        system_temp = system_atoms.copy()

        c = len(system_atoms)
        for pobj in pfluids:
            num_mol = len(pobj.info['system']['mol_indices'])
            a = 0
            new_mol_indices = []
            for i in range(num_mol):
                mol_indices = pobj.info['system']['mol_indices'][i]
                mol_atoms = fluid_non_duplicate[mol_indices]
                system_atoms_copied = system_temp.copy()    
                system_atoms_copied += mol_atoms

                is_valid = True
                for t in range(len(mol_atoms)):
                    d_array = system_atoms_copied.get_distances(a=solid_length+t,indices=list(range(solid_length)), mic=True)
                    if (d_array.min() < config['solid_fluid_tolerance']):
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