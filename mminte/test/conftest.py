import pytest
from os.path import join, abspath, dirname
from tempfile import gettempdir


@pytest.fixture(scope='session')
def data_folder():
    mminte_folder = abspath(join(dirname(abspath(__file__)), '..'))
    return join(mminte_folder, 'test', 'data', '')


@pytest.fixture(scope='session')
def test_folder():
    return gettempdir()


@pytest.fixture(scope='session')
def model_files():
    return ['BT.sbml', 'FP.sbml']
