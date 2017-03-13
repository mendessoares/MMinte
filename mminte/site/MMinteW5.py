from spyre import server
from pkg_resources import resource_filename
from os.path import exists, dirname
from os import makedirs
import cherrypy

from mminte import calculate_growth_rates
from .mminte_widget import css_filename


class Widget5(server.App):
    title = 'Widget 5'
    
    inputs = [
        {"type": "text",
         "key": 'pair_list_file',
         "label": "In this widget we're going to calculate growth rates and evaluate interactions for the species "
                  "in each community. Because we will want to know how the presence of another species "
                  "in the community affects the growth of a particular organism, we will estimate how "
                  "the species grow when in the absence and presence of another species in the community "
                  "under particular nutritional conditions and label the interactions based on a table in the "
                  "<a href 'http://aem.asm.org/content/81/12/4049.full'>AEM paper by Almut Heinken and "
                  "Ines Thiele</a>. What happens between two species may be broadly divided into positive, "
                  "negative, or no interaction. A data frame with the growth rates of each species "
                  "in the community and in isolation will be created.<br><br>Enter the location of the file "
                  "with the list of two-species community models",
         "value": "/home/me/my_analysis/community/pair_model_filenames.txt"},

        {"type": "text",
         "key": "diet_file",
         "label" : "You can determine which kind of metabolites are available for the "
                   "organisms by choosing a diet. In the 'Complete' diet, 380 metabolites are available "
                   "to the model, with a flux for the import reactions of 100 mmol/gDW/hr. 'Variant 1' "
                   "contains the same metabolites, but the reaction fluxes are 10 mmol/gDW/hr, and in "
                   "'Variant 2' the fluxes are 1 mmol/gDW/hr. Enter the location of the file with the"
                   "metabolites and bounds for the diet",
         "value": "/home/me/my_analysis/diets/complete.txt"},

        {"type": "text",
         "key": 'growth_rates_file',
         "label": "Enter the location of the file where the growth rates will be stored",
         "value": "/home/me/my_analysis/growth_rates.csv"},
    ]

    controls = [
        {"type": "button",
         "label": "Run Widget 5",
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
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
    
    def getHTML(self, params):
        """ Run Widget 5 and generate HTML output for Results tab. """

        if not exists(params['pair_list_file']):
            cherrypy.log('Widget 5: pair list file "{0}" was not found'.format(params['model_list_file']))
            return 'Sorry, pair list file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['pair_list_file'])
        if not exists(params['diet_file']):
            cherrypy.log('Widget 5: diet file "{0}" was not found'.format(params['diet_file']))
            return 'Sorry, diet file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['diet_file'])
        with open(params['pair_list_file'], 'r') as handle:
            pair_models = [line.strip() for line in handle]
        output_folder = dirname(params['growth_rates_file'])
        try:
            if not exists(output_folder):
                makedirs(output_folder)
        except Exception as e:
            cherrypy.log('Widget 5: We were unable to create folder "{0}" for blast output file'.format(output_folder))
            return 'Sorry something went wrong creating the folder "{0}" for the blast output file. Make sure ' \
                   'the path to the file is correct.<br>Exception: {1}'.format(output_folder, e)

        # @todo Need to convert diet file to dictionary, save as JSON file?
        try:
            cherrypy.log("Widget 5: Starting the growth rate calculations for {0} pair models".format(len(pair_models)))
            growth_rates = calculate_growth_rates(pair_models, params['diet_file'])
            cherrypy.log("Widget 5: Finished calculating the growth rates of the species")
            growth_rates.to_csv(params['growth_rates_file'], index=False)

        except Exception as e:
            cherrypy.log("Widget 5: Error calculating growth rates: {0}".format(e))
            return "Sorry something's wrong. Make sure the path to your file is correct.<br>Exception: {0}".format(e)

        head = ["Here's a glimpse of what the first few lines of your growth rates file look like.<br>"]
        # @todo Add some rows from the data frame

        return head

if __name__ == '__main__':
    app = Widget5()
    app.launch()
