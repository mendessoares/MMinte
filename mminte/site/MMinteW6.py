from pkg_resources import resource_filename
from os.path import join, exists
from os import makedirs
import webbrowser
import cherrypy

from mminte import make_d3_source, read_similarity_file, read_correlation_file, read_growth_rates_file
from mminte.site import MMinteApp, MMinteRoot


class Widget6(MMinteApp):
    """ Widget 6 application for spyre """

    title = 'Widget 6'  # Must be here for button label

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": 'analysis_folder',
             "label": 'And last, but not least, in this widget we are going to plot a network where the nodes '
                      'represent the different OTUs and the length and thickness of links represent the '
                      'correlations in your initial files. The color of the links represents the kind '
                      'of interaction predicted between those two OTUs by MMinte. We will do this using '
                      '<a href="https://d3js.org/">D3</a>, a neat "JavaScript library for manipulating '
                      'documents based on data".<br><br>Enter the location of the folder '
                      'for storing the files for this analysis',
             "value": self.analysis_folder},

            {"type": "text",
             "key": "correlation_file",
             "label": "Enter the name of the file with the information about the correlations between associated OTUs",
             "value": resource_filename('mminte', "test/data/correlation.txt")},

            {"type": "text",
             "key": "similarity_file",
             "label": "Enter the name of the file with percent similarity information",
             "value": "similarity.csv"},

            {"type": "text",
             "key": "growth_rates_file",
             "label": "Enter the name of the file with growth rates information",
             "value": "growth_rates.csv"},

            {"type": "dropdown",
             "key": "browser_tab",
             "label": "Do you want the network to be plotted in this browser tab or in a new tab",
             "options": [{"label": "This tab", "value": "Current"},
                         {"label": "New tab", "value": "New"}],
             "value": 'Current'},
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Widget 6",
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
        """ Run Widget 6 and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget 6 input parameters: {0}'.format(params))
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget 6: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry, something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br><br>Exception: {1}'.format(params['analysis_folder'], e)
        growth_rates_file = join(params['analysis_folder'], params['growth_rates_file'])
        if not exists(growth_rates_file):
            cherrypy.log('Widget 6: growth rates file "{0}" was not found'.format(growth_rates_file))
            return 'Sorry, growth rates file "{0}" was not found. Make sure the path to the file is correct.' \
                .format(growth_rates_file)
        similarity_file = join(params['analysis_folder'], params['similarity_file'])
        if not exists(similarity_file):
            cherrypy.log('Widget 6: similarity file "{0}" was not found'.format(similarity_file))
            return 'Sorry, similarity file "{0}" was not found. Make sure the path to the file is correct.' \
                .format(similarity_file)
        if not exists(params['correlation_file']):
            cherrypy.log('Widget 6: correlation file "{0}" was not found'.format(params['correlation_file']))
            return 'Sorry, correlation file "{0}" was not found. Make sure the path to the file is correct.' \
                .format(params['correlation_file'])

        # Generate data for plot of interaction network.
        try:
            cherrypy.log('Widget 6: Started generating data for plot of interaction network')
            growth_rates = read_growth_rates_file(growth_rates_file)
            similarity = read_similarity_file(similarity_file)
            correlation = read_correlation_file(params['correlation_file'])
            make_d3_source(growth_rates, join(params['analysis_folder'], 'data4plot.json'), similarity, correlation)
            make_d3_source(growth_rates, self.getRoot().data4plot_filename(), similarity, correlation)
            cherrypy.log('Widget 6: Finished generating data for plot of interaction network')

        except Exception as e:
            cherrypy.log('Widget 6: Error generating data for plot of network: {0}'.format(e))
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
            webbrowser.open('http://localhost:{0}/widget6_out'.format(cherrypy.server.socket_port), new=1)

        return text


if __name__ == '__main__':
    app = Widget6()
    app.launch()
