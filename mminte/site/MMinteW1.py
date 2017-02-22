
__package__ = "mminte"

from spyre import server
from mminte import get_unique_otu_sequences
from pkg_resources import resource_filename
#from widget1 import getUniqueOTU, getSeqs, workingOTUs
import os


import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt', 'log.error_file': '../supportFiles/logs/logError_file.txt','log.screen': True})

class Widget1(server.App):
    title = 'Widget 1'


    inputs = [{"type": "text",
        "key": "text1",
        "label": "<font size=4pt>In this widget we're just going to create a file with the sequences of the OTUs that will be required for the rest of the analysis.</font> <br> <br>Do you want to just run the widget with the default example files?",
        "value": "Yes or No"},

        {"type": "text",
         "key": "text2",
         "label": "<br><font size=3pt>If you want to run Widget 1 on you own files, tell me which file has the information about associated OTUs</font>",
         "value": "Enter the path to your file"},

        {"type": "text",
         "key": "text3",
         "label": "<font size=3pt>Tell me which file has the sequences of the representative OTUs</font>",
         "value": "Enter the path to your file"},

        {"type": "text",
         "key": "text4",
         "label": "<font size=3pt>Tell me which folder you would like to put the results from your analysis in</font>",
         "value": "Enter the path to your results folder"},

        {"type": "text",
         "key": "text5",
         "label": "<font size=3pt>Tell me what do you want the results file to be called</font>",
         "value": "Enter the name of your file"}

    ]




    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]

    controls = [{"type":"button",
                 "label":"Run Widget 1",
                 "id":"run_widget"}]

    tabs = ["Results"]

    
    
    def getCustomCSS(self):
        with open(resource_filename(__name__, 'static/custom_styleMMinte.css')) as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
    



    def getHTML(self,params):

        if params['text1'] == "Yes" or params['text1'] == "yes":
            corrsFile = '../supportFiles/exampleRun/userFiles/corrs.txt'
            sequencesFile = '../supportFiles/exampleRun/userFiles/otus.fasta'
            outFolder = '../supportFiles/exampleRun/userOutput/'
            outFastaFile = 'reprOTUsToUse.fasta'
            outputFasta = outFolder + outFastaFile

        else:
            corrsFile = params['text2']
            sequencesFile = params['text3']
            outFolder = params['text4']
            outFastaFile = params['text5']
            outputFasta = outFolder + outFastaFile

        if not os.path.exists(outFolder):
            os.makedirs(outFolder)


        try:
            get_unique_otu_sequences(corrsFile, sequencesFile, outputFasta)
        except:
            cherrypy.log('We were unable to run get_unique_otu_sequences')
            return "Sorry something's wrong. Make sure the path to your file is correct."
        # try:
        #     corrs = getUniqueOTU(corrsFile)
        #     cherrypy.log("We successfully ran getUniqueOTU.")
        # except:
        #     cherrypy.log("We were unable to run getUniqueOTU.")
        #     return "Sorry something's wrong. Make sure the path to your file is correct."
        #     exit()
        #
        # try:
        #     seqs = getSeqs(sequencesFile)
        #     cherrypy.log("We successfully ran getSeqs.")
        # except:
        #     cherrypy.log("We were unable to run getSeqs.")
        #     return "Sorry something's wrong. Make sure the path to your file is correct."
        #     exit()
        #
        #
        # try:
        #     workingOTUs(corrs,seqs,outputFasta)
        #     cherrypy.log("We successfully ran workingOTUs.")
        # except:
        #     cherrypy.log("We were unable to run workingOTUs.")
        #     return "Sorry something's wrong. Make sure the path to your file is correct."
        #     exit()

        
        head = ["<strong><font color=#00961E size=4pt>Here are the OTU's that will be used in the rest of the analysis:</strong></font>"]
        head.append('<br>')
        head.append("<strong><font color=#00961E size=2pt>You can find the full sequences in the userOutput folder.</strong></font>")
        head.append('<br>')
        
        myfile = open(outputFasta)

        for i in myfile:
            if i.startswith('>'):
                head.append('<br>')
                head.append(i)
                
       
        return head


        
if __name__ == '__main__':
    app = Widget1()
    app.launch()
