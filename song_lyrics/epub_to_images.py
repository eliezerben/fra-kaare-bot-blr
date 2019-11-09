import argparse
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_args():
    """Parse and return command line arguments"""

    def epub_file(file_path):
        if not os.path.isfile(file_path) or not file_path.endswith('.epub'):
            raise argparse.ArgumentTypeError(f"'{file_path}' does not exist or is not an epub file")
        else:
            return file_path

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-b', '--book',
        choices=['hv', 'mb'],
        required=True,
        help='type of song book',
    )
    arg_parser.add_argument(
        '-f', '--file',
        required=True,
        type=epub_file,
        help='path to epub file'
    )
    arg_parser.add_argument(
        '-o', '--output_dir',
        help="path to output directory where images should be stored. Default output dir is './hv' or '.mb' based on --book argument"
    )

    args = arg_parser.parse_args()
    if not args.output_dir:
        args.output_dir = os.path.join(SCRIPT_DIR, args.book_type)

    return args


if __name__ == '__main__':
    args = get_args()
    book_type = args.book
    epub_file_path = args.file
    output_dir = args.output_dir

    
