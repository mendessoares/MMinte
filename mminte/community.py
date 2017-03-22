import re
import json
import six
from warnings import warn
from os.path import splitext

from cobra.io import load_matlab_model, load_json_model, read_sbml_model
from cobra.core import Model, Reaction, Solution

# Regular expression for compartment suffix on ModelSEED IDs
modelseed_suffix_re = re.compile(r'_([ce])$')

# Regular expression for compartment suffix on BiGG IDs
bigg_suffix_re = re.compile(r'\[([cepu])\]$')

# ID of community compartment for metabolite exchange
community_compartment = 'u'


def _id_type(object_id):
    """ Figure out the ID type for an object ID.

    Parameters
    ----------
    object_id : str

    Returns
    -------
    str
        ID type ('bigg', 'modelseed', or 'unknown')
    """

    if re.search(bigg_suffix_re, object_id) is not None:
        return 'bigg'
    if re.search(modelseed_suffix_re, object_id) is not None:
        return 'modelseed'
    return 'unknown'


def _strip_compartment(string, id_type):
    """ Strip the compartment suffix from a string.

    Parameters
    ----------
    string : str
        String to strip compartment suffix from
    id_type : {'bigg', 'modelseed'}
        Type of ID string

    Returns
    -------
    str
        Changed string
    """

    if id_type == 'bigg':
        return re.sub(bigg_suffix_re, '', string)
    if id_type == 'modelseed':
        return re.sub(modelseed_suffix_re, '', string)
    return string


def _change_compartment(id_str, compartment, id_type):
    """ Change the compartment suffix in an ID string.

    Parameters
    ----------
    id_str : str
        ID string to be changed
    compartment : str
        ID of new compartment (usually a single character)
    id_type : {'bigg', 'modelseed'}
        Type of ID string

    Returns
    -------
    str
        Changed ID string
    """

    if id_type == 'bigg':
        return re.sub(bigg_suffix_re, '[{0}]'.format(compartment), id_str)
    elif id_type == 'modelseed':
        return re.sub(modelseed_suffix_re, '_{0}'.format(compartment), id_str)
    return '{0}_{1}'.format(id_str, compartment)


def load_model_from_file(filename):
    """ Load a model from a file based on the extension of the file name.

    Parameters
    ----------
    filename : str
        Path to model file

    Returns
    -------
    cobra.Model
        Model object loaded from file

    Raises
    ------
    Exception
        If model file extension is not supported.
    """

    (root, ext) = splitext(filename)
    if ext == '.mat':
        model = load_matlab_model(filename)
    elif ext == '.xml' or ext == '.sbml':
        model = read_sbml_model(filename)
    elif ext == '.json':
        model = load_json_model(filename)
    else:
        raise IOError('Model file extension not supported for {0}'.format(filename))

    return model


def copy_exchange_reaction(reaction):
    """ Make a copy of an exchange reaction for the community model from an exchange reaction in a source model.

    Parameters
    ----------
    reaction : cobra.Reaction
        Source exchange reaction

    Returns
    -------
    cobra.Reaction
        Exchange reaction for community model
    """

    # Confirm reaction has only one metabolite and metabolite coefficient is negative.
    if len(reaction.metabolites) > 1:
        warn('Model {0} exchange reaction {1} has {2} metabolites (expected one metabolite)'
             .format(reaction.model.id, reaction.id, len(reaction.metabolites)))
    for metabolite in reaction.metabolites:
        if reaction.metabolites[metabolite] >= 0:
            warn('Model {0} exchange reaction {1} metabolite {2} has positive coefficient (expected negative)'
                 .format(reaction.model.id, reaction.id, metabolite.id))

    # Make a copy of the reaction. Since exchange reactions are shared by all species in the
    # community model, set the lower and upper bounds to default values.
    copy_reaction = reaction.copy()
    copy_reaction.lower_bound = -1000.
    copy_reaction.upper_bound = 1000.
    copy_reaction.objective_coefficient = 0.

    # Put the metabolite in the community compartment.
    metabolite = six.next(six.iterkeys(copy_reaction.metabolites))
    metabolite.compartment = community_compartment
    metabolite.id = _change_compartment(metabolite.id, community_compartment, metabolite.notes['type'])

    return copy_reaction


