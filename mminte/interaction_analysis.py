from itertools import combinations
from pandas import DataFrame
from multiprocessing import Pool, cpu_count

from .interaction_worker import growth_rate_columns, create_pair_model, compute_growth_rates


def create_interaction_models(source_models, output_folder='data', n_processes=None):
    """ Create two species community models for all pairs in a community.

    Parameters
    ----------
    source_models : list of str
        List of path names to model files
    output_folder : str
        Path to folder where output community model files are saved
    n_processes: int, optional
        Number of processes in job pool

    Returns
    -------
    list of str
        List of path names to two species community model files
    """

    if len(source_models) < 2:
        raise ValueError('There must be at least two models in the list of source models')

    if n_processes is None:
        n_processes = min(cpu_count(), 4)
    pool = Pool(n_processes)
    result_list = [pool.apply_async(create_pair_model, (pair, output_folder))
                   for pair in combinations(source_models, 2)]
    output_models = [result.get() for result in result_list]
    return output_models


def calculate_growth_rates(pair_models, media_filename, n_processes=None):
    """ Calculate growth rates for all pairs in community.

    The media file is in JSON format and contains a dictionary with an exchange
    reaction ID as the key and lower and upper bounds of the exchange reaction
    as the value. For example,

    {'EX_h2o': [0.0, 1000.0],
     'EX_h2s': [-1.0, 1000.0],
     'EX_pi': [-10.0, 1000.0],
     ...
    }

    Parameters
    ----------
    pair_models : list of str
        List of path names to two species community model files
    media_filename : str
        Path to file with exchange reaction bounds for media
    n_processes: int, optional
        Number of processes in job pool

    Returns
    -------
    pandas.DataFrame
        Results of growth rate calculations
    """

    if n_processes is None:
        n_processes = min(cpu_count(), 4)
    pool = Pool(n_processes)
    result_list = [pool.apply_async(compute_growth_rates, (pair_filename, media_filename))
                   for pair_filename in pair_models]
    growth_rates = DataFrame(columns=growth_rate_columns)
    for result in result_list:
        growth_rates = growth_rates.append(result.get(), ignore_index=True)
    return growth_rates
