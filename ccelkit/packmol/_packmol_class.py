from ase import Atoms, Atom
from abc import abstractmethod

import numpy as np
from ase.cell import Cell

class PObj:
    def __init__(self,path:str, atoms:Atoms, name:str, type:str):
        self.path = path
        self.atoms = atoms
        self.name = name
        self.type = type
        self.info = {'system':{'name':name,'type':type},'surrounding':{}}

    def __str__(self):
        return f"{self.name} {self.type}"
    
    @abstractmethod
    def set_system_info(self,system_info:dict)->None:
        pass

    @abstractmethod
    def set_surrounding_info(self,surrounding_info:dict)->None:
        pass

    @abstractmethod
    def to_packmol_str(self)->str:
        pass

    @abstractmethod
    def get_info(self)->dict:
        pass

class PSolid(PObj):
    def __init__(self,path:str, atoms:Atoms, name:str, type:str):
        super().__init__(path,atoms,name,type)

    def set_system_info(self,system_info:dict=None)->None:
        if system_info is None:
            system_info = {}
        self.info['system']['center_of_mass'] = {'x': self.atoms.get_center_of_mass()[0]
                                                 ,'y': self.atoms.get_center_of_mass()[1]
                                                 ,'z': self.atoms.get_center_of_mass()[2]}
        self.info['system']['weight'] = self.atoms.get_masses().sum()
        self.info['system']['total_weight'] = self.atoms.get_masses().sum()
        self.info['system']['number'] = 1
        self.info['system'].update(system_info)

    def set_surrounding_info(self,surrounding_info:dict=None)->None:
        if surrounding_info is None:
            surrounding_info = {}
        self.info['surrounding'].update(surrounding_info)

    def to_packmol_str(self)->str:
        self.packmol_str = f'''
        structure {self.path}
            number {self.info['system']['number']}
            center
            fixed {self.info['system']['center_of_mass']['x']} {self.info['system']['center_of_mass']['y']} {self.info['system']['center_of_mass']['z']} 0. 0. 0.
        end structure
        '''
        return self.packmol_str
    
    def get_info(self)->dict:
        return self.info

class PLiquid(PObj):
    def __init__(self,path:str, atoms:Atoms, name:str, type:str):
        super().__init__(path,atoms,name,type)

    def set_system_info(self,system_info:dict=None)->None:
        if system_info is None:
            system_info = {}
        self.info['system'].update(system_info)

    def set_surrounding_info(self,surrounding_info:dict=None)->None:
        if surrounding_info is None:
            surrounding_info = {}
        self.info['surrounding'].update(surrounding_info)

    def to_packmol_str(self)->str:
        self.packmol_str = f'''
structure {self.path}
    number {self.info['system']['num_molecules']}
    inside box {self.info['system']['x_min']} {self.info['system']['y_min']} {self.info['system']['z_min']} {self.info['system']['x_max']} {self.info['system']['y_max']} {self.info['system']['z_max']}
end structure
        '''
        return self.packmol_str

    def get_info(self)->dict:
        return self.info

class PGas(PObj):
    def __init__(self,path:str, atoms:Atoms, name:str, type:str):
        super().__init__(path,atoms,name,type)

    def set_system_info(self,system_info:dict=None)->None:
        if system_info is None:
            system_info = {}
        self.info['system'].update(system_info)

    def set_surrounding_info(self,surrounding_info:dict=None)->None:
        if surrounding_info is None:
            surrounding_info = {}
        self.info['surrounding'].update(surrounding_info)

    def to_packmol_str(self)->str:
        self.packmol_str = f'''
structure {self.path}
    number {self.info['system']['num_molecules']}
    inside box {self.info['system']['x_min']} {self.info['system']['y_min']} {self.info['system']['z_min']} {self.info['system']['x_max']} {self.info['system']['y_max']} {self.info['system']['z_max']}
end structure
        '''
        return self.packmol_str
    def get_info(self)->dict:
        return self.info

class PCell(PObj):
    def __init__(self,path:str, cell:Cell, name:str, type:str):
        super().__init__(path,cell,name,type)
        self.info['system']['cell'] = cell

    def set_system_info(self,system_info:dict=None)->None:
        if system_info is None:
            system_info = {}
        self.info['system'].update(system_info)

    def set_surrounding_info(self,surrounding_info:dict=None)->None:
        if surrounding_info is None:
            surrounding_info = {}
        self.info['surrounding'].update(surrounding_info)

    def to_packmol_str(self)->str:
        pass

    def get_info(self)->dict:
        return self.info


