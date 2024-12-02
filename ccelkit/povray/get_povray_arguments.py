from argparse import ArgumentParser

def get_povray_parser(subparsers):
    """Set up parser for visual command."""
    parser_povray = subparsers.add_parser('povray', help='for povray visualization')
    parser_povray.add_argument("-i", "--input_filepath", type=str, required=True, help="input structure file path")
    parser_povray.add_argument("-o", "--output_filepath", type=str, required=True, help="output image file path")
    parser_povray.add_argument("-r", "--repeat_atom", type=int, nargs='+', default=[1, 1, 1], help="repeatation")
    parser_povray.add_argument("-ori", "--orientation", type=float, nargs='+', default=[+0.955480, +0.294974, -0.006949, -0.042581, +0.161156, +0.986010, +0.291967, -0.941817, +0.166542], help="camera orientation")
    parser_povray.add_argument("-c", "--cell_on", action='store_true', help="visual cell")
    parser_povray.add_argument("-t", "--transmittances", type=float, nargs='+', default=None, help="atom transmittances")
    parser_povray.add_argument("-H", "--heatmaps", type=float, nargs='+', default=None, help="atom heatmaps")
    parser_povray.add_argument("-w", "--canvas_width", type=int, default=960, help="pixel of width")
    return parser_povray

