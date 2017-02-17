from cobra.io import save_json_model
import json
from pandas import Series

from .community import create_community_model, load_model_from_file, single_species_knockout

# Column names for reporting growth rate results.
growth_rate_columns = ['A_ID', 'B_ID', 'TYPE', 'TOGETHER', 'A_TOGETHER', 'B_TOGETHER',
                       'A_ALONE', 'B_ALONE', 'A_CHANGE', 'B_CHANGE']


def create_pair_model(pair, output_folder):
    """ Create a two species community model.

    Parameters
    ----------
    pair : list of str
        Each element is a path to a single species model file
    output_folder : str
        Path to output folder where community model JSON file is saved

    Returns
    -------
    str
        Path to two species community model file
    """

    community = create_community_model(pair)
    community_filename = '{0}/{1}.json'.format(output_folder, community.id)
    save_json_model(community, community_filename)
    return community_filename


def compute_growth_rates(pair_filename, media_filename):
    """ Compute growth rates for a two species community model.

    Parameters
    ----------
    pair_filename : str
        Path to two species community model file
    media_filename : str
        Path to file with exchange reaction bounds for media

    Returns
    -------
    pandas.Series
        Growth rate details for interaction between two species in pair
    """

    # Load the model and apply the media to it.
    pair_model = load_model_from_file(pair_filename)
    apply_media(pair_model, media_filename)

    # Optimize the model with two species together, one species knocked out, and
    # other species knocked out.
    t_solution = pair_model.optimize()
    a_id = pair_model.notes['species'][0]['id']
    b_id = pair_model.notes['species'][1]['id']
    a_solution = single_species_knockout(pair_model, b_id)
    b_solution = single_species_knockout(pair_model, a_id)

    # Evaluate the interaction between the two species.
    a_objective = pair_model.notes['species'][0]['objective']
    b_objective = pair_model.notes['species'][1]['objective']
    a_percent_change, b_percent_change, interaction_type = \
        evaluate_interaction(t_solution.x_dict[a_objective], t_solution.x_dict[b_objective],
                             a_solution.x_dict[a_objective], b_solution.x_dict[b_objective])
    return Series([a_id, b_id, interaction_type, t_solution.f, t_solution.x_dict[a_objective],
                   t_solution.x_dict[b_objective], a_solution.x_dict[a_objective],
                   b_solution.x_dict[b_objective], a_percent_change, b_percent_change],
                   index=growth_rate_columns)


def apply_media(model, media_filename):
    """ Apply a media to a model to set the metabolites that can be consumed.

    Parameters
    ----------
    model : cobra.Model
        Model to apply media to
    media_filename : str
        Path to file with exchange reaction bounds for media
    """

    # Load the media from the file.
    media = json.load(open(media_filename))

    # Get the list of exchange reactions. Only allow exchange reactions in the media.
    exchange_reactions = model.reactions.query(lambda x: x.startswith('EX_'))

    # Update the bounds for exchange reactions based on the values in the media.
    for reaction in exchange_reactions:
        if reaction.id in media:
            reaction.bounds = media[reaction.id]
        else:
            reaction.lower_bound = 0.

    return


def evaluate_interaction(a_together, b_together, a_alone, b_alone):
    """ Evaluate interaction between two species.

    Parameters
    ----------
    a_together : float
        Objective flux of first species when grown together with second species
    b_together : float
        Objective flux of second species when grown together with first species
    a_alone : float
        Objective flux of first species when grown alone
    b_alone : float
        Objective flux of second species when grown alone

    Returns
    -------
    a_percent_change : float
        Percent change in growth rate in presence of second species
    b_percent_change : float
        Percent change in growth rate in presence of first species
    interaction_type : {'Mutualism', 'Parasitism', 'Commensalism', 'Competition', 'Amensalism', 'Neutralism', 'Empty'}
        Type of interaction between the two species
    """

    # Calculate the effect of the presence of species B on the growth rate of species A.
    if a_alone == 0.:
        a_alone = float(1e-25)
    a_percent_change = (a_together - a_alone) / a_alone

    # Calculate the effect of the presence of species A on the growth rate of species B.
    if b_alone == 0.:
        b_alone = float(1e-25)
    b_percent_change = (b_together - b_alone) / b_alone

    # Set the interaction type based on the percent change values.
    if a_percent_change > 0.1 and b_percent_change > 0.1:
        interaction_type = 'Mutualism'

    elif a_percent_change > 0.1 and b_percent_change < -0.1:
        interaction_type = 'Parasitism'

    elif a_percent_change > 0.1 and b_percent_change > -0.1 and b_percent_change < 0.1:
        interaction_type = 'Commensalism'

    elif a_percent_change < -0.1 and b_percent_change > 0.1:
        interaction_type = 'Parasitism'

    elif a_percent_change < -0.1 and b_percent_change < -0.1:
        interaction_type = 'Competition'

    elif a_percent_change < -0.1 and b_percent_change > -0.1 and b_percent_change < 0.1:
        interaction_type = 'Amensalism'

    elif a_percent_change > -0.1 and a_percent_change < 0.1 and b_percent_change > 0.1:
        interaction_type = 'Commensalism'

    elif a_percent_change > -0.1 and a_percent_change < 0.1 and b_percent_change < -0.1:
        interaction_type = 'Amensalism'

    elif a_percent_change > -0.1 and a_percent_change < 0.1 and b_percent_change > -0.1 and b_percent_change < 0.1:
        interaction_type = 'Neutralism'

    else:
        interaction_type = 'Empty'

    return a_percent_change, b_percent_change, interaction_type
