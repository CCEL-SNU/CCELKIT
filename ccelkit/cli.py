from argparse import ArgumentParser
import os, subprocess, copy
from ase.calculators.vasp import Vasp
from ase.io import read, write
from PIL import Image
import numpy as np
from scipy.spatial.transform import Rotation as R
from .povray import visual
from .povray._povray_utils import *

from .packmol import make_system, init_dir, init_config

def main():
    parser = ArgumentParser(description="Function commands")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    parser_visual = subparsers.add_parser('visual', help='for povray visualization')

    parser_visual.add_argument("--target",type=str,default=None,help="target file path")
    parser_visual.add_argument("-c","--config",type=str,default=None,help="config file path")
    parser_visual.add_argument("-i","--input_filepath",type=str,default=None,help="input structure file path")
    parser_visual.add_argument("-o","--output_filepath",type=str,default=None,help="output image file path")
    parser_visual.add_argument("-r","--repeatation",type=int,nargs='+',default=[1,1,1],help="repeatation")
    parser_visual.add_argument("-ori","--orientation",type=str,default="+0.955480 +0.294974 -0.006949 -0.042581 +0.161156 +0.986010 +0.291967 -0.941817 +0.166542",help="camera orientation")
    parser_visual.add_argument("--cell_off",action='store_true',help="turn off cell")
    parser_visual.add_argument("-t","--transmittances",type=float,nargs='+',default=None,help="atom transmittances")
    parser_visual.add_argument("-H","--heatmaps",type=float,nargs='+',default=None,help="atom heatmaps")
    parser_visual.add_argument("-w","--canvas_width",type=int,default=960,help="pixel of width")
    parser_visual.add_argument("-cs","--color_species",type=dict,default=None,help="color of the atoms by species")
    parser_visual.add_argument("-ci","--color_index",type=dict,default=None,help="color of the atoms by index")
    parser_visual.add_argument("-fps","--frame_per_second",type=int,default=24,help="frame per second")
    
    visual_subparsers = parser_visual.add_subparsers(dest="visual_command", help="Visual commands")
    visual_subparsers.add_parser("create_config", help="create default config file")

    parser_make_system = subparsers.add_parser('make_system', help='make packmol system')
    parser_make_system.add_argument("-c","--config",type=str,default=None,help="config file path")

    make_system_subparsers = parser_make_system.add_subparsers(dest="make_system_command", help="Make system commands")
    make_system_subparsers.add_parser("init_dir", help="initialize directory")
    make_system_subparsers.add_parser("init_config", help="initialize config")

    args = parser.parse_args()

    if args.command == 'visual':
        if hasattr(args, 'visual_command') and args.visual_command == 'create_config':
            create_config()
        else:
            visual(args=args)
    elif args.command == 'make_system':
        if hasattr(args, 'make_system_command') and args.make_system_command == 'init_dir':
            init_dir()
        elif hasattr(args, 'make_system_command') and args.make_system_command == 'init_config':
            init_config()
        else:
            make_system(args.config)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()