def create_community_model(source_models):
    """ Create a community model from a list of source models.

    A community model contains all of the reactions and metabolites from the
    source models. As a source model for a species is added to the community
    model, a model ID prefix is added to the IDs of reactions and metabolites.
    This is the same as assigning each species to a different compartment,
    which is required because cells are closed compartments that do not share
    metabolites. A shared compartment is added to the community model and all
    unique exchange reactions from the source models are added to the community
    model to exchange metabolites between the shared compartment and the system
    boundary. For each source model, all exchange reactions are converted to
    transport reactions to move the metabolite between the shared compartment
    and the extracellular compartment of the source model.

    Parameters
    ----------
    source_models : list of str
        List of path names to model files

    Returns
    -------
    cobra.Model
        Community model

    Raises
    ------
    Exception
        If there are less than two models in the list of source models.
        If there is a duplicate model ID in the list of source models.
        If there is more than one objective
        If the type of IDs in the model metabolites could not be determined.
    """

    # There must be at least two source models to make a community model.
    if len(source_models) < 2:
        raise Exception('There must be at least two species in a community model')

    # Start with an empty model.
    community = Model('Community')
    community.compartments['u'] = 'Lumen'

    # Keep track of the source models. Each element is a tuple with ID and source file name.
    community.notes['species'] = list()

    # IDs of all exchange reactions in the community.
    exchange_reaction_ids = set()

    # IDs of all models in the community (duplicates are not allowed).
    model_ids = set()

    # Add of the source models to the community model.
    for model_filename in source_models:
        # Load the model from a file.
        model = load_model_from_file(model_filename)

        # Since the model ID is used as a prefix for reactions and metabolites it must be unique.
        if model.id in model_ids:
            raise Exception('Model ID {0} from {1} is a duplicate in the community'
                            .format(model.id, model_filename))
        model_ids.add(model.id)

        # Check for multiple objectives in the model.
        if len(model.objective) > 1:
            raise Exception('More than one objective for model {0}, only one growth objective is allowed'
                            .format(model_filename))

        # All metabolites need to have a compartment suffix.
        for metabolite in model.metabolites:
            metabolite.notes['type'] = _id_type(metabolite.id)
        unknown = model.metabolites.query(lambda x: 'unknown' in x['type'], 'notes')
        if len(unknown) > 0:
            raise Exception('Unknown compartment suffixes found in metabolites for {0}'.format(model_filename))

        # Get the exchange reactions from the species model.
        exchange_reactions = model.reactions.query(lambda x: x.startswith('EX_'))

        # Add any exchange reactions that are not already in the community model.
        for reaction in exchange_reactions:
            if reaction.id not in exchange_reaction_ids:
                exchange_reaction_ids.add(reaction.id)
                community.add_reaction(copy_exchange_reaction(reaction))

        # Update the reaction IDs with species prefix and convert exchange reactions to transport reactions.
        for reaction in model.reactions:
            # Change the exchange reactions to transport reactions to move the metabolite between the
            # community compartment and the extracellular compartment of this organism.
            if reaction in exchange_reactions:
                e_metabolite = six.next(six.iterkeys(reaction.metabolites))
                u_metabolite = community.metabolites.get_by_id(
                    _change_compartment(e_metabolite.id, community_compartment, e_metabolite.notes['type']))
                reaction.add_metabolites({u_metabolite: 1.})
                reaction.id = '{0}_TR_{1}'.format(model.id, reaction.id[3:])  # Strip "EX_" prefix
                reaction.lower_bound = -1000.
                reaction.upper_bound = 1000.
            else:
                reaction.id = '{0}_{1}'.format(model.id, reaction.id)

        # Update the metabolite IDs with species prefix.
        for metabolite in model.metabolites:
            if metabolite.compartment != community_compartment:
                metabolite.id = '{0}_{1}'.format(model.id, metabolite.id)

        # Add the species model to the community model.
        community += model
        species = {
            'id': model.id,
            'objective': six.next(six.iterkeys(model.objective)).id,
            'filename': model_filename
        }
        community.notes['species'].append(species)

    # Update the community ID to include all of the species in the community.
    # @todo Could the ID get too long for a large community?
    community.id = 'x'.join(model_ids)
    return community


def single_species_knockout(model, species_id):
    """ Knockout a species from a community model.

    Parameters
    ----------
    model : cobra.Model
        Community model
    species_id : str
        ID of species to knockout from community model

    Returns
    -------
    cobra.Solution
        Solution after optimizing model with species knocked out

    Raises
    ------
    Exception
        If specified species is not a member of the community.
    """

    # Make sure the species is in the community model.
    species_id_list = [x['id'] for x in model.notes['species']]
    if species_id not in species_id_list:
        raise Exception('Species {0} is not a member of the community'.format(species_id))

    # Set lower and upper bound of all species reactions to zero.
    species_reactions = model.reactions.query(lambda r: r.startswith(species_id))
    saved_bounds = dict()
    for reaction in species_reactions:
        saved_bounds[reaction.id] = reaction.bounds
        reaction.knock_out()

    # Knockout the species objective reactions.
    species_objectives = dict()
    for reaction in model.objective:
        if reaction.id.startswith(species_id):
            species_objectives[reaction] = reaction.objective_coefficient
            reaction.objective_coefficient = 0.

    # Optimize the community model.
    solution = model.optimize()

    # Restore all species reactions to original values.
    for reaction in species_reactions:
        reaction.bounds = saved_bounds[reaction.id]
    for reaction in species_objectives:
        reaction.objective_coefficient = species_objectives[reaction]

    return solution
