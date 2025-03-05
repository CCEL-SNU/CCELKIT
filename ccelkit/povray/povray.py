import os
from ase.io import read, write
from PIL import Image
import subprocess
from ._povray_utils import set_repeatation
from ._povray_utils import set_cell_off
from ._povray_utils import set_canvas_width
from ._povray_utils import set_transmittances
from ._povray_utils import set_heatmaps
from ._povray_utils import set_camera_orientation
from ._povray_utils import set_custom_colors
from ._povray_utils import parse_orientation
from ._povray_utils import create_config
from ._povray_utils import set_position_smoothing
from ._povray_utils import set_postfix
from ._povray_utils import set_duration
import yaml
from typing import List,Dict,Union
from tqdm import tqdm

def to_povray_image(input_filepath: str
                    , output_filepath: str
                    , repeatation: List[int] = [1,1,1]
                    , orientation: str = 'perspective'
                    , cell_off: bool = False
                    , transmittances: Union[List[float],None] = None
                    , heatmaps: Union[List[float],None] = None
                    , canvas_width: int = 1000
                    , color_species: Union[Dict[str,List[float]],None] = None
                    , color_index: Union[Dict[str,List[float]],None] = None
                    , frame_per_second: int = 24):
    
    orientation = parse_orientation(orientation)
    
    is_trajectory = input_filepath.endswith('XDATCAR') or input_filepath.endswith('.traj')
    temp_images = []
    
    atoms_list = read(input_filepath, index=':') if is_trajectory else [read(input_filepath)]
    
    for i, atoms in enumerate(atoms_list):
        atoms = set_position_smoothing(atoms)
        atoms = set_repeatation(atoms, repeatation)
        atoms = set_cell_off(atoms, cell_off)

        # POV-Ray 설정
        povray_settings = {}
        if is_trajectory:
            povray_settings['background'] = 'White'
        set_canvas_width(povray_settings, canvas_width)
        set_transmittances(povray_settings, transmittances)
        set_heatmaps(povray_settings, heatmaps)
        set_custom_colors(atoms, povray_settings, color_species, color_index)
        rotation = set_camera_orientation(povray_settings, orientation)

        povray_base_path = os.environ.get("POVRAY")
        if not povray_base_path:
            raise EnvironmentError("환경 변수 'POVRAY'가 설정되지 않았습니다.")
        povray_include_path = os.path.join(povray_base_path, "include")

        write('./temp.pov', atoms, rotation=rotation, povray_settings=povray_settings)
        with open('./temp.ini', 'a') as file:
            file.write(f'Library_Path="{povray_include_path}"\n')

        povray_command = ['povray', '-D', f'+L{povray_include_path}', "./temp.pov", 'temp.ini']
        with subprocess.Popen(povray_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as process:
            process.wait()

        if is_trajectory:
            img = Image.open('./temp.png')
            new_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
            new_img.paste(img, (0, 0))
            temp_images.append(new_img)
            img.close()
        else:
            img = Image.open('./temp.png')
            img.save(output_filepath)
            img.close()

        os.remove("./temp.ini")
        os.remove("./temp.pov")
        os.remove("./temp.png")

    if is_trajectory and temp_images:
        try:
            if not output_filepath.endswith('.gif'):
                output_filepath = os.path.splitext(output_filepath)[0] + '.gif'
                
            temp_images = [img.convert('RGB') for img in temp_images]
            temp_images[0].save(
                output_filepath,
                save_all=True,
                append_images=temp_images[1:],
                duration=set_duration(frame_per_second),
                loop=0,
                disposal=2
            )
        finally:
            for img in temp_images:
                img.close()

    return None
    
def visual(args):
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        target = config['target']
        input_filepath = config['input_filepath']
        output_filepath = config['output_filepath']
        repeatation = config['repeatation']
        orientation = config['orientation']
        cell_off = config['cell_off']
        transmittances = config['transmittances']
        heatmaps = config['heatmaps']
        canvas_width = config['canvas_width']
        color_species = config['color_species']
        color_index = config['color_index']
        frame_per_second = config['frame_per_second']
        postfix = config['postfix']
    else:
        target: str = args.target
        config: str = args.config
        input_filepath: str = args.input_filepath
        output_filepath: str = args.output_filepath
        repeatation: List[int] = args.repeatation
        orientation: List[float] = args.orientation
        cell_off: bool = args.cell_off
        transmittances:List[float]  = args.transmittances
        heatmaps:List[float] = args.heatmaps
        canvas_width: int = args.canvas_width
        color_species: Dict[str,List[float]] = args.color_species
        color_index: Dict[str,List[float]] = args.color_index
        frame_per_second: int = args.frame_per_second
        postfix: str = args.postfix

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
                    new_file_name = set_postfix(file_name + postfix)
                    new_file_path = os.path.abspath(os.path.join(root, new_file_name))
                    files_to_be_saved.append(new_file_path)
    else:
        files_to_be_processed.append(input_filepath)
        files_to_be_saved.append(output_filepath)

    files_to_be_saved = [os.path.join(os.path.dirname(path), 
                         'img_' + os.path.basename(path) if not os.path.basename(path).startswith('img_') else os.path.basename(path))
                         for path in files_to_be_saved]

    
    for input_filepath, output_filepath in tqdm(zip(files_to_be_processed, files_to_be_saved), 
                                              desc="이미지 생성 중", 
                                              total=len(files_to_be_processed),
                                              unit="개"):
        print(f"{input_filepath} -> {output_filepath}")
        to_povray_image(input_filepath, output_filepath
                        , repeatation, orientation
                        , cell_off, transmittances
                        , heatmaps, canvas_width
                        , color_species, color_index
                        , frame_per_second)
