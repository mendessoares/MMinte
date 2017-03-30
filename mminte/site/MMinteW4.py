from pkg_resources import resource_filename
from os import makedirs
from os.path import join, exists
import cherrypy

from mminte import create_interaction_models, get_all_pairs
from mminte.site import MMinteApp


class Widget4(MMinteApp):
    """ Widget 4 application for spyre """
    title = 'Widget 4'

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": 'analysis_folder',
             "label": "In this widget we are going  we're going to create two-species community metabolic models "
                      "from single species metabolic models. You can specify the species pairs using (1) a file "
                      "with a list of single species model file names to select all possible pairs, (2) a file "
                      "with a list of pairs of single species file names to select specific pairs, or (3) the "
                      "correlations file from Widget 1 and the similarity file from Widget 2 to select a subset "
                      "of pairs.<br><br>Enter the location of the folder for storing the files for this analysis",
             "value": self.getRoot().analysisFolder()},

            {"type": "dropdown",
             "key": "pair_input_type",
             "label": "How do you want to specify the single species model file names of the pairs?",
             "options": [{"label": "All pairs", "value": "all"},
                         {"label": "Specific pairs", "value": "specific"},
                         {"label": "Subset pairs", "value": "subset"}],
             "value": 'All pairs'},

            {"type": "text",
             "key": "single_models_file",
             "label": 'If you selected "All pairs", enter the name of the file with the list of single '
                      'species model file names',
             "value": "single_model_filenames.txt"},

            {"type": "text",
             "key": "pair_list_file",
             "label": 'If you selcted "Specific pairs", enter the name of the file with the list of pairs of '
                      'single species models',
             "value": "pair_list.txt"},

            {"type": "text",
             "key": "correlation_file",
             "label": 'If you selected "Subset pairs", enter the name of the file with the information about the '
                      'correlations between associated OTUs',
             "value": resource_filename('mminte', "test/data/correlation.txt")},

            {"type": "text",
             "key": "similarity_file",
             "label": 'If you selected "Subset pairs", enter the name of the file with percent similarity information',
             "value": "similarity.txt"},

            {"type": "text",
             "key": "model_folder",
             "label": 'If you selected "Subset pairs", enter the name of the folder with single species model files',
             "value": "single_models"},

            {"type": "text",
             "key": 'community_folder',
             "label": "Enter the name of the folder for storing the two species community model files",
             "value": "pair_models"},

            {"type": "text",
             "key": 'pair_models_file',
             "label": "Enter the name of the file for storing the list of two species model file names",
             "value": "pair_model_filenames.txt"},
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Widget 4",
             "id": "run_widget"}
        ]

        self.outputs = [
            {"type": "html",
             "id": "results",
             "control_id": "run_widget",
             "tab": "Results",
             "on_page_load": False}
        ]

        self.tabs = ["Results"]
    
    def getHTML(self, params):
        """ Run Widget 4 and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget 4 input parameters: {0}'.format(params))
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget 4: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br>Exception: {1}'.format(params['analysis_folder'], e)
        if params['pair_input_type'] == 'all':
            model_list_file = join(params['analysis_folder'], params['single_models_file'])
            if not exists(model_list_file):
                cherrypy.log('Widget 4: Model list file "{0}" was not found'.format(model_list_file))
                return 'Sorry, model list file "{0}" was not found. Make sure the path to the file is correct.' \
                       .format(model_list_file)
            with open(model_list_file, 'r') as handle:
                source_models = [line.strip() for line in handle]
            pairs = get_all_pairs(source_models)
            cherrypy.log('Widget 4: Generated {0} pairs from {1} source models'.format(len(pairs), len(source_models)))
        elif params['pair_input_type'] == 'specific':
            pair_list_file = join(params['analysis_folder'], params['pair_list_file'])
            if not exists(pair_list_file):
                cherrypy.log('Widget 4: Pair list file "{0}" was not found'.format(pair_list_file))
                return 'Sorry, pair list file "{0}" was not found. Make sure the path to the file is correct.' \
                       .format(pair_list_file)
            with open(pair_list_file, 'r') as handle:
                pair_list = [line.strip().split('\t') for line in handle]
            for index in range(len(pair_list)):
                fields = pair_list[index]
                if len(fields) != 2:
                    return 'Line {0} in "{1}" file must have two columns separated by tab' \
                           .format(index, params['pair_list_file'])
            pairs = [(fields[0], fields[1]) for fields in pair_list]
            cherrypy.log('Widget 4: Found {0} pairs in pair list file'.format(len(pairs)))
        else:
            # Need to move over code from subset pairs. Still not convinced that it is different than going
            # through the standard workflow.
            with open(join(params['analysis_folder'], params['similarity_file']), 'r') as handle:
                similarity = [line.strip().split() for line in handle]
            with open(params['correlation_file'], 'r') as handle:
                correlation = [line.strip().split() for line in handle]

            source_models = list()
            for c in correlation:
                for s in similarity:
                    if c[0] == s[0] or c[1] == s[0]:
                        source_models.append(join(params['analysis_folder'], params['model_folder'],
                                                  '{0}.json'.format(s[1])))
            source_models = list(set(source_models))
            pairs = get_all_pairs(source_models)
        community_folder = join(params['analysis_folder'], params['community_folder'])
        if not exists(community_folder):
            try:
                makedirs(community_folder)
            except Exception as e:
                cherrypy.log('Widget 4: We were unable to create folder "{0}" for community model files'
                             .format(community_folder))
                return 'Sorry something went wrong creating the folder "{0}" for the community model files. ' \
                       'Make sure the path to the folder is correct.<br>Exception: {1}' \
                       .format(community_folder, e)

        # Create two species community models.
        try:
            cherrypy.log('Widget 4: Started creating community models from {0} pairs of single species models'
                         .format(len(pairs)))
            model_filenames = create_interaction_models(pairs, output_folder=community_folder)
            cherrypy.log("Widget 4: Finished creating {0} community models".format(len(model_filenames)))
            output_filename = join(params['analysis_folder'], params['pair_models_file'])
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(model_filenames))
        except Exception as e:
            cherrypy.log("Widget 4: Error creating community models: {0}".format(e))
            return "Sorry something's wrong. Make sure the path to your file is correct and " \
                   "that the Python package cobrapy is loaded into your system.<br>Exception: {0}".format(e)

        # Generate the output for the Results tab.
        return 'We created {0} two species community models. In the next widget, we will use them ' \
               'to predict the growth rate of their species in isolation and when in the community ' \
               'using COBRA tools. A list of the community model file names was stored in the ' \
               '"{1}" file.'.format(len(model_filenames), output_filename)


if __name__ == '__main__':
    app = Widget4()
    app.launch()
