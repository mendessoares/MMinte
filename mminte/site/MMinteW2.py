from spyre import server
from pkg_resources import resource_filename
from widget2 import blastSeqs, listTaxId4ModelSEED
import os

import cherrypy


#cherrypy.config.update({"response.timeout":1000000,'log.access_file':'../supportFiles/logs/logAccess_file.txt', 'log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

class Widget2(server.App):
    title = 'Widget 2'
    
    inputs = [
       {"type": "text",
         "label": "<font size=4pt>In this widget we're going to use the representative OTU sequences to find the closest matching bacterial species with a whole genome sequence. Two results files are produced. One contains lists the percent similarity between the individual representative OTUs and the closest match, identified by the NCBI genome ID. The other one contains the list of unique genome IDs found. This last file is used in Widget 3 to reconstruct metabolic models for the corresponding bacterial species  </font> <br> <br>Do you want to just run the widget with the default example files?",
        "key": 'text6',
         "value": "Yes or No"},

        {"type":"text",
        "key":"text7",
        "label" : "<font size=3pt>Tell me which file has the sequences you want to get the genome ID for</font>",
        "value":"Enter the path to the fasta file you want to use"},



        {"type": "text",
         "key": 'text8',
         "label": "<font size=3pt>Tell me which you folder would like to put the results from your analysis in</font>",
         "value": "Enter the path to your results folder"},

        {"type": "text",
         "key": 'text9',
         "label": "<font size=3pt>Tell me what do you want the results file with the percent similarity information to be called</font>",
         "value": "Enter the name of your file"},

        {"type": "text",
         "key": 'text10',
         "label": "<font size=3pt>Tell me what do you want the results file with the list of genome IDs to be called</font>",
         "value": "Enter the name of your file"}



        ]
    
    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]
    
    controls = [{"type":"button",
                 "label":"Run Widget 2",
                 "id":"run_widget"}]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        with open(resource_filename(__name__, 'static/custom_styleMMinte.css')) as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
    
    def getHTML(self,params):

        if params['text6'] == 'Yes' or params['text1'] == "yes":
            seqsToBlast = '../supportFiles/exampleRun/userOutput/reprOTUsToUse.fasta'
            outFolder = '../supportFiles/exampleRun/userOutput/'
            outSimilFile = 'similFile.txt'
            outputSimil = outFolder + outSimilFile

            outIDsFile = 'ids4MS.txt'
            outputIDs = outFolder + outIDsFile

        else:
            seqsToBlast = params['text7']
            outFolder = params['text8']
            outSimilFile = params['text9']
            outputSimil = outFolder + outSimilFile

            outIDsFile = params['text10']
            outputIDs = outFolder + outIDsFile

        if not os.path.exists(outFolder):
            os.makedirs(outFolder)



        try:
            blastSeqs(seqsToBlast)
            cherrypy.log("We finished blasting the sequences against the database with function blastSeqs.")
        except:
            cherrypy.log("We were unable to run blastSeqs.")
            return "Sorry something's wrong. Make sure the path to your file is correct and that the correct version of blast is installed."
            exit()


            
        try:
            listTaxId4ModelSEED(outputSimil,outputIDs)
            cherrypy.log("We finished creating the list of genomeIDs we'll send to ModelSEED with the function listTaxId4ModelSEED.")
        except:
            cherrypy.log("We were unable to run listTaxId4ModelSEED.")
            return "Sorry something's wrong. Make sure the path to your file is correct."
            exit()


        
        head = ["<strong><font color=#00961E size=4pt>Here's the genomeIDs we will use to reconstruct the metabolic models in the next widget:</strong></font>"]
        head.append('<br>')
        head.append("<strong><font color=#00961E size=2pt>You can find this and the other files created here in the userOutput folder.</strong></font>")
        head.append('<br>')
        
        myfile = open(outputIDs,'r')
        
        for i in myfile:
            head.append('<br>')
            head.append(i)
        
        return head
    
if __name__ == '__main__':
    app = Widget2()
    app.launch()
