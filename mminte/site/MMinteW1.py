from spyre import server
from pkg_resources import resource_filename
from os.path import exists, dirname
from os import makedirs
import cherrypy

from mminte import get_unique_otu_sequences
from .mminte_widget import css_filename


class Widget1(server.App):
    title = 'Widget 1'

    inputs = [
        {"type": "text",
         "key": "correlation_file",
         "label": "In this widget we're going to create a file with the sequences of the OTUs "
                  "that will be required for the rest of the analysis.<br><br>Enter the location of "
                  "the file with the information about the correlations between associated OTUs",
         "value": "/home/me/my_analysis/correlations.txt"},

        {"type": "text",
         "key": "representative_otu_file",
         "label": "Enter the location of the file with the sequences of the representative OTUs",
         "value": "/home/me/my_analysis/otus.fasta"},

        {"type": "text",
         "key": "unique_otu_file",
         "label": "Enter the location of the file where the sequences of the unique OTUs will be stored",
         "value": "/home/me/my_analysis/unique_otus.fasta"},
    ]

    controls = [
        {"type": "button",
         "label": "Run Widget 1",
         "id": "run_widget"},
    ]

    outputs = [
        {"type": "html",
         "id": "results",
         "control_id": "run_widget",
         "tab": "Results",
         "on_page_load": False},
    ]

    tabs = ["Results"]
    
    def getCustomCSS(self):
        with open(resource_filename(__name__, css_filename)) as style:
            return style.read()

    def getHTML(self, params):
        """ Run Widget 1 and generate HTML output for Results tab. """

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
        output_folder = dirname(params['unique_otu_file'])
        try:
            if not exists(output_folder):
                makedirs(output_folder)
        except Exception as e:
            cherrypy.log('Widget 1: Error creating folder "{0}" for unique OTUs file: {1}'.format(output_folder, e))
            return 'Sorry something went wrong creating the folder "{0}" for the unique OTUs file. Make sure ' \
                   'the path to the file is correct.<br>Exception: {1}'.format(output_folder, e)

        try:
            cherrypy.log('Widget 1: Started getting unique OTU sequences')
            get_unique_otu_sequences(params['correlation_file'], params['representative_otu_file'],
                                     params['unique_otu_file'])
            cherrypy.log("Widget 1: Finished getting unique OTU sequences")
        except Exception as e:
            cherrypy.log('Widget 1: Error getting unique OTU sequences: {0}'.format(e))
            return "Sorry something went wrong. Make sure the paths to your files are correct.<br>" \
                   "Exception: {0}.".format(e)

        head = ['Here are the OTUs that will be used in the rest of the analysis. You can find '
                'the full sequences in the "{0}" file.<br>'.format(params['unique_otu_file'])]

        with open(params['unique_otu_file']) as handle:
            for line in handle:
                if line.startswith('>'):
                    head.append('<br>{0}'.format(line))

        return head

if __name__ == '__main__':
    app = Widget1()
    app.launch()
