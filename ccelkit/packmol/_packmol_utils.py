import numpy as np
import ase, os
from ase.io import read, write
from ase import Atoms
from ._packmol_class import *
from typing import List, Dict, Any
import subprocess
from ase.cell import Cell

def check_root_dir(root_dir=os.getcwd())->None:
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"The directory {root_dir} does not exist.")
    src_dir = os.path.join(root_dir, 'src')
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"The directory {src_dir} does not exist.")
    configs_dir = os.path.join(src_dir, 'configs')
    if not os.path.exists(configs_dir):
        raise FileNotFoundError(f"The directory {configs_dir} does not exist.")
    return None

def get_filename(filepath:str)->str:
    filename = os.path.basename(filepath)
    if filename.endswith('_POSCAR'):
        return filename.replace('_POSCAR','')
    else:
        return os.path.splitext(filename)[0]

def get_file_format(filepath:str)->str:
    possible_extensions = {'.xyz' : 'xyz', '.poscar' : 'poscar', '.cif' : 'cif', '.pdb' : 'pdb','_POSCAR' : 'vasp'}
    for ext, format in possible_extensions.items():
        if filepath.endswith(ext):
            return format
    raise ValueError(f"The file {filepath} is not a valid file.")


def read_psolid(pobj_path:str)->PSolid:
    ptype = 'solid'
    format = get_file_format(pobj_path)
    atoms = read(pobj_path,format=format)
    name = get_filename(pobj_path)

    xyz_atoms_path = os.path.join("/".join(pobj_path.split('/')[:-1]), f'pinp_{name}.xyz')
    write(xyz_atoms_path, atoms, format='xyz')

    pobj = PSolid(xyz_atoms_path, atoms, name, ptype)
    pobj.set_system_info()
    pobj.set_surrounding_info()
        
    return pobj

def read_pliquid(pobj_path:str)->PLiquid:
    ptype = 'liquid'
    format = get_file_format(pobj_path)
    atoms = read(pobj_path,format=format)
    name = get_filename(pobj_path)

    xyz_atoms_path = os.path.join("/".join(pobj_path.split('/')[:-1]), f'pinp_{name}.xyz')
    write(xyz_atoms_path, atoms, format='xyz')

    pobj = PLiquid(xyz_atoms_path, atoms, name, ptype)

    molar_mass = pobj.atoms.get_masses().sum()
    molar_length = len(pobj.atoms)

    pobj.set_system_info({"molar_mass": molar_mass, "molar_length": molar_length})
    pobj.set_surrounding_info()
    
    return pobj

def read_pgas(pobj_path:str)->PLiquid:
    ptype = 'gas'
    format = get_file_format(pobj_path)
    atoms = read(pobj_path,format=format)
    name = get_filename(pobj_path)

    xyz_atoms_path = os.path.join("/".join(pobj_path.split('/')[:-1]), f'pinp_{name}.xyz')
    write(xyz_atoms_path, atoms, format='xyz')

    pobj = PGas(xyz_atoms_path, atoms, name, ptype)

    molar_mass = pobj.atoms.get_masses().sum()
    molar_length = len(pobj.atoms)

    pobj.set_system_info({"molar_mass": molar_mass, "molar_length": molar_length})
    pobj.set_surrounding_info()
    
    return pobj


def read_pcell(cell_path:str)->PCell:

    ptype = 'cell'
    format = get_file_format(cell_path)
    atoms = read(cell_path,format=format)
    cell = atoms.cell
    name = 'cell'
    pobj = PCell(cell_path, cell, name, ptype)
    pobj.set_system_info()
    pobj.set_surrounding_info()
    
    return pobj

def read_pobj(pobj_path:str, ptype:str)->PObj:
    if ptype == 'solid':
        return read_psolid(pobj_path)
    elif ptype == 'liquid':
        return read_pliquid(pobj_path)
    elif ptype == 'gas':
        return read_pgas(pobj_path)
    elif ptype == 'cell':
        return read_pcell(pobj_path)
    else:
        raise ValueError(f"The ptype {ptype} is not valid.")
    
def check_pcell(pcell:PCell)->None:
    cell_array = pcell.cell.array

    if not cell_array:
        print(f"The cell array of {pcell.name} is not set.")
        return False
    
    if cell_array.shape != (3,3):
        print(f"The cell array of {pcell.name} is not a 3x3 array.")
        return False
    
    if not np.allclose([np.dot(cell_array[i], cell_array[j]) for i,j in [(0,1), (1,2), (0,2)]], 0, atol=1e-6):
        print(f"{pcell.name}의 셀 벡터들이 서로 직교하지 않습니다.")
        current_angles = [np.degrees(np.arccos(np.dot(cell_array[i], cell_array[j]) / (np.linalg.norm(cell_array[i]) * np.linalg.norm(cell_array[j])))) for i,j in [(0,1), (1,2), (0,2)]]
        print(f"현재 셀 벡터들의 각도: {current_angles}")
        return False
    
    return True

def density_to_number(density:float, molar_mass:float, molar_atom_number:float, cell_volume:float)->int:
    # density = [g/cm^3]
    # molar_mass = [g/mol]
    # cell_volume = [Angstrom^3]
    # return number of atoms

    density = density * (1e-8**3) * (1/molar_mass) * (6.02e23) # g/cm^3 -> molecule_number /Angstrom^3

    number = density * cell_volume # molecule_number /Angstrom^3 * Angstrom^3 -> molecule_number

    
    return int(number)


def read_liquid_src(src_dir:str)->List[PLiquid]:
    pobjs = []
    liquid_dir = os.path.join(src_dir, 'liquid')
    for file in os.listdir(liquid_dir):
        if file.startswith('pinp_'):
            continue
        pobj = read_pliquid(os.path.join(liquid_dir, file))
        pobjs.append(pobj)
    return pobjs

def read_gas_src(src_dir:str)->List[PGas]:
    pobjs = []
    gas_dir = os.path.join(src_dir, 'gas')
    for file in os.listdir(gas_dir):
        if file.startswith('pinp_'):
            continue
        pobj = read_pgas(os.path.join(gas_dir, file))
        pobjs.append(pobj)
    return pobjs

def read_solid_src(src_dir:str)->List[PSolid]:
    pobjs = []
    solid_dir = os.path.join(src_dir, 'solid')
    for file in os.listdir(solid_dir):
        if file.startswith('pinp_'):
            continue
        pobj = read_psolid(os.path.join(solid_dir, file))
        pobjs.append(pobj)
    return pobjs

def read_src(src_dir:str)->Dict[str, List[PObj]]:
    pobjs = {"cell":None, "liquid":[], "gas":[], "solid":[]}
    pcell = read_pcell(os.path.join(src_dir, 'cell_POSCAR'))

    pliquids = read_liquid_src(src_dir)
    pgases = read_gas_src(src_dir)
    psolids = read_solid_src(src_dir)

    pobjs["cell"] = pcell
    pobjs["liquid"] = pliquids
    pobjs["gas"] = pgases
    pobjs["solid"] = psolids
    return pobjs

def write_packmol_header(tolerance:float, seed:int)->str:
    header = f"tolerance {tolerance:.1f}\nfiletype xyz\nseed {seed}\n\n"
    return header

def write_liquid_gas_packmol_inp(pliquids:List[PLiquid], pgases:List[PGas])->None:
    packmol_str = ""
    for pobj in pliquids + pgases:
        packmol_str += pobj.to_packmol_str()
    return packmol_str





            



    