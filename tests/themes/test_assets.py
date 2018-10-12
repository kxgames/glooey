#!/usr/bin/env python3

import pytest, json
from pyglet.resource import ResourceNotFoundException
from glooey.themes import ResourceLoader

@pytest.mark.parametrize("theme", ["golden", "kenney"])
def test_assets_installed(theme):
    assets = ResourceLoader(theme)

    # Make sure that the test errors on a resource that doesn't exist.
    with pytest.raises(ResourceNotFoundException):
        assets.location('nonexistent')

    # Load the list of assets that should be included for this theme.
    with open(f'{theme}_assets.json') as fp:
        manifest = json.load(fp)

    # If all these paths exist, we shouldn't get any exceptions asking for 
    # their locations:
    for path in manifest:
        assets.location(path)
