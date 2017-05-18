from pkg_resources import resource_filename
from os.path import exists, join
from os import makedirs
import cherrypy

from mminte import calculate_growth_rates, read_diet_file
from mminte.site import MMinteApp, MMinteRoot


class Widget5(MMinteApp):
    """ Widget 5 application for spyre """

    title = 'Widget 5'  # Must be here for button label

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": 'analysis_folder',
             "label": "In this widget we are going to calculate growth rates and evaluate interactions "
                      "for the species in each community. Because we will want to know how the presence "
                      "of another species in the community affects the growth of a particular organism, "
                      "we will estimate how the species grow when in the absence and presence of another "
                      "species in the community under particular nutritional conditions and label the "
                      "interactions based on a table in the <a href 'http://aem.asm.org/content/81/12/4049.full'>"
                      "AEM paper by Almut Heinken and Ines Thiele</a>. What happens between two species "
                      "may be broadly divided into positive, negative, or no interaction. A data frame "
                      "with the growth rates of each species in the community and in isolation is created."
                      "<br><br>Enter the location of the folder for storing the files for this analysis",
             "value": self.analysis_folder},

            {"type": "text",
             "key": "pair_models_file",
             "label": "Enter the name of the file with the list of two species model file names",
             "value": "pair_model_filenames.txt"},

            {"type": "text",
             "key": "diet_file",
             "label": "You can determine which kind of metabolites are available for the organisms by "
                      "choosing a diet. In the ms_complete100 diet, over 400 metabolites are available "
                      "to the community, with a flux for the import reactions of 100 mmol/gDW/hr. The "
                      "ms_complete10 diet contains the same metabolites, but the reaction fluxes are "
                      "10 mmol/gDW/hr, and in the ms_complete1 diet the fluxes are 1 mmol/gDW/hr. Enter "
                      "the location of the file with the metabolites and bounds for the diet",
             "value": resource_filename("mminte", "test/data/ms_complete100.txt")},

            {"type": "text",
             "key": 'growth_rates_file',
             "label": "Enter the name of the file for storing the growth rates",
             "value": "growth_rates.csv"},
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Widget 5",
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
        """ Run Widget 5 and generate HTML output for Results tab. """

        # Validate input parameters.
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget 5: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry, something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br><br>Exception: {1}'.format(params['analysis_folder'], e)
        if not exists(params['diet_file']):
            cherrypy.log('Widget 5: diet file "{0}" was not found'.format(params['diet_file']))
            return 'Sorry, diet file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['diet_file'])
        pair_models_file = join(params['analysis_folder'], params['pair_models_file'])
        if not exists(pair_models_file):
            cherrypy.log('Widget 5: pair list file "{0}" was not found'.format(pair_models_file))
            return 'Sorry, pair list file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(pair_models_file)

        # Calculate growth rates for the two species models.
        try:
            with open(pair_models_file, 'r') as handle:
                pair_models = [line.strip() for line in handle]
            cherrypy.log("Widget 5: Starting calculating growth rates for {0} pair models".format(len(pair_models)))
            medium = read_diet_file(params['diet_file'])
            growth_rates = calculate_growth_rates(pair_models, medium)
            output_file = join(params['analysis_folder'], params['growth_rates_file'])
            growth_rates.to_csv(output_file, index=False)
            cherrypy.log("Widget 5: Finished calculating growth rates")

        except Exception as e:
            cherrypy.log("Widget 5: Error calculating growth rates: {0}".format(e))
            return "Sorry, something went wrong. Make sure the path to your file is correct.<br><br>" \
                   "Exception: {0}".format(e)

        # Generate the output for the Results tab.
        text = ["Here's a glimpse of what the first few lines of your growth rates file look like.<br><br>"]
        with open(output_file, 'r') as handle:
            for index in range(15):
                text.append(handle.readline())
        return text


if __name__ == '__main__':
    cherrypy.config.update({"response.timeout": 1000000})
    app = Widget5()
    app.launch()
