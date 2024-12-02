import os
from ase.io import read, write
from PIL import Image
import subprocess
from ._povray_utils import set_repeatation
from ._povray_utils import set_cell_on
from ._povray_utils import set_canvas_width
from ._povray_utils import set_transmittances
from ._povray_utils import set_heatmaps
from ._povray_utils import set_camera_orientation
from ._povray_utils import set_custom_colors
from ._povray_utils import parse_orientation
from ._povray_utils import create_config
import yaml
from typing import List,Dict
import click
def to_povray_image(input_filepath: str
                    , output_filepath: str
                    , repeatation: List[int]
                    , orientation: List[float]
                    , cell_on: bool
                    , transmittances: List[float]
                    , heatmaps: List[float]
                    , canvas_width: int
                    , color_species: Dict[str,List[float]]
                    , color_index: Dict[str,List[float]]):


    atoms = read(input_filepath)
    atoms = set_repeatation(atoms,repeatation)
    atoms = set_cell_on(atoms,cell_on)

    # POV-Ray 설정
    povray_settings = {}
    set_canvas_width(povray_settings, canvas_width)
    set_transmittances(povray_settings, transmittances)
    set_heatmaps(povray_settings, heatmaps)
    set_custom_colors(atoms, povray_settings, color_species, color_index)
    # set camera orientation, refer the "VESTA orientation tap"
    rotation = set_camera_orientation(povray_settings, orientation)

    povray_base_path = os.environ.get("POVRAY")
    if not povray_base_path:
        raise EnvironmentError("환경 변수 'POVRAY'가 설정되지 않았습니다.")
    povray_include_path = os.path.join(povray_base_path, "include")

    write('./temp.pov', atoms, rotation=rotation, povray_settings=povray_settings)
    with open('./temp.ini', 'a') as file:
        file.write(f'Library_Path="{povray_include_path}"\n')

    povray_command = ['povray', f'+L{povray_include_path}', "./temp.pov", 'temp.ini']
    subprocess.run(povray_command, check=True)

    temp_image_path = './temp.png'
    img = Image.open(temp_image_path)
    img.save(output_filepath)

    os.remove("./temp.ini")
    os.remove("./temp.pov")
    os.remove("./temp.png")
    return None
    
@click.group()
def visual(args):
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        target = config['target']
        input_filepath = config['input_filepath']
        output_filepath = config['output_filepath']
        repeatation = config['repeatation']
        orientation = parse_orientation(config['orientation'])
        cell_on = config['cell_on']
        transmittances = config['transmittances']
        heatmaps = config['heatmaps']
        canvas_width = config['canvas_width']
        color_species = config['color_species']
        color_index = config['color_index']

    else:
        target: str = args.target
        config: str = args.config
        input_filepath: str = args.input_filepath
        output_filepath: str = args.output_filepath
        repeatation: List[int] = args.repeatation
        orientation: List[float] = parse_orientation(args.orientation)
        cell_on: bool = args.cell_on
        transmittances:List[float]  = args.transmittances
        heatmaps:List[float] = args.heatmaps
        canvas_width: int = args.canvas_width
        color_species: Dict[str,List[float]] = args.color_species
        color_index: Dict[str,List[float]] = args.color_index

    files_to_be_processed = []
    files_to_be_saved = []
    if target:
        if (input_filepath or output_filepath):
            raise ValueError("input_filepath and output_filepath cannot be specified when target is specified")
        for root, _, files in os.walk('.'):
            for file in files:
                if target in file and not file.startswith('img_'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    files_to_be_processed.append(file_path)

                    if '.' in file:
                        file_name, _ = os.path.splitext(file)
                    else:
                        file_name = file
                    new_file_name = f"{file_name}.png"
                    new_file_path = os.path.abspath(os.path.join(root, new_file_name))
                    files_to_be_saved.append(new_file_path)
    else:
        files_to_be_processed.append(input_filepath)
        files_to_be_saved.append(output_filepath)

    files_to_be_saved = [os.path.join(os.path.dirname(path), 
                         'img_' + os.path.basename(path) if not os.path.basename(path).startswith('img_') else os.path.basename(path))
                         for path in files_to_be_saved]

    for input_filepath, output_filepath in zip(files_to_be_processed, files_to_be_saved):
        print(f"{input_filepath} -> {output_filepath}")
        to_povray_image(input_filepath, output_filepath, repeatation, orientation, cell_on, transmittances, heatmaps, canvas_width, color_species, color_index)

visual.add_command(create_config)
