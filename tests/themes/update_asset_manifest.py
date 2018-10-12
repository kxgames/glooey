#!/usr/bin/env python3

"""\
Recreate the list of assets expected to be included in the distributed package.

Usage:
    update_asset_manifest.py
"""

import docopt, json
from fnmatch import fnmatch
from pathlib import Path

args = docopt.docopt(__doc__)
ASSETS = Path(__file__).resolve().parents[2] / 'glooey/themes/assets'

def make_manifest(theme, globs=('**/*.png',), exclude=()):
    theme_dir = ASSETS / theme

    paths = set()
    for glob in globs:
        paths.update(
                str(x.relative_to(theme_dir))
                for x in theme_dir.glob(glob)
        )

    for glob in exclude:
        for path in sorted(paths):
            if fnmatch(path, glob):
                paths.discard(path)
                break

    with open(f'{theme}_assets.json', 'w') as fp:
        json.dump(sorted(paths), fp)

make_manifest('golden', exclude=('heroes_and_villains.png',))
make_manifest('kenney')
