from spyre import server
from widget3 import getModels
import os
from os import listdir
from os.path import isfile, join

import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt', 'log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

class Widget3(server.App):
    title = 'Widget 3 '
    
    inputs = [
        {"type": "text",
         "label": '<font size=4pt>In this widget we are going to use the list of genome IDs for our bacterial species of interest to reconstruct, gap fill and fetch individual species metabolic models from <a href="http://modelseed.theseed.org/">ModelSEED</a>. We will need these models to predict the growth of our species of interest under different nutritional conditions.  </font> <br> <br> Please note that <a href="http://modelseed.theseed.org/">ModelSEED</a> is undergoing active development. If you are having issues, click here to contact the <a href="mailto:chia.nicholas@mayo.edu">ModelSEED</a> or <a href="mailto:microbialmetabolicinteractions@gmail.com">MMinte</a> developers! <br> <br>Do you want to just run the widget with the default example files?',
        "key": 'text11',
        "value": "Yes or No"},

        {"type":"text",
        "key":"text12",
        "label" : '<font size=3pt>Tell me which file has the list of IDs for the Genomes for which you want to fetch metabolic models.</font>',
        "value":"Enter the path to your file with the list of genomeIDs"},


        {"type": "text",
         "key": 'text13',
         "label": "<font size=3pt>Tell me which folder you would like to put the metabolic models in</font>",
         "value": "Enter the path to your models folder"}
    ]
    
    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]
    
    controls = [{"type":"button",
                 "label":"Run Widget 3",
                 "id":"run_widget"}]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        ROOT_DIR = os.path.dirname(os.path.realpath('static/custom_styleMMinte.css'))
        with open(ROOT_DIR + '/custom_styleMMinte.css') as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
        
        
    def getHTML(self,params):

        if params['text11'] == 'Yes' or params['text11'] == "yes":
            listIDs = '../supportFiles/exampleRun/userOutput/ids4MS.txt'
            modelFolder = '../supportFiles/exampleRun/userOutput/models/'


        else:
            listIDs = params['text12']
            modelFolder = params['text13']

        #fixme It's running if default is not yes and looking for a folder?

        if not os.path.exists(modelFolder):
            os.makedirs(modelFolder)


        listOfModels = open(listIDs,'r')
        mypath = modelFolder
        
        existingModels = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        
         
        for i in listOfModels:
            cherrypy.log("Will now see if %s is in the folder already" %i)
            i = i.rstrip()
            if (i + '.sbml') not in existingModels:
                cherrypy.log("The model %s isn't in the folder, so we're going to fetch it from ModelSeed" %i)
                try:
                    cherrypy.log("Started getting model for genome %s" %i)
                    getModels(i,modelFolder)
                    cherrypy.log("We finished getting the metabolic model for genome %s from ModelSEED." %i)
                except:
                    #cherrypy.log("We were either unable to run getModels or were unable to get the metabolic models we wanted from ModelSEED. We'll keep going for now and try the next model.")
                    #return "Sorry something's wrong. Make sure the path to your file is correct."
                    pass
                continue
            else:
                cherrypy.log("The model %s was already in the folder" %i)
                continue
        
        ids = []
        idsFile = open(listIDs,'r')
        
        #check if all models in the list are in the model folder.
        for i in idsFile:
            ids.append(i)
            
        numIDs = len(ids)
        
        numModels = sum(os.path.isfile(os.path.join(mypath, f)) for f in os.listdir(mypath))
        
        return "You have %d genome IDs on the IDs file and %d models in the models folder. If you are still missing models, go ahead and run this widget again." %(numIDs,numModels)
    
if __name__ == '__main__':
    app = Widget3()
    app.launch()
