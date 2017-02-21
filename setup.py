from os.path import abspath, dirname, join
from sys import argv, path

# To temporarily modify sys.path
SETUP_DIR = abspath(dirname(__file__))

try:
    from setuptools import setup, find_packages
except ImportError:
    path.insert(0, SETUP_DIR)
    import ez_setup
    path.pop(0)
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

# Import version to get the version string
path.insert(0, join(SETUP_DIR, 'mminte'))
from version import get_version, update_release_version
path.pop(0)
version = get_version(pep440=True)

# If building something for distribution, ensure the VERSION
# file is up to date
if 'sdist' in argv or 'bdist_wheel' in argv:
    update_release_version()

requirements = [
    'six',
    'pandas>=0.18.0',
    'cobra>=0.5.4'
]

try:
    with open('README.rst') as handle:
        description = handle.read()
except:
    description = ''

setup(
    name='mminte',
    version=version,
    packages=find_packages(),
    scripts=['bin/launchMMinte.py'],
    setup_requires=[],
    install_requires=requirements,
    tests_require=['pytest'],
    package_data={
         '': ['VERSION']
    },
    author='Helena Mendes-Soares, Michael Mundy, Luis Mendes Soares, Nicholas Chia',
    author_email='microbialmetabolicinteractions@gmail.com',
    description='Microbial Metabolic interactions',
    long_description=description,
    license='BSD',
    keywords='metabolism biology optimization flux balance analysis fba',
    url='https://github.com/mendessoares/mminte',
    # download_url='https://pypi.python.org/pypi/mminte',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    platforms='GNU/Linux, Mac OS X >= 10.7, Microsoft Windows >= 7')
