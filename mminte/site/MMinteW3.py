from spyre import server
from pkg_resources import resource_filename
from os import makedirs
from os.path import join, exists
import cherrypy

from mminte import create_organism_models
from .mminte_widget import css_filename


class Widget3(server.App):
    title = 'Widget 3 '
    
    inputs = [
        {"type": "text",
         "key": 'genome_ids_file',
         "label": 'In this widget we are going to use the list of genome IDs for our '
                  'bacterial species of interest to reconstruct, gap fill and fetch single species '
                  'metabolic models from <a href="http://modelseed.theseed.org/">ModelSEED</a>. We '
                  'will need these models to predict the growth of our species of interest under '
                  'different nutritional conditions.<br><br> Please note that ModelSEED is undergoing active '
                  'development. If you are having issues, click here to contact the '
                  '<a href="mailto:chia.nicholas@mayo.edu">ModelSEED</a> or '
                  '<a href="mailto:microbialmetabolicinteractions@gmail.com">MMinte</a> developers! '
                  '<br><br>Enter the location of the file with the genome IDs',
         "value": "/home/me/my_analysis/genome_ids.txt"},

        {"type": "text",
         "key": "model_folder",
         "label": "Enter the location of the folder where single species metabolic model files will be stored",
         "value": "/home/me/my_analysis/models"}
    ]

    controls = [
        {"type": "button",
         "label": "Run Widget 3",
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
        """ Run Widget 3 and generate HTML output for Results tab. """

        cherrypy.log('Widget 3 input parameters: {0}'.format(params))

        try:
            if not exists(params['model_folder']):
                makedirs(params['model_folder'])
        except Exception as e:
            cherrypy.log('Widget 3: Error creating folder "{0}" for model files: {1}'
                         .format(params['model_folder'], e))
            return 'Sorry something went wrong creating the folder "{0}" for the model files. Make sure ' \
                   'the path to the folder is correct.<br>Exception: {1}'.format(params['model_folder'], e)

        try:
            with open(params['genome_ids_file'], 'r') as handle:
                genome_ids = [line.strip() for line in handle]
        except Exception as e:
            cherrypy.log('Widget 3: error reading genome IDs file "{0}": {1}'.format(params['genome_ids_file'], e))
            return 'Sorry, genome IDs file "{0}" was not found. Make sure the path to the file is correct.' \
                   '<br>Exception: {1}'.format(params['genome_ids_file'], e)

        try:
            cherrypy.log('Widget 3: Started creating models for {0} genomes'.format(len(genome_ids)))
            model_filenames = create_organism_models(genome_ids, params['model_folder'])
            cherrypy.log('Widget 3: Created and downloaded {0} models'.format(len(model_filenames)))
            output_filename = join(params['model_folder'], 'model_filenames.txt')
            with open(output_filename, 'w') as handle:
                handle.write('\n'.join(model_filenames))
        except Exception as e:
            cherrypy.log('Widget 3: Error creating models: {0}'.format(e))
            return "Sorry something went wrong creating metabolic models using ModelSEED.<br>" \
                   "Exception: {0}".format(e)

        return "You have {0} IDs in the genome IDs file and {1} models in the models folder. " \
               "If you are still missing models, go ahead and run this widget again. A list of " \
               "the model file names was stored in {2}" \
               .format(len(genome_ids), len(model_filenames), output_filename)
    
if __name__ == '__main__':
    app = Widget3()
    app.launch()
