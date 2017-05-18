from os import makedirs
from os.path import join, exists
import cherrypy

from mminte import create_species_models
from mminte.site import MMinteApp, MMinteRoot


class Widget3(MMinteApp):
    """ Widget 3 application for spyre """

    title = 'Widget 3 '  # Must be here for button label

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": "analysis_folder",
             "label": 'In this widget we are going to use the list of genome IDs for our '
                      'bacterial species of interest to reconstruct, gap fill and fetch single species '
                      'metabolic models from <a href="http://modelseed.theseed.org/">ModelSEED</a>. We '
                      'will need these models to predict the growth of our species of interest under '
                      'different nutritional conditions.<br><br> Please note that ModelSEED is undergoing active '
                      'development. If you are having issues, click here to contact the '
                      '<a href="mailto:chia.nicholas@mayo.edu">ModelSEED</a> or '
                      '<a href="mailto:microbialmetabolicinteractions@gmail.com">MMinte</a> developers! '
                      '<br><br>Enter the location of the folder for storing the files for this analysis',
             "value": self.analysis_folder},

            {"type": "text",
             "key": "genome_ids_file",
             "label": "Enter the name of the file with the genome IDs",
             "value": "genome_ids.txt"},

            {"type": "text",
             "key": "model_folder",
             "label": "Enter the name of the folder for storing the single species model files",
             "value": "single_models"},

            {"type": "text",
             "key": "single_models_file",
             "label": "Enter the name of the file for storing the single species model file names",
             "value": "single_model_filenames.txt"}
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Widget 3",
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
        """ Run Widget 3 and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget 3 input parameters: {0}'.format(params))
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget 3: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry, something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br><br>Exception: {1}'.format(params['analysis_folder'], e)
        model_folder = join(params['analysis_folder'], params['model_folder'])
        if not exists(model_folder):
            try:
                makedirs(model_folder)
            except Exception as e:
                cherrypy.log('Widget 3: Error creating folder "{0}" for model files: {1}'
                             .format(model_folder, e))
                return 'Sorry, something went wrong creating the folder "{0}" for the single species ' \
                       'model files. Make sure the path to the folder is correct.<br><br>' \
                       'Exception: {1}'.format(model_folder, e)
        genome_ids_file = join(params['analysis_folder'], params['genome_ids_file'])
        if not exists(genome_ids_file):
            cherrypy.log('Widget 3: genome IDs file "{0}" was not found'.format(genome_ids_file))
            return 'Sorry, genome IDs file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(genome_ids_file)

        # Create single species models using ModelSEED.
        try:
            with open(genome_ids_file, 'r') as handle:
                genome_ids = [line.strip() for line in handle]
            cherrypy.log('Widget 3: Started creating models for {0} genomes'.format(len(genome_ids)))
            model_filenames = create_species_models(genome_ids, model_folder)
            output_filename = join(params['analysis_folder'], params['single_models_file'])
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(model_filenames)+'\n')
            cherrypy.log('Widget 3: Created and downloaded {0} models'.format(len(model_filenames)))

        except Exception as e:
            cherrypy.log('Widget 3: Error creating models: {0}'.format(e))
            return "Sorry something went wrong creating metabolic models using ModelSEED.<br>" \
                   "Exception: {0}".format(e)

        # Generate the output for the Results tab.
        return "You have {0} IDs in the genome IDs file and {1} models in the models folder. " \
               "If you are still missing models, go ahead and run this widget again. A list of " \
               "the model file names was stored in {2}" \
               .format(len(genome_ids), len(model_filenames), output_filename)


if __name__ == '__main__':
    cherrypy.config.update({"response.timeout": 1000000})
    app = Widget3()
    app.launch()
