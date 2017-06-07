#!/usr/bin/env python3

"""\
Usage:
    zip_demos.py [<directory>]
"""

import docopt
from pathlib import Path
from zipfile import ZipFile

def demo_uses_asset(asset, content):
    asset = Path(asset)

    if f"'{asset.name}'" in content:
        return True

    if asset.suffix == '.py':
        return f'import {asset.stem}' in content


args = docopt.docopt(__doc__)
directory = Path(args['<directory>'] or '.')

for demo in directory.glob('*.py'):
    demo = Path(demo)

    with demo.open() as file:
        content = file.read()

    # Skip python scripts that don't seem to have main functions.
    if not content.strip().endswith('pyglet.app.run()'):
        continue

    with ZipFile(f'{directory / demo.stem}_assets.zip', 'w') as zip:
        print(f"Making archive: '{zip.filename}'")

        for asset in directory.glob('*'):
            if asset == demo or demo_uses_asset(asset, content):
                zip.write(str(asset))
                print(f"  + {asset}")



