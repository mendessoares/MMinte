from setuptools import setup, find_packages

requirements = [
    'six',
    'pandas>=0.18.0',
    'cobra>=0.5.4',
    'mackinac>=0.8.0'
]

try:
    with open('README.rst') as handle:
        description = handle.read()
except:
    description = ''

setup(
    name='mminte',
    version='0.2.0',
    packages=find_packages(),
    scripts=['bin/launchMMinte'],
    setup_requires=[],
    install_requires=requirements,
    tests_require=['pytest'],
    package_data={
         '': ['data/db/*']
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
