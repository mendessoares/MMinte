from pkg_resources import resource_filename
from os import listdir, makedirs
from os.path import isfile, join, exists
import webbrowser

import cherrypy

from mminte import get_unique_otu_sequences, search, write_similarity_file, create_species_models, \
    get_all_pairs, create_interaction_models, read_diet_file, calculate_growth_rates, write_growth_rates_file, \
    read_correlation_file, make_d3_source
from mminte.site import MMinteApp


class WidgetRunAll(MMinteApp):
    title = 'Run All'

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": "analysis_folder",
             "label": "This widget runs the full pipeline for your analysis. You only need to provide "
                      "three files: the correlation file, the sequence file, and the diet file.<br><br>"
                      "Enter the location of the folder for storing the files for this analysis",
             "value": self.getRoot().analysisFolder()},

            {"type": "text",
             "key": "correlation_file",
             "label": "Enter the location of the file with the information about the correlations "
                      "between associated OTUs. Use the example correlation file included with the "
                      "mminte package or enter the location of the file for your analysis",
             "value": resource_filename('mminte', 'test/data/correlation.txt')},

            {"type": "text",
             "key": "representative_otu_file",
             "label": "Enter the location of the file with the sequences of the representative OTUs. "
                      "Use the example sequence file included with the mminte package or enter the "
                      "location of the file for your analysis",
             "value": resource_filename('mminte', 'test/data/all_otus.fasta')},

            {"type": "text",
             "key": "diet_file",
             "label": "You can determine which kind of metabolites are available for the "
                      "organisms by choosing a diet. In the ms_complete100 diet, over 400 metabolites are available "
                      "to the community, with a flux for the import reactions of 100 mmol/gDW/hr. The ms_complete10 diet "
                      "contains the same metabolites, but the reaction fluxes are 10 mmol/gDW/hr, and in the "
                      "ms_complete1 diet the fluxes are 1 mmol/gDW/hr. Enter the location of the file with the"
                      "metabolites and bounds for the diet",
             "value": resource_filename("mminte", "test/data/ms_complete100.txt")},

            {"type": "dropdown",
             "key": "browser_tab",
             "label": "Do you want the network to be plotted in this browser tab or in a new tab",
             "options": [{"label": "This tab", "value": "Current"},
                         {"label": "New tab", "value": "New"}],
             "value": 'Current'},
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Full Analysis",
             "id": "run_widget"}
        ]

        self.outputs = [
            {"type":"html",
             "id":"some_html",
             "control_id":"run_widget",
             "tab":"Results",
             "on_page_load": False}
        ]

        self.tabs = ["Results"]

    def getHTML(self, params):
        """ Run Widget All and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget All input parameters: {0}'.format(params))
        if not exists(params['correlation_file']):
            cherrypy.log('Widget All: correlation file "{0}" was not found'.format(params['correlation_file']))
            return 'Sorry, correlation file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['correlation_file'])
        if not exists(params['representative_otu_file']):
            cherrypy.log('Widget All: representative OTU file "{0}" was not found'
                         .format(params['representative_otu_file']))
            return 'Sorry, representative OTU file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['representative_otu_file'])
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget All: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br>Exception: {1}'.format(params['analysis_folder'], e)

        # Widget 1 - Get the unique OTU sequences.
        try:
            cherrypy.log('Widget All: Started getting unique OTU sequences')
            unique_otus_file = join(params['analysis_folder'], 'unique_otus.fasta')
            get_unique_otu_sequences(params['correlation_file'], params['representative_otu_file'],
                                     unique_otus_file)
            cherrypy.log("Widget All: Finished getting unique OTU sequences")

        except Exception as e:
            cherrypy.log('Widget All: Error getting unique OTU sequences: {0}'.format(e))
            return "Sorry something went wrong. Make sure the paths to your files are correct.<br>" \
                   "Exception: {0}.".format(e)

        # Widget 2 - Run blast search to find matching bacterial species.
        try:
            cherrypy.log('Widget All: Started blast search for matching bacterial species')
            blast_output_file = join(params['analysis_folder'], 'blast.txt')
            genome_ids, similarity = search(unique_otus_file, blast_output_file)
            cherrypy.log("Widget All: Finished running blast search")
            with open(join(params['analysis_folder'], 'genome_ids.txt'), 'w') as handle:
                handle.write('\n'.join(genome_ids))
            write_similarity_file(similarity, join(params['analysis_folder'], 'similarity.csv'))

        except Exception as e:
            cherrypy.log("Widget All: Error running blast search: {0}".format(e))
            return "Sorry something went wrong. Make sure the paths to your files are correct and " \
                   "that the correct version of blast is installed.<br>Exception: {0}".format(e)

        # Widget 3 - Create single species models using ModelSEED.
        model_folder = join(params['analysis_folder'], 'single_models')
        if not exists(model_folder):
            try:
                makedirs(model_folder)
            except Exception as e:
                cherrypy.log('Widget 3: Error creating folder "{0}" for model files: {1}'
                             .format(params['model_folder'], e))
                return 'Sorry something went wrong creating the folder "{0}" for the model files. Make sure ' \
                       'the path to the folder is correct.<br>Exception: {1}'.format(params['model_folder'], e)
        try:
            cherrypy.log('Widget All: Started creating models for {0} genomes'.format(len(genome_ids)))
            single_filenames = create_species_models(genome_ids, model_folder)
            cherrypy.log('Widget All: Created and downloaded {0} models'.format(len(single_filenames)))
            output_filename = join(params['analysis_folder'], 'single_model_filenames.txt')
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(single_filenames))
        except Exception as e:
            cherrypy.log('Widget All: Error creating models: {0}'.format(e))
            return "Sorry something went wrong creating metabolic models using ModelSEED.<br>" \
                   "Exception: {0}".format(e)

        # Widget 4 - Create two species community models.
        pair_model_folder = join(params['analysis_folder'], 'pair_models')
        if not exists(pair_model_folder):
            try:
                makedirs(pair_model_folder)
            except Exception as e:
                cherrypy.log('Widget All: We were unable to create folder "{0}" for community model files'
                             .format(pair_model_folder))
                return 'Sorry something went wrong creating the folder "{0}" for the community model files. ' \
                       'Make sure the path to the folder is correct.<br>Exception: {1}' \
                       .format(pair_model_folder, e)
        try:
            pairs = get_all_pairs(single_filenames)
            cherrypy.log('Widget All: Started creating community models from {0} pairs of single species models'
                         .format(len(pairs)))
            pair_filenames = create_interaction_models(pairs, output_folder=pair_model_folder)
            cherrypy.log("Widget All: Finished creating {0} community models".format(len(pair_filenames)))
            output_filename = join(params['analysis_folder'], 'pair_model_filenames.txt')
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(pair_filenames))
        except Exception as e:
            cherrypy.log("Widget All: Error creating community models: {0}".format(e))
            return "Sorry something's wrong. Make sure the path to your file is correct and " \
                   "that the Python package cobrapy is loaded into your system.<br>Exception: {0}".format(e)

        # Widget 5 - Calculate growth rates for the two species models.
        try:
            cherrypy.log("Widget All: Starting the growth rate calculations for {0} pair models"
                         .format(len(pair_filenames)))
            medium = read_diet_file(params['diet_file'])
            growth_rates = calculate_growth_rates(pair_filenames, medium)
            cherrypy.log("Widget All: Finished calculating the growth rates of the species")
            write_growth_rates_file(growth_rates, join(params['analysis_folder'], 'growth_rates.csv'))

        except Exception as e:
            cherrypy.log("Widget All: Error calculating growth rates: {0}".format(e))
            return "Sorry something's wrong. Make sure the path to your file is correct.<br>Exception: {0}".format(e)

        # Widget 6 - Generate data for plot of interaction network.
        self.getRoot().analysisFolder(params['analysis_folder'])
        correlation = read_correlation_file(params['correlation_file'])
        make_d3_source(growth_rates, join(params['analysis_folder'], 'data4plot.json'), similarity, correlation)

        # Generate the output for the Results tab.
        text = ["The plot with the network of interactions between your organisms is shown below or"
                "on a new tab.<br>The shading of the nodes indicates how close the sequence of the "
                "OTU is to the sequence of the genome. The darker the node, the higher the similarity.<br"
                "The length and thickness of the links reflect the association values on the initial "
                "file you provided. The shorter and thicker the link, the higher the association value.<br"
                "The colors of the links reflect the kind of interaction. The red, green and grey "
                "represent negative, positive and no interaction, respectively.<br>"
                "<a href='http://d3js.org/'>D3 is awesome</a>! If you mouse over the nodes, you get "
                "the id of the OTU, and if you click a node and drag it, the network will follow it."]

        if params['browser_tab'] == 'Current':
            with open(resource_filename(__name__, 'static/plot.html')) as page:
                text.append(page.read())
        else:
            webbrowser.open('http://localhost:8080/widget6_out', new=1)

        return text


if __name__ == '__main__':
    app = WidgetRunAll()
    app.launch()