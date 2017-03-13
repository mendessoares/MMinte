from spyre import server
from pkg_resources import resource_filename
from os.path import exists, dirname
from os import makedirs
import cherrypy

from mminte import search
from .mminte_widget import css_filename


class Widget2(server.App):
    title = 'Widget 2'
    
    inputs = [
        {"type": "text",
         "key": "unique_otus_file",
         "label": "In this widget we're going to use the unique representative OTU sequences to "
                  "find the closest matching bacterial species with a whole genome sequence by "
                  "running blast. Two files are produced. The first file contains the percent similarity "
                  "between the individual representative OTUs and the closest match, identified "
                  "by the NCBI genome ID. The second file contains the "
                  "list of unique genome IDs and is used to reconstruct metabolic models "
                  "for the corresponding bacterial species.<br><br>Enter the location of the file with "
                  "the sequences of the unique representative OTUs",
         "value": "/home/me/my_analysis/unique_otus.fasta"},

        {"type": "text",
         "key": "blast_output_file",
         "label": "Enter the location of the file where blast output will be stored",
         "value": "/home/me/my_analysis/blast.txt"},

        {"type": "text",
         "key": 'similarity_file',
         "label": "Enter the location of the file where the percent similarity information will be stored",
         "value": "/home/me/my_analysis/similarity.txt"},

        {"type": "text",
         "key": 'genome_ids_file',
         "label": "Enter the location of the file where the list of genome IDs will be stored",
         "value": "/home/me/my_analysis/genome_ids.txt"}
    ]

    controls = [
        {"type": "button",
         "label": "Run Widget 2",
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
        """ Run Widget 2 and generate HTML output for Results tab. """

        cherrypy.log('Widget 2 input parameters: {0}'.format(params))

        if not exists(params['unique_otus_file']):
            cherrypy.log('Widget 2: unique OTUs file "{0}" was not found'.format(params['unique_otus_file']))
            return 'Sorry, unique OTUs file "{0}" was not found. Make sure the path to the file is correct.' \
                   .format(params['unique_otus_file'])
        output_folder = dirname(params['blast_output_file'])
        try:
            if not exists(output_folder):
                makedirs(output_folder)
        except:
            cherrypy.log('Widget 2: Error creating folder "{0}" for blast output file: {1}'.format(output_folder, e))
            return 'Sorry something went wrong creating the folder "{0}" for the blast output file. Make sure ' \
                   'the path to the file is correct.<br>Exception: {1}'.format(output_folder, e)
        output_folder = dirname(params['similarity_file'])
        try:
            if not exists(output_folder):
                makedirs(output_folder)
        except:
            cherrypy.log('Widget 2: Error creating folder "{0}" for similarity file: {1}'.format(output_folder, e))
            return 'Sorry something went wrong creating the folder "{0}" for the similarity file. Make sure ' \
                   'the path to the file is correct.<br>Exception: {1}'.format(output_folder, e)
        output_folder = dirname(params['genome_ids_file'])
        try:
            if not exists(output_folder):
                makedirs(output_folder)
        except:
            cherrypy.log('Widget 2: Error creating folder "{0}" for genome IDs file: {1}'.format(output_folder, e))
            return 'Sorry something went wrong creating the folder "{0}" for the genome IDs file. Make sure ' \
                   'the path to the file is correct.<br>Exception: {1}'.format(output_folder, e)

        try:
            cherrypy.log('Widget 2: Started blast search for matching bacterial species')
            genome_ids, similarity = search(params['unique_otus_file'], params['blast_output_file'])
            cherrypy.log("Widget 2: Finished running blast search")
            with open(params['genome_ids_file'], 'w') as handle:
                handle.write('\n'.join(genome_ids))
            with open(params['similarity_file'], 'w') as handle:
                lines = ['\t'.join(fields) for fields in similarity]
                handle.write('\n'.join(lines))
        except Exception as e:
            cherrypy.log("Widget 2: Error running blast search: {0}".format(e))
            return "Sorry something went wrong. Make sure the paths to your files are correct and " \
                   "that the correct version of blast is installed.<br>Exception: {0}".format(e)

        head = ["Here's the genome IDs we will use to reconstruct the metabolic models in the next widget:<br>"]
        for g_id in genome_ids:
            head.append('<br>{0}'.format(g_id))

        return head
    
if __name__ == '__main__':
    app = Widget2()
    app.launch()
