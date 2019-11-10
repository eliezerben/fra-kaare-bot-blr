# epub_to_images
epub_to_images.py is can convert epub of hv/mb to images.\
It works by first extracting the epub(which is just a collection of html files) after which [`pyppeteer`](https://pypi.org/project/pyppeteer) is used to atutomate the process of opening the html files in chromium and taking screenshot.

## Requirements
1. Install requirements \
  `pip install -r requirements.txt`
2. pyppeteer uses chromium internally. So after installing requirements, run the following which will download a copy of chromium.\
  `pyppeteer-install`\
  If this is not done, chromium will be downloaded on first use of pyppeteer.

## Usage
Run `python epub_to_images.py --help` to know how to use.

## Note
1. There is a bug in pyppeteer currently which raises `pyppeteer.errors.NetworkError` error if an operation takes more than 20 seconds. The workaround is to downgrade `websockets` package.\
  `pip install websockets==6.0 --force-reinstall`\
  Refer [this issue](https://github.com/miyakogi/pyppeteer/issues/171).
2. If you encounter error `error while loading shared libraries: libX11-xcb.so.1: cannot open shared object file: No such file or directory`, install these dependencies:\
  `sudo apt-get install gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget`\
  Refer [this issue](https://github.com/miyakogi/pyppeteer/issues/82).
