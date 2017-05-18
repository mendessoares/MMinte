from pkg_resources import resource_filename
from os import makedirs
from os.path import join, exists
import cherrypy
import webbrowser

from mminte import get_unique_otu_sequences, search, write_similarity_file, create_species_models, \
    get_all_pairs, create_interaction_models, read_diet_file, calculate_growth_rates, write_growth_rates_file, \
    read_correlation_file, make_d3_source
from mminte.site import MMinteApp, MMinteRoot


class WidgetRunAll(MMinteApp):
    """ Widget Run All application for spyre """

    title = 'Run All'  # Must be here for button label

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": "analysis_folder",
             "label": "This widget runs the full pipeline for your analysis. You only need to provide "
                      "three files: the correlation file, the sequence file, and the diet file.<br><br>"
                      "Enter the location of the folder for storing the files for this analysis",
             "value": self.analysis_folder},

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
                      "organisms by choosing a diet. In the ms_complete100 diet, over "
                      "400 metabolites are available to the community, with a flux for the "
                      "import reactions of 100 mmol/gDW/hr. The ms_complete10 diet contains "
                      "the same metabolites, but the reaction fluxes are 10 mmol/gDW/hr, and "
                      "in the ms_complete1 diet the fluxes are 1 mmol/gDW/hr. Enter the location "
                      "of the file with the metabolites and bounds for the diet",
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
            {"type": "html",
             "id": "results",
             "control_id": "run_widget",
             "tab": "Results",
             "on_page_load": False}
        ]

        self.tabs = ["Results"]

        self.root = MMinteRoot(
            templateVars=self.templateVars,
            title=self.title,
            inputs=self.inputs,
            outputs=self.outputs,
            controls=self.controls,
            tabs=self.tabs,
            spinnerFile=self.spinnerFile,
            getJsonDataFunction=self.getJsonData,
            getDataFunction=self.getData,
            getTableFunction=self.getTable,
            getPlotFunction=self.getPlot,
            getImageFunction=self.getImage,
            getD3Function=self.getD3,
            getCustomJSFunction=self.getCustomJS,
            getCustomCSSFunction=self.getCustomCSS,
            getCustomHeadFunction=self.getCustomHead,
            getHTMLFunction=self.getHTML,
            getDownloadFunction=self.getDownload,
            noOutputFunction=self.noOutput,
            storeUploadFunction=self.storeUpload,
            prefix=self.prefix)

    def getHTML(self, params):
        """ Run Widget All and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget A input parameters: {0}'.format(params))
        if not exists(params['correlation_file']):
            cherrypy.log('Widget A: correlation file "{0}" was not found'.format(params['correlation_file']))
            return 'Sorry, correlation file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['correlation_file'])
        if not exists(params['representative_otu_file']):
            cherrypy.log('Widget A: representative OTU file "{0}" was not found'
                         .format(params['representative_otu_file']))
            return 'Sorry, representative OTU file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['representative_otu_file'])
        if not exists(params['diet_file']):
            cherrypy.log('Widget A: diet file "{0}" was not found'.format(params['diet_file']))
            return 'Sorry, diet file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['diet_file'])
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget A: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry, something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br><br>Exception: {1}'.format(params['analysis_folder'], e)

        # Widget 1 - Get the unique OTU sequences.
        try:
            cherrypy.log('Widget A1: Started getting unique OTU sequences')
            unique_otus_file = join(params['analysis_folder'], 'unique_otus.fasta')
            get_unique_otu_sequences(read_correlation_file(params['correlation_file']),
                                     params['representative_otu_file'],
                                     unique_otus_file)
            cherrypy.log("Widget A1: Finished getting unique OTU sequences")

        except Exception as e:
            cherrypy.log('Widget A1: Error getting unique OTU sequences: {0}'.format(e))
            return "Sorry, something went wrong. Make sure the paths to your files are correct.<br><br>" \
                   "Exception: {0}.".format(e)

        # Widget 2 - Run blast search to find matching bacterial species.
        try:
            cherrypy.log('Widget A2: Started blast search for matching bacterial species')
            blast_output_file = join(params['analysis_folder'], 'blast.txt')
            genome_ids, similarity = search(unique_otus_file, blast_output_file)
            with open(join(params['analysis_folder'], 'genome_ids.txt'), 'w') as handle:
                handle.write('\n'.join(genome_ids)+'\n')
            write_similarity_file(similarity, join(params['analysis_folder'], 'similarity.csv'))
            cherrypy.log("Widget A2: Finished blast search")

        except Exception as e:
            cherrypy.log("Widget A2: Error running blast search: {0}".format(e))
            return "Sorry, something went wrong. Make sure the paths to your files are correct and " \
                   "that the correct version of blast is installed.<br><br>Exception: {0}".format(e)

        # Widget 3 - Create single species models using ModelSEED.
        model_folder = join(params['analysis_folder'], 'single_models')
        if not exists(model_folder):
            try:
                makedirs(model_folder)
            except Exception as e:
                cherrypy.log('Widget A3: Error creating folder "{0}" for model files: {1}'
                             .format(params['model_folder'], e))
                return 'Sorry something went wrong creating the folder "{0}" for the model files. Make sure ' \
                       'the path to the folder is correct.<br><br>Exception: {1}'.format(params['model_folder'], e)
        try:
            cherrypy.log('Widget A3: Started creating models for {0} genomes'.format(len(genome_ids)))
            single_filenames = create_species_models(genome_ids, model_folder)
            output_filename = join(params['analysis_folder'], 'single_model_filenames.txt')
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(single_filenames)+'\n')
            cherrypy.log('Widget A3: Finished creating and downloading {0} models'.format(len(single_filenames)))

        except Exception as e:
            cherrypy.log('Widget A3: Error creating models: {0}'.format(e))
            return "Sorry, something went wrong creating metabolic models using ModelSEED.<br><br>" \
                   "Exception: {0}".format(e)

        # Widget 4 - Create two species community models.
        pair_model_folder = join(params['analysis_folder'], 'pair_models')
        if not exists(pair_model_folder):
            try:
                makedirs(pair_model_folder)
            except Exception as e:
                cherrypy.log('Widget A4: We were unable to create folder "{0}" for community model files'
                             .format(pair_model_folder))
                return 'Sorry, something went wrong creating the folder "{0}" for the community model files. ' \
                       'Make sure the path to the folder is correct.<br><br>Exception: {1}' \
                       .format(pair_model_folder, e)
        try:
            pairs = get_all_pairs(single_filenames)
            cherrypy.log('Widget A4: Started creating community models from {0} pairs of single species models'
                         .format(len(pairs)))
            pair_filenames = create_interaction_models(pairs, output_folder=pair_model_folder)
            output_filename = join(params['analysis_folder'], 'pair_model_filenames.txt')
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(pair_filenames)+'\n')
            cherrypy.log("Widget A4: Finished creating {0} community models".format(len(pair_filenames)))

        except Exception as e:
            cherrypy.log("Widget A4: Error creating community models: {0}".format(e))
            return "Sorry, something went wrong. Make sure the path to your file is correct and " \
                   "that the Python package cobrapy is loaded into your system.<br><br>Exception: {0}".format(e)

        # Widget 5 - Calculate growth rates for the two species models.
        try:
            cherrypy.log("Widget A5: Started calculating growth rates for {0} pair models"
                         .format(len(pair_filenames)))
            medium = read_diet_file(params['diet_file'])
            growth_rates = calculate_growth_rates(pair_filenames, medium)
            write_growth_rates_file(growth_rates, join(params['analysis_folder'], 'growth_rates.csv'))
            cherrypy.log("Widget A5: Finished calculating the growth rates")

        except Exception as e:
            cherrypy.log("Widget A5: Error calculating growth rates: {0}".format(e))
            return "Sorry, something went wrong. Make sure the path to your file is correct.<br><br>" \
                   "Exception: {0}".format(e)

        # Widget 6 - Generate data for plot of interaction network.
        try:
            cherrypy.log('Widget A6: Started generating data for plot of interaction network')
            correlation = read_correlation_file(params['correlation_file'])
            make_d3_source(growth_rates, join(params['analysis_folder'], 'data4plot.json'), similarity, correlation)
            make_d3_source(growth_rates, self.getRoot().data4plot_filename(), similarity, correlation)
            cherrypy.log('Widget A6: Finished generating data for plot of interaction network')

        except Exception as e:
            cherrypy.log('Widget A6: Error generating data for plot of network: {0}'.format(e))
            return 'Sorry, something went wrong. Make sure the locations of your files are correct.<br><br>' \
                   'Exception: {0}'.format(e)

        # Generate the output for the Results tab.
        text = ["The plot with the network of interactions between your organisms is shown below or "
                "on a new tab.<br><br>The shading of the nodes indicates how close the sequence of the "
                "OTU is to the sequence of the genome. The darker the node, the higher the similarity.<br><br>"
                "The length and thickness of the links reflect the association values on the initial "
                "file you provided. The shorter and thicker the link, the higher the association value.<br><br>"
                "The colors of the links reflect the kind of interaction. The red, green and grey "
                "represent negative, positive and no interaction, respectively.<br><br>"
                "<a href='http://d3js.org/'>D3 is awesome</a>! If you mouse over the nodes, you get "
                "the ID of the OTU, and if you click a node and drag it, the network will follow it."]

        if params['browser_tab'] == 'Current':
            text.append(self.getRoot().widget6_out())
        else:
            webbrowser.open('http://localhost:8080/widget6_out', new=1)

        return text


if __name__ == '__main__':
    cherrypy.config.update({"response.timeout": 1000000})
    app = WidgetRunAll()
    app.launch()
