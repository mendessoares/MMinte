from pkg_resources import resource_filename
from os.path import exists, join
from os import makedirs
import cherrypy

from mminte import get_unique_otu_sequences, read_correlation_file
from mminte.site import MMinteApp, MMinteRoot


class Widget1(MMinteApp):
    """ Widget 1 application for spyre """

    title = 'Widget 1'  # Must be here for button label

    def __init__(self):

        self.inputs = [
            {"type": "text",
             "key": "analysis_folder",
             "label": "In this widget we are going to create a file with the sequences of the OTUs "
                      "that will be required for the rest of the analysis.<br><br> "
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
             "key": "unique_otu_file",
             "label": "Enter the name of the file for storing the sequences of the unique OTUs",
             "value": 'unique_otus.fasta'},
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Widget 1",
             "id": "run_widget"},
        ]

        self.outputs = [
            {"type": "html",
             "id": "results",
             "control_id": "run_widget",
             "tab": "Results",
             "on_page_load": False},
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
        """ Run Widget 1 and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget 1 input parameters: {0}'.format(params))
        if not exists(params['correlation_file']):
            cherrypy.log('Widget 1: correlation file "{0}" was not found'.format(params['correlation_file']))
            return 'Sorry, correlation file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['correlation_file'])
        if not exists(params['representative_otu_file']):
            cherrypy.log('Widget 1: representative OTU file "{0}" was not found'
                         .format(params['representative_otu_file']))
            return 'Sorry, representative OTU file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['representative_otu_file'])
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget 1: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br><br>Exception: {1}'.format(params['analysis_folder'], e)

        # Get the unique OTU sequences.
        try:
            cherrypy.log('Widget 1: Started getting unique OTU sequences')
            get_unique_otu_sequences(read_correlation_file(params['correlation_file']),
                                     params['representative_otu_file'],
                                     join(params['analysis_folder'], params['unique_otu_file']))
            cherrypy.log("Widget 1: Finished getting unique OTU sequences")
        except Exception as e:
            cherrypy.log('Widget 1: Error getting unique OTU sequences: {0}'.format(e))
            return "Sorry, something went wrong. Make sure the paths to your files are correct.<br><br>" \
                   "Exception: {0}.".format(e)

        # Generate the output for the Results tab.
        text = ['Here are the OTUs that will be used in the rest of the analysis. You can find '
                'the full sequences in the "{0}" file.<br>'.format(params['unique_otu_file'])]
        with open(join(params['analysis_folder'], params['unique_otu_file']), 'r') as handle:
            for line in handle:
                if line.startswith('>'):
                    text.append('<br>{0}'.format(line))

        return text

if __name__ == '__main__':
    app = Widget1()
    app.launch()
