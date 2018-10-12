#!/usr/bin/env python3

import pytest, json
from pathlib import Path
from pyglet.resource import ResourceNotFoundException
from glooey.themes import ResourceLoader

@pytest.mark.parametrize("theme", ["golden", "kenney"])
def test_assets_installed(theme):
    assets = ResourceLoader(theme)

    # Make sure that the test errors on a resource that doesn't exist.
    with pytest.raises(ResourceNotFoundException):
        assets.location('nonexistent')

    # Load the list of assets that should be included for this theme.
    manifest_json = Path(__file__).parent / f'{theme}_assets.json'
    with manifest_json.open() as fp:
        manifest = json.load(fp)

    # If all these paths exist, we shouldn't get any exceptions asking for 
    # their locations:
    for path in manifest:
        assets.location(path)
