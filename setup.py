import distutils.core

# Uploading to PyPI
# =================
# $ python setup.py register -r pypi
# $ python setup.py sdist upload -r pypi

version = '0.0'
distutils.core.setup(
        name='glooey',
        version=version,
        author='Kale Kundert and Alex Mitchell',
        packages=['glooey'],
        url='https://github.com/kxgames/glooey',
        download_url='https://github.com/kxgames/glooey/tarball/'+version,
        license='LICENSE.txt',
        description="An object-oriented GUI library for pyglet.",
        long_description=open('README.rst').read(),
        keywords=['pyglet', 'gui', 'library'],
        install_requires=[
            'pyglet',
            'more_itertools',
            # not available on PyPI yet: 'vecrec', 
        ],
)
