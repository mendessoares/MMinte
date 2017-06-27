from setuptools import setup, find_packages
from setuptools.command.install import install as _install
import os
from os.path import join, exists
from sys import platform
from shutil import copy, rmtree
import tarfile
from tempfile import mkdtemp
from warnings import warn
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


def download_unpack_tar(url, folder, download_file_name):
    """ Download a tar file from a URL and extract the contents to a folder.

    Parameters
    ----------
    url : str
        URL of tar file to download
    folder : str
        Path to folder for storing downloaded file and extracting tar file to
    download_file_name : str
        Name of downloaded tar file
    """

    print('downloading from {0}'.format(url))
    download_file = join(folder, download_file_name)
    urlretrieve(url, download_file)

    print('extracting from {0}'.format(download_file))
    tarfile_handle = tarfile.open(download_file)
    tarfile_handle.extractall(path=folder)
    tarfile_handle.close()

    try:
        os.unlink(download_file)
    except EnvironmentError as e:
        warn('Error removing file: {0}'.format(e))

    return


def find_exe_in_path(exe):
    """ Check that an executable exists in one of the directories of the PATH variable.

    Parameters
    ----------
    exe : str
        Name of executable

    Returns
    -------
    str or None
        Fully-qualified path to executable or None if executable is not found
    """

    paths = os.environ['PATH'].split(os.pathsep)
    for path in paths:
        full_exe = join(path, exe)
        if exists(full_exe):
            if os.access(full_exe, os.X_OK):
                return path
    return None


def install_blast(install_folder, replace_install=False):
    """ Download and install the blast+ software if not already installed.

    Parameters
    ----------
    install_folder : str
        Path to folder mminte package is being installed in
    replace_install : bool
        When True, replace an existing install
    """

    # MMinte only requires blastn from the suite of blast commands.
    # Check if blastn is already installed on the system.
    blast_exe = 'blastn'
    blast_exe_path = find_exe_in_path(blast_exe)

    if blast_exe_path is None or replace_install:
        blast_version = '2.2.22'
        print('installing blast+ {0}'.format(blast_version))

        # Select the file to download from NCBI based on the platform this install is running on.
        if platform.startswith('linux'):
            blast_file = 'ncbi-blast-{0}+-x64-linux.tar.gz'.format(blast_version)
        elif platform.startswith('darwin'):
            blast_file = 'ncbi-blast-{0}+-universal-macosx.tar.gz'.format(blast_version)
        elif platform.startswith('win32'):
            blast_file = 'ncbi-blast-{0}+-x64-win64.tar.gz'.format(blast_version)
        elif platform.startswith('cygwin'):
            blast_file = 'something different?'
        else:
            raise EnvironmentError('platform {0} is not supported'.format(platform))
        blast_url = 'ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/{0}/{1}'.format(blast_version, blast_file)

        # Create a temporary folder for downloading and extracting blast package.
        temp_folder = mkdtemp(prefix='blast_download_')

        # Download and extract the blast package.
        download_unpack_tar(blast_url, temp_folder, blast_file)

        # Copy the blast executable to the mminte package's bin folder.
        download_blast_exe = join(temp_folder, 'ncbi-blast-{0}+'.format(blast_version), 'bin', blast_exe)
        copy(download_blast_exe, join(install_folder, blast_exe))

        # Remove the extracted blast package.
        try:
            rmtree(temp_folder)
        except EnvironmentError as e:
            warn('Error removing temporary folder {0}: {1}'.format(temp_folder, e))

        print('installed {0} at {1}'.format(blast_exe, install_folder))

    else:
        target = join(install_folder, blast_exe)
        print('adding link at {0} to {1}'.format(target, blast_exe_path))
        if not exists(target):
            os.symlink(blast_exe_path, target)
        print('found {0} installed at {1}'.format(blast_exe, blast_exe_path))


class Install(_install):
    """ Custom setuptools install command. """

    _install.user_options = _install.user_options+[('replace-dependencies-install', None, 'replace dependencies already installed')]

    def initialize_options(self):
        self.replace_dependencies_install = False
        _install.initialize_options(self)

    def finalize_options(self):
        _install.finalize_options(self)

    def run(self):
        _install.run(self)

        # Get the final script install location for both source and wheel.
        install_scripts = os.path.join(self.install_base, 'bin')
        install_blast(install_scripts, replace_install=self.replace_dependencies_install)


requirements = [
    'biopython>=1.66',
    'cobra>=0.5.11',
    'lxml',
    'mackinac>=0.8.3',
    'networkx>=1.11',
    'numpy>=1.12.0',
    'pandas>=0.18.0',
    'python-libsbml>=5.12.0',
    'scipy>=0.18.0',
    'six',
    'tabulate'
]

extras = {
    'site': ['CherryPy>=10.2.0', 'DataSpyre>=0.2.6'],
    'test': ['pytest']
}

all_extras = {''}
for extra in extras.values():
    all_extras.update(extra)
extras['all'] = sorted(list(all_extras))

try:
    with open('README.rst') as handle:
        description = handle.read()
except:
    description = ''

setup(
    name='mminte',
    version='1.0.3',
    cmdclass={'install': Install},
    packages=find_packages(),
    scripts=['bin/launchMMinte'],
    setup_requires=[],
    install_requires=requirements,
    tests_require=extras['test'],
    extras_require=extras,
    package_data={
         '': ['data/db/*', 'test/data/*', 'site/static/*', 'notebooks/*']
    },
    author='Helena Mendes-Soares, Michael Mundy, Luis Mendes Soares, Nicholas Chia',
    author_email='microbialmetabolicinteractions@gmail.com',
    description='Microbial Metabolic interactions',
    long_description=description,
    license='BSD',
    keywords='metabolism biology optimization flux balance analysis fba',
    url='https://github.com/mendessoares/mminte',
    download_url='https://pypi.python.org/pypi/mminte',
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
