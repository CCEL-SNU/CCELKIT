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
import yaml
from typing import List,Dict

def visual(args):
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        input_filepath = config['input_filepath']
        output_filepath = config['output_filepath']
        repeatation = config['repeatation']
        orientation = config['orientation']
        cell_on = config['cell_on']
        transmittances = config['transmittances']
        heatmaps = config['heatmaps']
        canvas_width = config['canvas_width']
        color_species = config['color_species']
        color_index = config['color_index']

    else:
        config: str = args.config
        input_filepath: str = args.input_filepath
        output_filepath: str = args.output_filepath
        repeatation: List[int] = args.repeatation
        orientation: List[float] = args.orientation
        cell_on: bool = args.cell_on
        transmittances:List[float]  = args.transmittances
        heatmaps:List[float] = args.heatmaps
        canvas_width: int = args.canvas_width
        color_species: Dict[str,List[float]] = args.color_species
        color_index: Dict[str,List[float]] = args.color_index


    # Read atoms
    atoms = read(input_filepath)

    # 구조 생성 및 반복
    atoms = set_repeatation(atoms,repeatation)

    # 셀 시각화 설정
    atoms = set_cell_on(atoms,cell_on)

    # POV-Ray 설정
    # initialize setup dictionary
    povray_settings = {}

    set_canvas_width(povray_settings, canvas_width)

    # set transmittances
    set_transmittances(povray_settings, transmittances)

    # set heatmap
    set_heatmaps(povray_settings, heatmaps)

    # set atom color by species
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
