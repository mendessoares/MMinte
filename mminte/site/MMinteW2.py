from os.path import exists, join
from os import makedirs
import cherrypy

from mminte import search, write_similarity_file
from mminte.site import MMinteApp, MMinteRoot


class Widget2(MMinteApp):
    """ Widget 2 application for spyre """

    title = 'Widget 2'  # Must be here for button label

    def __init__(self):
        self.inputs = [
            {"type": "text",
             "key": "analysis_folder",
             "label": "In this widget we are going to use the unique representative OTU sequences to "
                      "find the closest matching bacterial species with a whole genome sequence by "
                      "running blast. There are three output files: (1) blast output file, (2) a file "
                      "with the percent similarity between the individual representative OTUs and the "
                      "closest match, identified by the NCBI genome ID, and (3) a file with the "
                      "list of unique genome IDs which is used to reconstruct metabolic models for "
                      "the corresponding bacterial species.<br><br>Enter the location of the folder "
                      "for storing the files for this analysis",
             "value": self.analysis_folder},

            {"type": "text",
             "key": "unique_otus_file",
             "label": "Enter the name of the file with the sequences of the unique representative OTUs",
             "value": 'unique_otus.fasta'},

            {"type": "text",
             "key": "blast_output_file",
             "label": "Enter the name of the file for storing the blast output",
             "value": "blast.txt"},

            {"type": "text",
             "key": 'similarity_file',
             "label": "Enter the name of the file for storing the percent similarity information",
             "value": "similarity.csv"},

            {"type": "text",
             "key": 'genome_ids_file',
             "label": "Enter the name of the file for storing the list of genome IDs",
             "value": "genome_ids.txt"}
        ]

        self.controls = [
            {"type": "button",
             "label": "Run Widget 2",
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
        """ Run Widget 2 and generate HTML output for Results tab. """

        # Validate input parameters.
        cherrypy.log('Widget 2 input parameters: {0}'.format(params))
        if not exists(params['analysis_folder']):
            try:
                makedirs(params['analysis_folder'])
            except Exception as e:
                cherrypy.log('Widget 2: Error creating folder "{0}" for analysis files: {1}'
                             .format(params['analysis_folder'], e))
                return 'Sorry, something went wrong creating the folder "{0}" for the analysis files. Make sure ' \
                       'the path to the file is correct.<br><br>Exception: {1}'.format(params['analysis_folder'], e)
        unique_otus_file = join(params['analysis_folder'], params['unique_otus_file'])
        if not exists(unique_otus_file):
            cherrypy.log('Widget 2: unique OTUs file "{0}" was not found'.format(unique_otus_file))
            return 'Sorry, unique OTUs file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(unique_otus_file)

        # Run blast search to find matching bacterial species.
        try:
            cherrypy.log('Widget 2: Started blast search for matching bacterial species')
            genome_ids, similarity = search(unique_otus_file,
                                            join(params['analysis_folder'], params['blast_output_file']))
            with open(join(params['analysis_folder'], params['genome_ids_file']), 'w') as handle:
                handle.write('\n'.join(genome_ids)+'\n')
            write_similarity_file(similarity, join(params['analysis_folder'], params['similarity_file']))
            cherrypy.log("Widget 2: Finished running blast search")

        except Exception as e:
            cherrypy.log("Widget 2: Error running blast search: {0}".format(e))
            return "Sorry, something went wrong. Make sure the paths to your files are correct and " \
                   "that the correct version of blast is installed.<br><br>Exception: {0}".format(e)

        # Generate the output for the Results tab.
        text = ["Here's the genome IDs we will use to reconstruct the metabolic models in the next widget:<br>"]
        for g_id in genome_ids:
            text.append('<br>{0}'.format(g_id))

        return text


if __name__ == '__main__':
    cherrypy.config.update({"response.timeout": 1000000})
    app = Widget2()
    app.launch()
