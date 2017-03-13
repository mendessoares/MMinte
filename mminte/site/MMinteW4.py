from spyre import server
from pkg_resources import resource_filename
from os import makedirs
from os.path import join, exists
import cherrypy

from mminte import create_interaction_models, get_all_pairs
from .mminte_widget import css_filename


class Widget4(server.App):
    title = 'Widget 4'
    
    inputs = [
        {"type": "dropdown",
         "key": 'pair_input_type',
         "label": "In this widget we are going  we're going to create two-species community metabolic models "
                  "from single species metabolic models. You can specify the species pairs using (1) a file "
                  "with a list of single species model file names to select all possible pairs, (2) a file "
                  "with a list of pairs of single species file names to select specific pairs, or (3) the "
                  "correlations file from Widget 1 and the similarity file from Widget 2 to select a subset "
                  "of pairs. How do you want to specify the single species model file names of the pairs?",
         "options": [{"label": "All pairs", "value": "all"},
                     {"label": "Specific pairs", "value": "specific"},
                     {"label": "Subset pairs", "value": "subset"}],
         "value": 'All pairs'},

        {"type": "text",
         "key": "model_list_file",
         "label": 'If you selected "All pairs", enter the location of the file with the list of single species models',
         "value": "/home/me/my_analysis/models/single_model_filenames.txt"},

        {"type": "text",
         "key": "pair_list_file",
         "label": 'If you seelcted "Specific pairs", enter the location of the file with the list of pairs of '
                  'single species models',
         "value": "/home/me/my_analysis/models/pair_model_filenames.txt"},

        {"type": "text",
         "key": "correlation_file",
         "label": 'If you selected "Subset pairs", enter the location of the file with the information about the '
                  'correlations between associated OTUs',
         "value": "/home/me/my_analysis/correlations.txt"},

        {"type": "text",
         "key": "similarity_file",
         "label": 'If you selected "Subset pairs", enter the location of the file with percent similarity information',
         "value": "/home/me/my_analysis/similarity.txt"},

        {"type": "text",
         "key": 'community_folder',
         "label": "Enter the location of the folder where two-species community models will be stored",
         "value": "/home/me/my_analysis/community"},
    ]

    controls = [
        {"type": "button",
         "label": "Run Widget 4",
         "id": "run_widget"}
    ]

    outputs = [
        {"type": "html",
         "id": "results",
         "control_id": "run_widget",
         "tab": "Results",
         "on_page_load": False}
    ]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        with open(resource_filename(__name__, css_filename)) as style:
            return style.read()

    def getHTML(self, params):
        """ Run Widget 4 and generate HTML output for Results tab. """

        cherrypy.log('Widget 4 input parameters: {0}'.format(params))

        if params['pair_input_type'] == 'all':
            if not exists(params['model_list_file']):
                cherrypy.log('Widget 4: Model list file "{0}" was not found'.format(params['model_list_file']))
                return 'Sorry, model list file "{0}" was not found. Make sure the path to the file is correct.' \
                       .format(params['model_list_file'])
            with open(params['model_list_file'], 'r') as handle:
                source_models = [line.strip() for line in handle]
            pairs = get_all_pairs(source_models)
            cherrypy.log('Widget 4: Generated {0} pairs from {1} source models'.format(len(pairs), len(source_models)))
        elif params['pair_input_type'] == 'specific':
            if not exists(params['pair_list_file']):
                cherrypy.log('Widget 4: Pair list file "{0}" was not found'.format(params['pair_list_file']))
                return 'Sorry, pair list file "{0}" was not found. Make sure the path to the file is correct.' \
                       .format(params['pair_list_file'])
            with open(params['pair_list_file'], 'r') as handle:
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
            source_models = []
            with open(params['similarity_file'], 'r') as handle:
                similarity = [line.strip().split() for line in handle]
            with open(params['correlation_file'], 'r') as handle:
                correlation = [line.strip().split() for line in handle]

            tempTableA = []
            for i in correlation:
                for j in similarity:
                    if i[0] == j[1]:
                        new_line = i[0], i[1], j[2]
                        tempTableA.append(list(new_line))

            cherrypy.log('Finished creating the first temporary table.')

            tempTableB = []

            for i in tempTableA:
                for j in similarity:
                    if i[1] == j[1]:
                        new_line = i[2] + 'X' + j[2]
                        tempTableB.append(new_line)

            cherrypy.log('Finished creating the second temporary table.')

            tempTableC = list(set(tempTableB))

            cherrypy.log(
                'There are %d unique combinations of two species that will be used to create the community models.' % (
                len(tempTableC)))

            # pairsListFile = open('../tempFiles/pairsList.txt', 'w')
            #
            # print>> pairsListFile, 'speciesA', 'speciesB'
            #
            # for item in tempTableC:
            #     line = item.split('X')
            #     print>> pairsListFile, line[0], line[1]
            #
            # pairsListFile.close()

        try:
            if not exists(params['community_folder']):
                makedirs(params['community_folder'])
        except Exception as e:
            cherrypy.log('Widget 4: We were unable to create folder "{0}" for community model files'
                         .format(params['community_folder']))
            return 'Sorry something went wrong creating the folder "{0}" for the community model files. Make sure ' \
                   'the path to the folder is correct.<br>Exception: {1}'.format(params['community_folder'], e)

        try:
            cherrypy.log('Widget 4: Started created community models from {0} pairs of single species models'
                         .format(len(pairs)))
            model_filenames = create_interaction_models(pairs, output_folder=params['community_folder'])
            cherrypy.log("Widget 4: Finished creating {0} community models".format(len(model_filenames)))
            output_filename = join(params['community_folder'], 'pair_model_filenames.txt')
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(model_filenames))
        except Exception as e:
            cherrypy.log("Widget 4: Error creating community models: {0}".format(e))
            return "Sorry something's wrong. Make sure the path to your file is correct and " \
                   "that the Python package cobrapy is loaded into your system.<br>Exception: {0}".format(e)

        return 'We created {0} community models. In the next widget, we will use them  to predict the growth ' \
               'rate of their species in isolation and when in the community using COBRA tools. A list of ' \
               'the community model file names was stored in the "{1}" file.' \
               .format(len(model_filenames), output_filename)


if __name__ == '__main__':
    app = Widget4()
    app.launch()
