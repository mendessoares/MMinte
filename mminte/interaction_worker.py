from cobra.io import save_json_model
from pandas import Series
from six import iteritems

from .community import create_community_model, load_model_from_file, single_species_knockout

# Column names for data frame reporting growth rate results.
growth_rate_columns = ['A_ID', 'B_ID', 'TYPE', 'TOGETHER', 'A_TOGETHER', 'B_TOGETHER',
                       'A_ALONE', 'B_ALONE', 'A_CHANGE', 'B_CHANGE']

# Cutoff for rounding growth rate to zero.
growth_rate_cutoff = 1e-12


def create_pair_model(pair, output_folder):
    """ Create a two species community model.

    Parameters
    ----------
    pair : tuple
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


def compute_growth_rates(pair_filename, medium):
    """ Compute growth rates for a two species community model.

    Parameters
    ----------
    pair_filename : str
        Path to two species community model file
    medium : dict
        Dictionary with exchange reaction ID as key and bound as value

    Returns
    -------
    pandas.Series
        Growth rate details for interaction between two species in pair
    """

    # Load the model and apply the medium to it.
    pair_model = load_model_from_file(pair_filename)
    apply_medium(pair_model, medium)

    # Optimize the model with two species together, one species knocked out, and
    # other species knocked out.
    a_id = pair_model.notes['species'][0]['id']
    a_objective = pair_model.notes['species'][0]['objective']
    b_id = pair_model.notes['species'][1]['id']
    b_objective = pair_model.notes['species'][1]['objective']

    t_solution = pair_model.optimize()
    a_solution = single_species_knockout(pair_model, b_id)
    b_solution = single_species_knockout(pair_model, a_id)

    # Round very small growth rates to zero.
    if t_solution.x_dict[a_objective] < growth_rate_cutoff:
        t_solution.x_dict[a_objective] = 0.
    if t_solution.x_dict[b_objective] < growth_rate_cutoff:
        t_solution.x_dict[b_objective] = 0.
    if a_solution.x_dict[a_objective] < growth_rate_cutoff:
        a_solution.x_dict[a_objective] = 0.
    if b_solution.x_dict[b_objective] < growth_rate_cutoff:
        b_solution.x_dict[b_objective] = 0.

    # Evaluate the interaction between the two species.
    if t_solution.status == 'optimal' and a_solution.status == 'optimal' and b_solution.status == 'optimal':
        a_percent_change, b_percent_change, interaction_type = \
            evaluate_interaction(t_solution.x_dict[a_objective], t_solution.x_dict[b_objective],
                                 a_solution.x_dict[a_objective], b_solution.x_dict[b_objective])
        details = Series([a_id, b_id, interaction_type, t_solution.f, t_solution.x_dict[a_objective],
                         t_solution.x_dict[b_objective], a_solution.x_dict[a_objective],
                         b_solution.x_dict[b_objective], a_percent_change, b_percent_change],
                         index=growth_rate_columns)
    else:
        details = Series([a_id, b_id, 'Empty', 0., 0., 0., 0., 0., 0., 0.], index=growth_rate_columns)
        if t_solution.status == 'optimal':
            details.set_value('TOGETHER', t_solution.f)
            details.set_value('A_TOGETHER', t_solution.x_dict[a_objective])
            details.set_value('B_TOGETHER', t_solution.x_dict[b_objective])
        if a_solution.status == 'optimal':
            details.set_value('A_ALONE', a_solution.x_dict[a_objective])
        if b_solution.status == 'optimal':
            details.set_value('B_ALONE', b_solution.x_dict[b_objective])

    return details


def apply_medium(model, medium):
    """ Apply a medium to a model to set the metabolites that can be consumed.

    This function is adapted from the cobra.core.Model.medium setter in cobra 0.6
    with two differences: (1) if a reaction is in the medium but not in the
    model, the reaction is ignored (2) when turning off reactions in the model
    and not in the medium, only exchange reactions with the prefix 'EX_' are 
    considered (instead of all boundary reactions).
    
    Parameters
    ----------
    model : cobra.core.Model
        Model to apply medium to
    medium : dict
        Dictionary with exchange reaction ID as key and bound as value
    """

    def set_active_bound(reaction, bound):
        if reaction.reactants:
            reaction.lower_bound = -bound
        elif reaction.products:
            reaction.upper_bound = bound

    # Set the given media bounds.
    medium_reactions = set()
    for reaction_id, bound in iteritems(medium):
        try:
            reaction = model.reactions.get_by_id(reaction_id)
            medium_reactions.add(reaction)
            set_active_bound(reaction, bound)
        except KeyError:
            pass

    # The boundary attribute of a cobra.core.Reaction also includes demand and
    # sink reactions that we don't want turned off.
    exchange_reactions = set(model.reactions.query(lambda x: x.startswith('EX_'), 'id'))

    # Turn off reactions not present in medium.
    for reaction in (exchange_reactions - medium_reactions):
        set_active_bound(reaction, 0)

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
        a_alone = growth_rate_cutoff
    a_percent_change = (a_together - a_alone) / a_alone

    # Calculate the effect of the presence of species A on the growth rate of species B.
    if b_alone == 0.:
        b_alone = growth_rate_cutoff
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
