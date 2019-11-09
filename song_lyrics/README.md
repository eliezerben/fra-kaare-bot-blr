# epub_to_images
epub_to_images.py is can convert epub of hv/mb to images.\
It works by first extracting the epub(which is just a collection of html files) after which [`pyppeteer`](https://pypi.org/project/pyppeteer) is used to atutomate the process of opening the html files in chromium and taking screenshot.

## Requirements
1. Install requirements \
  `pip install -r requirements.txt`
2. pyppeteer uses chromium internally. So after installing requirements, run the following which will download a copy of chromium.\
  `pyppeteer-install`\
  If this is not done, chromium will be downloaded on first use of pyppeteer.
3. There is a bug in pyppeteer currently which raises `pyppeteer.errors.NetworkError` error if an operation takes more than 20 seconds. The workaround is to downgrade `websockets` package.\
  `pip install websockets==6.0 --force-reinstall`\
  Refer [this issue](https://github.com/miyakogi/pyppeteer/issues/171).

## Usage
Run `python epub_to_images.py --help` to know how to use.
