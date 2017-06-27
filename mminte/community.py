import re
import six
from warnings import warn
from os.path import splitext
from pkg_resources import parse_version

from cobra.io import load_matlab_model, load_json_model, read_sbml_model
from cobra.io import save_matlab_model, save_json_model, write_sbml_model
from cobra.core import Model
from cobra import __version__ as cobra_version

# Can we use new features in cobra 0.6?
cobra06 = parse_version(cobra_version) >= parse_version('0.6.0')
if cobra06:
    from cobra.util.solver import linear_reaction_coefficients
    from cobra.util.solver import set_objective


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
    cobra.core.Model
        Model object loaded from file

    Raises
    ------
    IOError
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


def save_model_to_file(model, filename):
    """ Save a model to a file based on the extension of the file name.

    Parameters
    ----------
    model : cobra.core.Model
        Model object loaded from file
    filename : str
        Path to model file

    Raises
    ------
    IOError
        If model file extension is not supported.
    """

    (root, ext) = splitext(filename)
    if ext == '.mat':
        save_matlab_model(model, filename)
    elif ext == '.xml' or ext == '.sbml':
        write_sbml_model(model, filename)
    elif ext == '.json':
        save_json_model(model, filename)
    else:
        raise IOError('Model file extension not supported for {0}'.format(filename))
    return


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

    # Make a copy of the reaction. Since exchange reactions are shared by all species in the
    # community model, set the lower and upper bounds to default values.
    copy_reaction = reaction.copy()
    copy_reaction.bounds = (-1000., 1000)

    # Confirm reaction has only one metabolite and metabolite coefficient is negative.
    reaction_metabolites = copy_reaction.metabolites
    if len(reaction_metabolites) > 1:
        warn('Model {0} exchange reaction {1} has {2} metabolites (expected one metabolite)'
             .format(reaction.model.id, reaction.id, len(reaction_metabolites)))
    metabolite = six.next(six.iterkeys(reaction_metabolites))
    if reaction_metabolites[metabolite] >= 0:
        warn('Model {0} exchange reaction {1} metabolite {2} has positive coefficient (expected negative)'
             .format(reaction.model.id, reaction.id, metabolite.id))

    # Put the metabolite in the community compartment.
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
    cobra.core.Model
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

        # Check for multiple objectives in the model (which changed significantly in cobra 0.6).
        if cobra06:
            linear_coefficients = linear_reaction_coefficients(model)
            if len(linear_coefficients) != 1:
                raise Exception('Wrong number of objectives for model {0}, only one growth objective is allowed'
                                .format(model_filename))
            objective_id = '{0}_{1}'.format(model.id, six.next(six.iterkeys(linear_coefficients)).id)
            objective_value = six.next(six.itervalues(linear_coefficients))
        else:
            if len(model.objective) != 1:
                raise Exception('Wrong number of objectives for model {0}, only one growth objective is allowed'
                                .format(model_filename))
            objective_id = '{0}_{1}'.format(model.id, six.next(six.iterkeys(model.objective)).id)
            objective_value = six.next(six.itervalues(model.objective))

        # All metabolites need to have a compartment suffix.
        for metabolite in model.metabolites:
            metabolite.notes['type'] = _id_type(metabolite.id)
        unknown = model.metabolites.query(lambda x: 'unknown' in x['type'], 'notes')
        if len(unknown) > 0:
            raise Exception('Unknown compartment suffixes found in metabolites for {0}'.format(model_filename))

        # Get the exchange reactions from the species model.
        exchange_reactions = model.reactions.query(lambda x: x.startswith('EX_'), 'id')

        # Add any exchange reactions that are not already in the community model.
        for reaction in exchange_reactions:
            if reaction.id not in exchange_reaction_ids:
                exchange_reaction_ids.add(reaction.id)
                if cobra06:
                    metabolite = six.next(six.iterkeys(reaction.metabolites)).copy()
                    metabolite.compartment = community_compartment
                    metabolite.id = _change_compartment(metabolite.id, community_compartment, metabolite.notes['type'])
                    rxn = community.add_boundary(metabolite)  # This is slow on cobra06
                    rxn.id = reaction.id  # Keep same ID as species model
                else:
                    community.add_reactions([copy_exchange_reaction(reaction)])

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
                reaction.bounds = (-1000., 1000.)
            else:
                reaction.id = '{0}_{1}'.format(model.id, reaction.id)

        # Update the metabolite IDs with species prefix.
        for metabolite in model.metabolites:
            if metabolite.compartment != community_compartment:
                metabolite.id = '{0}_{1}'.format(model.id, metabolite.id)

        # Add the species model to the community model.
        community += model
        if cobra06:
            # Workaround until agreement reached on issue #505.
            objective_reaction = community.reactions.get_by_id(objective_id)
            set_objective(community, {objective_reaction: objective_value}, additive=True)
        species = {
            'id': model.id,
            'objective': objective_id,
            'filename': model_filename
        }
        community.notes['species'].append(species)

    # Update the community ID to include all of the species in the community.
    # Note that the community ID is used as the file name when saving the
    # community model to a JSON file.
    community.id = 'x'.join(model_ids)
    return community


def single_species_knockout(community, species_id):
    """ Knockout a species from a community model.

    Parameters
    ----------
    community : cobra.core.Model
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
    species_index = -1
    for index in range(len(community.notes['species'])):
        if community.notes['species'][index]['id'] == species_id:
            species_index = index
    if species_index < 0:
        raise Exception('Species {0} is not a member of the community'.format(species_id))

    if cobra06:
        with community:
            # Knock out all of the reactions for the specified species.
            species_reactions = community.reactions.query(lambda r: r.startswith(species_id), 'id')
            for reaction in species_reactions:
                reaction.knock_out()

            # Remove the species objective from the community model objective.
            species_objective = community.reactions.get_by_id(community.notes['species'][species_index]['objective'])
            linear_coefficients = linear_reaction_coefficients(community)
            del linear_coefficients[species_objective]
            set_objective(community, linear_coefficients)

            # Optimize the community model with the specified species knocked out.
            solution = community.optimize()

    else:
        # Knock out all of the reactions for the specified species.
        species_reactions = community.reactions.query(lambda r: r.startswith(species_id), 'id')
        saved_bounds = dict()
        for reaction in species_reactions:
            saved_bounds[reaction.id] = reaction.bounds
            reaction.knock_out()

        # Remove the species objective from the community model objective.
        species_objectives = dict()
        for reaction in community.objective:
            if reaction.id.startswith(species_id):
                species_objectives[reaction] = reaction.objective_coefficient
                reaction.objective_coefficient = 0.

        # Optimize the community model with the specified species knocked out.
        solution = community.optimize()

        # Restore all species reactions to original values.
        for reaction in species_reactions:
            reaction.bounds = saved_bounds[reaction.id]
        for reaction in species_objectives:
            reaction.objective_coefficient = species_objectives[reaction]

    return solution
