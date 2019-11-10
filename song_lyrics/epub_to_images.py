from zipfile import ZipFile
import argparse
import tempfile
import shutil
import os
import asyncio

from bs4 import BeautifulSoup
import pyppeteer

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
        help="path to output directory where images should be stored. Default output dir is './HV' or './MB' based on --book argument"
    )

    args = arg_parser.parse_args()
    if not args.output_dir:
        args.output_dir = os.path.join(SCRIPT_DIR, args.book.upper())

    return args


def get_songnumber_file_pairs(songnumber_index_file_path):
    """Read songnumber index file and return list of item in the format:
        [
            (1, 'song_1.html'),
            (2, 'song_2.html')
        ]
    """
    index_file_soup = BeautifulSoup(open(songnumber_index_file_path), 'html.parser')
    anchors = index_file_soup.find_all('a', class_='index-songnumbers2')

    songnumber_file_pairs = []
    for anchor in anchors:
        songnumber_file_pairs.append((
            int(anchor.get_text(strip=True)),
            anchor.get('href')
        ))

    return songnumber_file_pairs


async def get_images(book_type, songnumber_file_pairs, output_dir):
    """Use pyppeteer to take screenshots of html files and save them in output_dir"""

    browser = await pyppeteer.launch()
    page = await browser.newPage()
    viewport_width = 411
    await page.setViewport({
        'width': viewport_width,
        'height': page.viewport['height'],
        'deviceScaleFactor': 2  # Scale page 2x
    })

    songs_count = len(songnumber_file_pairs)
    print(f'Saving images to: {output_dir}')
    for index, pair in enumerate(songnumber_file_pairs, start=1):
        (songnumber, file_path) = pair
        print(f'    Saving Song: {index}/{songs_count}')
        await page.goto(file_path)
        if book_type == 'hv':
            # Hide the [Index] link in HV
            await page.evaluate('''
                indexLink = document.querySelector('.indexlink')
                if (indexLink) {
                    indexLink.style.display = 'none';
                }
            ''')
        body = await page.querySelector('html')
        await body.screenshot(path=os.path.join(output_dir, f'{songnumber}.png'))
    await browser.close()


if __name__ == '__main__':
    args = get_args()
    book_type = args.book
    epub_file_path = args.file
    output_dir = args.output_dir

    # Create temporary directory
    epub_extract_dir = tempfile.mkdtemp()
    try:
        with ZipFile(epub_file_path, 'r') as zip_ref:
            zip_ref.extractall(epub_extract_dir)

        songnumbers_index_file_filter = [file
                                         for file in os.listdir(epub_extract_dir)
                                         if file.endswith('index-songnumbers.html')]

        if not songnumbers_index_file_filter:
            raise Exception('Songnumber Index file not found!')

        songnumbers_index_file_path = os.path.join(epub_extract_dir, songnumbers_index_file_filter[0])
        songnumber_file_pairs = get_songnumber_file_pairs(songnumbers_index_file_path)
        songnumber_file_pairs_full_url = [
                                            (
                                                pair[0],
                                                'file://' + os.path.join(epub_extract_dir, pair[1])
                                            ) for pair in songnumber_file_pairs
                                         ]

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        asyncio.get_event_loop().run_until_complete(get_images(book_type, songnumber_file_pairs_full_url, output_dir))

    finally:
        # Delete temporary directory
        shutil.rmtree(epub_extract_dir)
