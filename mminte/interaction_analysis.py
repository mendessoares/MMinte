from itertools import combinations
from os.path import join, exists
import pandas as pd
from multiprocessing import Pool, cpu_count
from warnings import warn
from cobra.io import load_json_model, save_json_model
from mackinac import get_modelseed_model_stats, reconstruct_modelseed_model, gapfill_modelseed_model, \
    create_cobra_model_from_modelseed_model, delete_modelseed_model
from mackinac.SeedClient import ObjectNotFoundError

from .interaction_worker import growth_rate_columns, create_pair_model, compute_growth_rates


def get_all_pairs(source_models):
    """ Get all of the unique pairs from a list of models.

    Parameters
    ----------
    source_models : list of str
        List of path names to model files

    Returns
    -------
    list of tuple
        List of tuples where each tuple has two elements, path to first model file in pair and
        path to second model file in pair
    """

    return [pair for pair in combinations(source_models, 2)]


def create_species_models(genome_ids, output_folder, replace=False, optimize=False):
    """ Create ModelSEED models from a list of PATRIC genome IDs.

    The ModelSEED server can be overwhelmed by too many requests so reconstructing
    models is single-threaded (and got weird errors trying to use multiprocessing).

    Parameters
    ----------
    genome_ids : list of str
        List of PATRIC genome IDs
    output_folder: str
        Path to folder where single species models are stored
    replace : bool, optional
        When True, always reconstruct model using ModelSEED service and replace local model
    optimize : bool, optional
        When True, optimize the model and check for growth

    Returns
    -------
    list of str
        List of paths to single species model files
    """

    # Get a model for each genome in the list.
    output_models = list()
    for genome_id in genome_ids:
        # If possible, use the model that was previously obtained from ModelSEED.
        model_filename = join(output_folder, '{0}.json'.format(genome_id))
        if exists(model_filename) and not replace:
            output_models.append(model_filename)
        else:
            reconstruct = False
            try:
                get_modelseed_model_stats(genome_id)
                if replace:
                    delete_modelseed_model(genome_id)
                    reconstruct = True
            except ObjectNotFoundError:
                reconstruct = True

            # If needed, reconstruct and gap fill a model from the genome.
            if reconstruct:
                reconstruct_modelseed_model(genome_id)
                gapfill_modelseed_model(genome_id)

            # Create a COBRA model and save in JSON format.
            model = create_cobra_model_from_modelseed_model(genome_id)
            save_json_model(model, model_filename)
            output_models.append(model_filename)

    # If requested, verify ModelSEED models produce growth.
    if optimize:
        for model_filename in output_models:
            model = load_json_model(model_filename)
            solution = model.optimize()
            if solution.f <= 0.0001:
                warn('Model {0} does not produce growth'.format(model.id))
    return output_models


def create_interaction_models(source_models, output_folder, n_processes=None):
    """ Create two species community models for all pairs in a community.

    Parameters
    ----------
    source_models : list of tuple
        List of tuples where each tuple has two elements, path to first model file in pair and
        path to second model file in pair
    output_folder : str
        Path to folder where output community model files are saved
    n_processes : int, optional
        Number of processes in job pool

    Returns
    -------
    list of str
        List of path names to two species community model files
    """

    # Make sure the input list of models has exactly two elements in each tuple.
    for index in range(len(source_models)):
        if len(source_models[index]) != 2:
            raise ValueError('There must be exactly two models at index {0} in the list of source models'
                             .format(index))

    if n_processes is None:
        n_processes = min(cpu_count(), 4)
    pool = Pool(n_processes)
    result_list = [pool.apply_async(create_pair_model, (pair, output_folder))
                   for pair in source_models]
    output_models = [result.get() for result in result_list]
    pool.close()
    return output_models


def calculate_growth_rates(pair_models, medium, n_processes=None):
    """ Calculate growth rates for all pairs in community.

    The medium is a dictionary with an exchange reaction ID as the key and the
    absolute value of bound in direction of metabolite creation as the value
    (i.e. lower bound for `met <--` or upper bound for `met -->`). For example,

    {'EX_h2o': 0.0,
     'EX_h2s': 1.0,
     'EX_pi': 10.0
     ...
    }

    Parameters
    ----------
    pair_models : list of str
        List of path names to two species community model files
    medium : dict
        Dictionary with exchange reaction ID as key and bound as value
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
    result_list = [pool.apply_async(compute_growth_rates, (pair_filename, medium))
                   for pair_filename in pair_models]
    growth_rates = pd.DataFrame(columns=growth_rate_columns)
    for result in result_list:
        growth_rates = growth_rates.append(result.get(), ignore_index=True)
    pool.close()
    return growth_rates


def read_diet_file(diet_filename):
    """ Read a diet file and convert to medium dictionary.

    Each line of the diet file has three fields: (1) exchange reaction ID, (2) reaction name,
    and (3) absolute value of bound in direction of metabolite creation (i.e. lower bound
    for `met <--` or upper bound for `met -->`). The first line of the file is a header that
    is ignored and the reaction name field is not used. Fields are separated by tabs.

    Parameters
    ----------
    diet_filename : str
        Path to file with nutrient conditions for a diet

    Returns
    -------
    dict
        Dictionary with reaction ID as key and bound as value
    """

    medium = dict()
    with open(diet_filename, 'rU') as handle:
        handle.readline()
        line_num = 1
        for line in handle:
            line_num += 1
            fields = line.strip().split('\t')
            if len(fields) != 3:
                raise ValueError('Line {0} in file "{1}" must have three fields'
                                 .format(line_num, diet_filename))
            medium[fields[0]] = abs(float(fields[2]))
    return medium


def read_growth_rates_file(growth_rates_filename):
    """ Read a file with the saved growth rates data frame.

    Parameters
    ----------
    growth_rates_filename : str
        Path to file with growth rates data frame in CSV format

    Returns
    -------
    pandas.DataFrame
        Growth rates information
    """

    return pd.read_csv(growth_rates_filename, dtype={'A_ID': str, 'B_ID': str})


def write_growth_rates_file(growth_rates, growth_rates_filename):
    """ Write a growth rates data frame to a file.

    Parameters
    ----------
    growth_rates : pandas.DataFrame
        Growth rates information
    growth_rates_filename : str
        Path to file for storing growth rates data frame in CSV format
    """

    growth_rates.to_csv(growth_rates_filename, index=False)
    return
